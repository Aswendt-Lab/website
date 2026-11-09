#!/usr/bin/env python3
"""Run the pinned lab citation reporter and publish a validated website snapshot.

The reporter's works-summary CSV is the source of bibliographic metadata. Raw
OpenAlex records supply types and yearly citation counts. All network calls that
supply publication/citation lists fail closed; files are staged until success.
"""
import argparse
import csv
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_REV = "c9f9fbb8c4f22b28d750467627bde29b44acd915"
UPSTREAM_ROOT = f"https://raw.githubusercontent.com/Aswendt-Lab/Tools/{UPSTREAM_REV}/CitationsReport"
API_ROOT = "https://api.openalex.org"


def request_json(url, params=None):
    query = dict(params or {})
    if url.startswith(API_ROOT + "/") and os.environ.get("OPENALEX_API_KEY"):
        query["api_key"] = os.environ["OPENALEX_API_KEY"]
    target = url + ("?" + urllib.parse.urlencode(query) if query else "")
    # Never log URLs or upstream exception strings: they may contain the API key.
    for attempt in range(5):
        try:
            req = urllib.request.Request(target, headers={"User-Agent": "AswendtLabWebsite/1.0"})
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.load(response)
            if not isinstance(result, dict):
                raise ValueError("API response is not an object")
            return result
        except (urllib.error.URLError, TimeoutError, ValueError):
            if attempt == 4:
                raise RuntimeError("API request failed after retries; existing website data retained") from None
            time.sleep(2 ** attempt)


def fetch_all(filter_value, get_json=request_json):
    """Cursor pagination with count, unique-ID, and early-termination checks."""
    records, seen, cursors = [], set(), set()
    cursor, expected = "*", None
    while cursor:
        if cursor in cursors:
            raise ValueError("Repeated pagination cursor")
        cursors.add(cursor)
        payload = get_json(API_ROOT + "/works", {
            "filter": filter_value, "per-page": 200, "cursor": cursor,
        })
        meta, batch = payload.get("meta"), payload.get("results")
        if not isinstance(meta, dict) or not isinstance(batch, list):
            raise ValueError("Incomplete OpenAlex response")
        count = meta.get("count")
        if not isinstance(count, int) or count < 0:
            raise ValueError("Missing OpenAlex result count")
        if expected is None:
            expected = count
        elif count != expected:
            raise ValueError("Result count changed during pagination; retry next run")
        for work in batch:
            identifier = work.get("id")
            if not identifier or identifier in seen:
                raise ValueError("Missing or repeated OpenAlex work ID")
            seen.add(identifier)
            records.append(work)
        if len(records) == expected:
            return records
        if len(records) > expected or not batch:
            raise ValueError("Truncated or inconsistent OpenAlex results")
        cursor = meta.get("next_cursor")
    raise ValueError("Pagination ended before all works were retrieved")


def verify_author(config, author):
    if author.get("id", "").rsplit("/", 1)[-1] != config["author_id"]:
        raise ValueError("OpenAlex author ID does not match configuration")
    if (author.get("orcid") or "").rstrip("/").rsplit("/", 1)[-1] != config["orcid"]:
        raise ValueError("ORCID does not match configured author; refusing name fallback")


def select_works(works, config):
    """Preserve every fetched record for the report and CSV, including preprints."""
    if not works:
        raise ValueError("No author records returned")
    return list(works)


def is_display_publication(work, config):
    """Exclude preprints, presentations, abstracts, and repository-only records."""
    if work.get("type") not in config.get("display_types", ["article", "review", "data-paper", "book", "book-chapter"]):
        return False
    if work.get("is_retracted") or work.get("is_paratext") or work["id"] in config.get("exclude_ids", []):
        return False
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    if source.get("type") not in {"journal", "book series", "ebook platform", "book"}:
        return False
    if re.search(r"\b(?:biorxiv|medrxiv|arxiv)\b", source.get("display_name", ""), re.I):
        return False
    if (location.get("raw_type") or "").lower() in {"proceedings-article", "proceedings", "posted-content"}:
        return False
    title = work.get("title") or ""
    if re.match(r"^(?:Abstract\b|(?:P|PO|OP|FV)\s+\d+\b)", title, re.I):
        return False
    return True


def display_records(records):
    """Count publisher/repository/video versions once without dropping CSV rows."""
    selected, seen_dois, seen_titles = [], set(), set()
    def preference(record):
        # Publisher metadata generally includes a volume; JoVE's -v DOI is a
        # video version of the same paper, not an additional publication.
        return (bool(record["volume"]), not record["doi"].endswith("-v"), record["cited_by_count"])
    for record in sorted(records, key=preference, reverse=True):
        if not record["display_eligible"]:
            continue
        doi = record["doi"].lower()
        if doi.startswith("10.3791/"):
            doi = doi.removesuffix("-v")
        title = re.sub(r"[\W_]+", "", record["title"].casefold())
        venue = re.sub(r"[\W_]+", "", record["journal"].casefold())
        first_author = record["authors"].split(",")[0].split()[0].casefold()
        title_key = (title, venue, first_author) if len(title) >= 32 else None
        if doi and doi in seen_dois or title_key and title_key in seen_titles:
            continue
        if doi:
            seen_dois.add(doi)
        if title_key:
            seen_titles.add(title_key)
        selected.append(record)
    return sorted(selected, key=lambda p: (p["year"], p["publication_date"], p["title"]), reverse=True)


def build_dataset(rows, works, config, previous=None):
    raw_by_id = {work["id"]: work for work in works}
    if len(rows) != len(raw_by_id):
        raise ValueError("Reporter CSV does not match the retrieved publication list")
    publications, seen, annual = [], set(), {}
    required = {"openalex_id", "title", "authors", "year", "doi", "journal", "cited_by_count"}
    for row in rows:
        if not required.issubset(row):
            raise ValueError("Reporter CSV schema changed")
        identifier = row["openalex_id"]
        if identifier not in raw_by_id or identifier in seen:
            raise ValueError("Reporter CSV contains a missing, duplicate, or unexpected ID")
        seen.add(identifier)
        if not row["title"].strip() or not row["authors"].strip() or not re.fullmatch(r"\d{4}", row["year"]):
            raise ValueError("Publication has incomplete bibliographic metadata")
        work = raw_by_id[identifier]
        count = int(row["cited_by_count"])
        if count < 0 or count != int(work.get("cited_by_count", 0)):
            raise ValueError("Citation count differs between CSV and snapshot")
        doi = row["doi"].strip()
        if doi and (not doi.startswith("10.") or re.search(r"\s", doi)):
            raise ValueError("Invalid DOI in reporter output")
        publication = {key: str(row.get(key, "")).strip() for key in (
            "openalex_id", "title", "authors", "publication_date", "journal", "volume", "issue", "pages", "doi",
        )}
        publication.update({
            "year": int(row["year"]), "cited_by_count": count,
            "url": "https://doi.org/" + doi if doi else identifier,
            "type": work["type"],
            "source_type": ((work.get("primary_location") or {}).get("source") or {}).get("type", ""),
            "display_eligible": is_display_publication(work, config),
        })
        access = work.get("open_access") or {}
        oa_url = access.get("oa_url") or ""
        publication.update({
            "is_open_access": access.get("is_oa") is True,
            "open_access_status": access.get("oa_status") or "unknown",
            "open_access_url": oa_url if isinstance(oa_url, str) and oa_url.startswith("https://") else "",
        })
        # Use explicit source metrics; never describe SCImago's metric as JIF.
        metric = row.get("impact_factor", "").strip()
        if metric:
            publication["scimago_cites_per_doc_2y"] = float(metric)
            publication["scimago_year"] = int(float(row["impact_factor_year"]))
        publications.append(publication)
    all_publications = sorted(publications, key=lambda p: (p["year"], p["publication_date"], p["title"]), reverse=True)
    publications = display_records(all_publications)
    for publication in publications:
        work = raw_by_id[publication["openalex_id"]]
        for point in work.get("counts_by_year", []):
            year, citations = int(point["year"]), int(point["cited_by_count"])
            if citations < 0:
                raise ValueError("Negative annual citation count")
            annual[year] = annual.get(year, 0) + citations
    publications.sort(key=lambda p: (p["year"], p["publication_date"], p["title"]), reverse=True)
    if previous:
        old_ids = {p["openalex_id"] for p in previous.get("all_publications", previous["publications"])}
        if len(old_ids - seen) > max(2, int(len(old_ids) * 0.1)):
            raise ValueError("More than 10% of previous publications disappeared; investigate before replacing")
    maximum = max(annual.values(), default=1) or 1
    return {
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "author": {"name": config["author_name"], "openalex_id": config["author_id"], "orcid": config["orcid"]},
        "source": "OpenAlex via Aswendt-Lab/Tools CitationsReport",
        "reporter_revision": UPSTREAM_REV,
        "publication_count": len(publications),
        "total_record_count": len(all_publications),
        "all_publications": all_publications,
        "citation_count": sum(p["cited_by_count"] for p in publications),
        "annual_citations": [{"year": y, "count": n, "width": round(n / maximum * 100, 1)} for y, n in sorted(annual.items())],
        "publications": publications,
    }


def normalize_pmid(value):
    """Pandas reads PMID columns with blanks as floats; preserve the integer ID."""
    text = str(value or "").strip()
    if re.fullmatch(r"\d+(?:\.0+)?", text):
        return text.split(".")[0]
    numbers = re.findall(r"\d+", text)
    return numbers[-1] if numbers else ""


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "AswendtLabWebsite/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        path.write_bytes(response.read())


def refresh(config, workspace, previous=None):
    print('Fetching and validating the configured OpenAlex author...', flush=True)
    author = request_json(API_ROOT + "/authors/" + config["author_id"])
    verify_author(config, author)
    works = select_works(fetch_all("authorships.author.id:" + config["author_id"]), config)
    print(f'Retrieved {len(works)} eligible publications; generating detailed report...', flush=True)
    source = workspace / "reporter.py"
    download(UPSTREAM_ROOT + "/collect_citations_openalex_ORCIDname.py", source)
    metrics = workspace / "scimago.csv"
    download(UPSTREAM_ROOT + "/scimagojr%202025.csv", metrics)
    spec = importlib.util.spec_from_file_location("citation_reporter", source)
    reporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reporter)
    reporter.OUTDIR = workspace / "output"
    reporter.OUTDIR.mkdir()
    # Harden the reporter for unattended use without modifying the upstream repo.
    reporter.get_json = lambda url, params=None, **kwargs: request_json(url, params)
    reporter.pick_best_author = lambda *args: author
    reporter.fetch_works_for_author = lambda *args: works
    reporter.fetch_citing_works = lambda identifier, **kwargs: fetch_all("cites:" + identifier)
    # The reporter tries to enrich every citing paper from Crossref. Use the
    # OpenAlex metadata already present: avoids thousands of optional requests.
    reporter.crossref_enrich_metadata = lambda meta: meta
    reporter.pmid_text = normalize_pmid
    from citation_geography import plot_citation_geography
    reporter.plot_citations_by_country = lambda frame, title, **kwargs: plot_citation_geography(
        frame, title, reporter.OUTDIR, reporter.safe_filename)
    # Embed Unicode-capable fonts for names, Greek letters, and punctuation.
    # Keep the reporter's existing font-family names and layout settings.
    from matplotlib import get_data_path
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font_dir = Path(get_data_path()) / "fonts/ttf"
    for family, filename in {
        "Helvetica": "DejaVuSans.ttf",
        "Helvetica-Bold": "DejaVuSans-Bold.ttf",
        "Helvetica-Oblique": "DejaVuSans-Oblique.ttf",
        "Helvetica-BoldOblique": "DejaVuSans-BoldOblique.ttf",
    }.items():
        pdfmetrics.registerFont(TTFont(family, str(font_dir / filename)))
    pdfmetrics.registerFontFamily("Helvetica", normal="Helvetica", bold="Helvetica-Bold", italic="Helvetica-Oblique", boldItalic="Helvetica-BoldOblique")
    original_clean_text = reporter.clean_text
    reporter.clean_text = lambda value: re.sub(r"[\u2010-\u2015]", "-", original_clean_text(value))

    generated = {}
    original_create_pdf = reporter.create_pdf_report
    def create_pdf(*args, **kwargs):
        generated["report_citation_count"] = int(args[5])
        generated["pdf"] = Path(original_create_pdf(*args, **kwargs))
        return str(generated["pdf"])
    reporter.create_pdf_report = create_pdf
    original_argv = sys.argv
    try:
        sys.argv = [str(source), "--orcid", config["orcid"], "--scimago_csv", str(metrics)]
        reporter.main()
    finally:
        sys.argv = original_argv
    csv_files = list(reporter.OUTDIR.glob("works_summary_*.csv"))
    if len(csv_files) != 1:
        raise ValueError("Expected exactly one works-summary CSV")
    with csv_files[0].open(encoding="utf-8-sig", newline="") as handle:
        data = build_dataset(list(csv.DictReader(handle)), works, config, previous)
    with csv_files[0].open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames)
        csv_rows = list(reader)
    classifications = {p["openalex_id"]: p for p in data["all_publications"]}
    displayed_ids = {p["openalex_id"] for p in data["publications"]}
    with csv_files[0].open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames + ["type", "source_type", "displayed_on_website", "is_open_access", "open_access_status", "open_access_url"], lineterminator="\n")
        writer.writeheader()
        for row in csv_rows:
            record = classifications[row["openalex_id"]]
            row.update(type=record["type"], source_type=record["source_type"], displayed_on_website=row["openalex_id"] in displayed_ids)
            row.update({key: record[key] for key in ("is_open_access", "open_access_status", "open_access_url")})
            writer.writerow(row)

    pdf = generated.get("pdf")
    if not pdf or not pdf.is_file() or not pdf.read_bytes().startswith(b"%PDF-"):
        raise ValueError("Reporter did not produce a valid PDF")
    data["report_citation_count"] = generated["report_citation_count"]
    data["report_url"] = "/pdf/citations-latest.pdf"
    data["csv_url"] = "/data/publications.csv"
    return data, pdf, csv_files[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    config = json.loads((root / "scripts/publications-config.json").read_text())
    target = root / "_data/publications.json"
    previous = json.loads(target.read_text()) if target.exists() else None
    # Importing the original reporter creates an output directory in cwd.
    # Run in a temporary directory so an unsuccessful run leaves the site intact.
    with tempfile.TemporaryDirectory(prefix="lab-citations-") as temporary:
        original_cwd = Path.cwd()
        try:
            os.chdir(temporary)
            data, pdf, csv_file = refresh(config, Path(temporary), previous)
        finally:
            os.chdir(original_cwd)
        staged = [(pdf, root / "pdf/citations-latest.pdf"), (csv_file, root / "data/publications.csv")]
        data_file = Path(temporary) / "publications.json"
        data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        staged.append((data_file, target))
        # All remote work and validation finished. CI builds before committing;
        # JSON is replaced last so readers never see references to absent assets.
        for source, destination in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            pending = destination.with_suffix(destination.suffix + ".pending")
            shutil.copyfile(source, pending)
            pending.replace(destination)
    print(f"Updated {data['publication_count']} publications and {data['citation_count']} citation links.")


if __name__ == "__main__":
    main()
