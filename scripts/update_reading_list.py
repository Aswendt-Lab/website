#!/usr/bin/env python3
"""Import linked manuscripts from Telegram into the website data."""
import argparse
import datetime as dt
import html
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
URL_PATTERN = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:\w]+", re.IGNORECASE)
TRAILING_URL_PUNCTUATION = ".,;:!?)]}'\""
PAGE_SIZE = 100
PUBMED_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def request_json(url, params):
    target = url + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(target, headers={"User-Agent": "AswendtLabWebsite/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise RuntimeError("Telegram API request failed; existing reading-list data retained") from None
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise RuntimeError("Telegram API returned an unsuccessful response")
    return payload


def request_pubmed_json(endpoint, params):
    target = f"{PUBMED_EUTILS}/{endpoint}?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        target,
        headers={"User-Agent": "AswendtLabWebsite/1.0 (PubMed reading-list citations)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise RuntimeError("PubMed API request failed; existing reading-list data retained") from None
    return payload


def request_pubmed_xml(params):
    target = f"{PUBMED_EUTILS}/efetch.fcgi?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        target,
        headers={"User-Agent": "AswendtLabWebsite/1.0 (PubMed reading-list citations)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            return ET.fromstring(response.read())
    except (urllib.error.URLError, TimeoutError, ET.ParseError):
        raise RuntimeError("PubMed record request failed; existing reading-list data retained") from None


def identify_bot(token, get_json=request_json):
    payload = get_json(f"https://api.telegram.org/bot{token}/getMe", {})
    bot = payload.get("result")
    if not isinstance(bot, dict) or not isinstance(bot.get("username"), str) or not isinstance(bot.get("id"), int):
        raise ValueError("Telegram getMe response is missing bot identity")
    return bot


def fetch_updates(token, offset, get_json=request_json):
    """Fetch one batch; avoid acknowledging a batch before its state is saved."""
    payload = get_json(
        f"https://api.telegram.org/bot{token}/getUpdates",
        {
            "offset": offset,
            "limit": PAGE_SIZE,
            "timeout": 0,
            "allowed_updates": json.dumps(["channel_post", "message"]),
        },
    )
    updates = payload.get("result")
    if not isinstance(updates, list):
        raise ValueError("Telegram response is missing its update list")
    next_offset = offset
    for update in updates:
        if not isinstance(update, dict) or not isinstance(update.get("update_id"), int):
            raise ValueError("Telegram response contains an invalid update")
        next_offset = max(next_offset, update["update_id"] + 1)
    return updates, next_offset


def _safe_url(value):
    value = value.rstrip(TRAILING_URL_PUNCTUATION)
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
        return ""
    return value


def manuscript_links(message, text):
    entities = message.get("entities") or message.get("caption_entities") or []
    candidates = [entity.get("url", "") for entity in entities if isinstance(entity, dict)]
    candidates.extend(URL_PATTERN.findall(text))
    candidates.extend(
        "https://doi.org/" + doi.rstrip(TRAILING_URL_PUNCTUATION)
        for doi in DOI_PATTERN.findall(text)
    )

    links = []
    seen = set()
    for candidate in candidates:
        url = _safe_url(candidate)
        if not url:
            continue
        doi_match = DOI_PATTERN.search(urllib.parse.unquote(urllib.parse.urlsplit(url).path))
        if doi_match:
            doi = doi_match.group(0).rstrip(TRAILING_URL_PUNCTUATION).lower()
            url = "https://doi.org/" + doi
            label = "DOI"
        else:
            label = "Full text" if not any(link["label"] == "Full text" for link in links) else "Link"
        if url not in seen:
            links.append({"label": label, "url": url})
            seen.add(url)
    return links


def parse_channel_post(message):
    text = message.get("text") or message.get("caption") or ""
    links = manuscript_links(message, text)
    if not links:
        return None

    title = URL_PATTERN.sub("", text)
    title = DOI_PATTERN.sub("", title)
    title = re.sub(r"\bdoi\s*:\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title).strip(" \t\r\n-–—:;|")
    if not title:
        title = "Untitled manuscript"

    doi = ""
    for link in links:
        if link["label"] == "DOI":
            doi_match = DOI_PATTERN.search(link["url"])
            if doi_match:
                doi = doi_match.group(0).lower()
                break
    primary_url = next((link["url"] for link in links if link["label"] == "Full text"), links[0]["url"])
    timestamp = message.get("date")
    if isinstance(timestamp, int):
        posted = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc)
    elif isinstance(timestamp, str):
        try:
            posted = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Telegram channel post has an invalid timestamp") from None
        if posted.tzinfo is None:
            raise ValueError("Telegram channel post timestamp must include a timezone")
        posted = posted.astimezone(dt.timezone.utc)
    else:
        raise ValueError("Telegram channel post is missing its timestamp")
    posted_at = posted.isoformat(timespec="seconds").replace("+00:00", "Z")
    key = "doi:" + doi if doi else "url:" + primary_url
    return {
        "key": key,
        "title": title,
        "links": links,
        "posted_at": posted_at,
        "message_id": message.get("message_id"),
    }


def merge_items(data, incoming):
    known_keys = set()
    for existing in data["items"]:
        if not isinstance(existing, dict):
            raise ValueError("Reading-list data contains an invalid entry")
        key = existing.get("key")
        if key is not None and not isinstance(key, str):
            raise ValueError("Reading-list data contains an invalid entry key")
        if key:
            known_keys.add(key)

    added = []
    for item in incoming:
        key = item.get("key")
        if not isinstance(key, str):
            raise ValueError("Imported reading-list entry has an invalid key")
        if key not in known_keys:
            added.append(item)
            known_keys.add(key)
    if added:
        data["items"].extend(added)
        data["items"].sort(key=lambda entry: (entry["posted_at"], entry.get("message_id") or 0), reverse=True)
        data["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return data, len(added)


def _flatten_export_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(
            part if isinstance(part, str) else part.get("text", "")
            for part in value
            if isinstance(part, str) or isinstance(part, dict) and isinstance(part.get("text"), str)
        )
    return ""


def import_history_export(path, data):
    """Merge a Telegram Desktop channel export (messages.json) into the list."""
    try:
        export = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise ValueError("Could not read the Telegram Desktop JSON export") from None
    messages = export.get("messages") if isinstance(export, dict) else None
    if not isinstance(messages, list):
        raise ValueError("Telegram export must be a messages.json file with a messages array")

    incoming = []
    for message in messages:
        if not isinstance(message, dict) or message.get("type") != "message":
            continue
        message_id = message.get("id")
        if not isinstance(message_id, int):
            raise ValueError("Telegram export contains a message without a numeric ID")
        entities = message.get("text_entities") or []
        if not isinstance(entities, list):
            raise ValueError("Telegram export contains invalid text entities")
        normalized = {
            "message_id": message_id,
            "date": message.get("date"),
            "text": _flatten_export_text(message.get("text")),
            "entities": [
                {"url": entity.get("href") or entity.get("url", "")}
                for entity in entities
                if isinstance(entity, dict)
            ],
        }
        item = parse_channel_post(normalized)
        if item:
            incoming.append(item)
    return merge_items(data, incoming)


def process_updates(updates, state, data):
    channel_id = state.get("channel_id")
    incoming = []

    for update in updates:
        message = update.get("channel_post") or update.get("message")
        if not isinstance(message, dict):
            continue
        chat = message.get("chat")
        if (
            not isinstance(chat, dict)
            or not isinstance(chat.get("id"), int)
            or chat.get("type") not in {"channel", "group", "supergroup"}
        ):
            continue
        message_channel_id = chat["id"]
        if channel_id is None:
            channel_id = message_channel_id
        if message_channel_id != channel_id:
            continue
        item = parse_channel_post(message)
        if item:
            incoming.append(item)
    data, added = merge_items(data, incoming)
    return {"channel_id": channel_id}, data, added


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_reading_list(data):
    rows = []
    for item in data["items"]:
        posted = dt.datetime.fromisoformat(item["posted_at"].replace("Z", "+00:00"))
        citation = html.escape(item.get("citation") or item["title"])
        if item.get("pubmed_url"):
            citation = (
                f'<a href="{html.escape(item["pubmed_url"], quote=True)}" '
                f'target="_blank" rel="noopener noreferrer">{citation}</a>'
            )
        links = " · ".join(
            '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'.format(
                html.escape(link["url"], quote=True),
                html.escape(link["label"]),
            )
            for link in item["links"]
        )
        rows.append(
            "  <tr>\n"
            f"    <td>{citation}</td>\n"
            f'    <td><time datetime="{html.escape(item["posted_at"], quote=True)}">{posted:%d %b %Y}</time></td>\n'
            f"    <td>{links}</td>\n"
            "  </tr>"
        )
    return "\n".join(rows) if rows else '  <tr><td colspan="3">The reading list is empty for now.</td></tr>'


def _doi_candidates(item):
    values = [item.get("key", "")]
    values.extend(link.get("url", "") for link in item.get("links", []))
    candidates = []
    for value in values:
        for doi in DOI_PATTERN.findall(urllib.parse.unquote(value)):
            doi = doi.rstrip(TRAILING_URL_PUNCTUATION)
            doi = re.sub(r"(?i)/(?:full|abstract|pdf)$", "", doi)
            doi = re.sub(r"(?i)\.full(?:\.pdf)?$", "", doi)
            doi = re.sub(r"(?i)\.pdf$", "", doi)
            if doi.lower() not in {candidate.lower() for candidate in candidates}:
                candidates.append(doi)
    return candidates


def _pubmed_record(article):
    def text(node):
        return "".join(node.itertext()).strip() if node is not None else ""

    pmid = text(article.find("./MedlineCitation/PMID"))
    pubmed_article = article.find("./MedlineCitation/Article")
    journal_issue = pubmed_article.find("./Journal/JournalIssue")
    pub_date = journal_issue.find("./PubDate")
    authors = []
    author_list = pubmed_article.find("./AuthorList")
    if author_list is not None:
        for author in author_list.findall("./Author"):
            collective_name = text(author.find("./CollectiveName"))
            last_name = text(author.find("./LastName"))
            initials = text(author.find("./Initials"))
            if collective_name:
                authors.append(collective_name)
            elif last_name:
                authors.append(f"{last_name} {initials}".strip())

    dois = []
    article_ids = article.find("./PubmedData/ArticleIdList")
    if article_ids is not None:
        dois = [
            identifier.text.lower().removeprefix("https://doi.org/")
            for identifier in article_ids.findall("./ArticleId")
            if identifier.attrib.get("IdType") == "doi" and identifier.text
        ]
    return {
        "pmid": pmid,
        "doi": dois[0] if dois else "",
        "dois": dois,
        "title": text(pubmed_article.find("./ArticleTitle")),
        "journal": text(pubmed_article.find("./Journal/ISOAbbreviation"))
        or text(pubmed_article.find("./Journal/Title")),
        "year": text(pub_date.find("./Year")) or text(pub_date.find("./MedlineDate"))[:4],
        "volume": text(journal_issue.find("./Volume")),
        "issue": text(journal_issue.find("./Issue")),
        "pages": text(pubmed_article.find("./Pagination/MedlinePgn")),
        "authors": authors,
        "publication_types": [
            text(publication_type)
            for publication_type in pubmed_article.findall("./PublicationTypeList/PublicationType")
        ],
        "publication_status": text(article.find("./PubmedData/PublicationStatus")),
    }


def _format_pubmed_citation(record):
    authors = record["authors"]
    author_text = ", ".join(authors[:6])
    if len(authors) > 6:
        author_text += ", et al"
    title = record["title"].strip()
    if title and title[-1] not in ".?!":
        title += "."
    citation = " ".join(
        part
        for part in (
            author_text + "." if author_text else "",
            title,
            record["journal"] + "." if record["journal"] else "",
        )
        if part
    )
    if record["year"]:
        citation += " " + record["year"]
        if record["volume"]:
            citation += ";" + record["volume"]
            if record["issue"]:
                citation += "(" + record["issue"] + ")"
            if record["pages"]:
                citation += ":" + record["pages"]
        citation += "."
    if record["publication_status"] == "aheadofprint":
        citation += " [Epub ahead of print]."
    if record["doi"]:
        citation += " doi:" + record["doi"] + "."
    return citation


def _is_pubmed_publication(record):
    publication_types = set(record["publication_types"])
    return (
        "Preprint" not in publication_types
        and not publication_types.intersection({"Editorial", "Comment", "Letter", "News"})
        and bool(publication_types.intersection({"Journal Article", "Review", "Systematic Review"}))
        and bool(record["pmid"])
    )


def enrich_unverified_items(data):
    pending = [item for item in data["items"] if not item.get("citation")]
    if not pending:
        return data, 0, 0

    doi_to_items = {}
    pmid_to_items = {}
    for item in pending:
        for doi in _doi_candidates(item):
            doi_to_items.setdefault(doi.lower(), []).append(item)
        for link in item.get("links", []):
            match = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", link.get("url", ""))
            if match:
                pmid_to_items.setdefault(match.group(1), []).append(item)

    pmids = set(pmid_to_items)
    doi_values = list(doi_to_items)
    for start in range(0, len(doi_values), 15):
        batch = doi_values[start : start + 15]
        result = request_pubmed_json(
            "esearch.fcgi",
            {
                "db": "pubmed",
                "term": " OR ".join(f'"{doi}"[doi]' for doi in batch),
                "retmode": "json",
                "retmax": 100,
            },
        ).get("esearchresult", {})
        ids = result.get("idlist")
        if not isinstance(ids, list):
            raise ValueError("PubMed response is missing its record list")
        pmids.update(ids)

    records = {}
    pmid_values = sorted(pmids, key=int)
    for start in range(0, len(pmid_values), 100):
        root = request_pubmed_xml(
            {
                "db": "pubmed",
                "id": ",".join(pmid_values[start : start + 100]),
                "retmode": "xml",
            }
        )
        for article in root.findall(".//PubmedArticle"):
            record = _pubmed_record(article)
            records[record["pmid"]] = record

    records_by_doi = {
        doi.lower(): record
        for record in records.values()
        for doi in record["dois"]
    }
    known_publication_ids = {
        item["pmid"] for item in data["items"] if item.get("pmid")
    }
    accepted = []
    rejected = 0
    for item in pending:
        record = next(
            (records_by_doi.get(doi.lower()) for doi in _doi_candidates(item) if records_by_doi.get(doi.lower())),
            None,
        )
        if record is None:
            for link in item.get("links", []):
                match = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", link.get("url", ""))
                if match:
                    record = records.get(match.group(1))
                    if record:
                        break
        if not record or not _is_pubmed_publication(record) or record["pmid"] in known_publication_ids:
            rejected += 1
            continue

        item.update(
            {
                "key": "doi:" + record["doi"].lower() if record["doi"] else "pmid:" + record["pmid"],
                "title": record["title"].rstrip("."),
                "citation": _format_pubmed_citation(record),
                "pmid": record["pmid"],
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{record['pmid']}/",
                "links": (
                    [{"label": "DOI", "url": "https://doi.org/" + record["doi"]}]
                    if record["doi"]
                    else [{"label": "PubMed", "url": f"https://pubmed.ncbi.nlm.nih.gov/{record['pmid']}/"}]
                ),
            }
        )
        known_publication_ids.add(record["pmid"])
        accepted.append(item)

    data["items"] = [item for item in data["items"] if item.get("citation")] + accepted
    data["items"].sort(
        key=lambda item: (item["posted_at"], item.get("message_id") or 0),
        reverse=True,
    )
    return data, len(accepted), rejected


def update_reading_list_page(path, data):
    content = path.read_text(encoding="utf-8")
    start_marker = "  <!-- reading-list-entries-start -->"
    end_marker = "  <!-- reading-list-entries-end -->"
    if content.count(start_marker) != 1 or content.count(end_marker) != 1:
        raise ValueError("Reading-list page is missing its generated-entry markers")
    start = content.index(start_marker) + len(start_marker)
    end = content.index(end_marker)
    if end < start:
        raise ValueError("Reading-list page has invalid generated-entry markers")
    content = content[:start] + "\n" + render_reading_list(data) + "\n" + content[end:]
    path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--history-export",
        type=Path,
        help="Import a Telegram Desktop messages.json export without contacting the Bot API",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    state_path = root / "_data/reading_list_state.json"
    data_path = root / "_data/reading_list.json"
    data = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else {"items": [], "updated_at": ""}
    if not isinstance(data.get("items"), list):
        raise ValueError("Reading-list data has an invalid format")

    state = None
    channel_post_count = 0
    skipped_publications = 0
    if args.history_export:
        data, _ = import_history_export(args.history_export, data)
        update_count = 0
    else:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            raise RuntimeError("Set TELEGRAM_BOT_TOKEN or provide --history-export")
        bot = identify_bot(token)
        print(f"Connected Telegram bot: @{bot['username']} (ID {bot['id']}).")
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"offset": 0, "channel_id": None}
        if not isinstance(state.get("offset"), int):
            raise ValueError("Telegram update state has an invalid format")
        updates, next_offset = fetch_updates(token, state["offset"])
        state, data, _ = process_updates(updates, state, data)
        state["offset"] = next_offset
        update_count = len(updates)
        channel_post_count = sum(
            isinstance(update.get("channel_post"), dict)
            or isinstance(update.get("message"), dict)
            and update["message"].get("chat", {}).get("type") in {"group", "supergroup"}
            for update in updates
        )

    data, verified_added, skipped_publications = enrich_unverified_items(data)
    with tempfile.TemporaryDirectory(prefix="lab-reading-list-") as temporary:
        staged_data = Path(temporary) / "reading_list.json"
        _write_json(staged_data, data)
        staged_page = Path(temporary) / "reading-list.md"
        shutil.copyfile(root / "reading-list.md", staged_page)
        update_reading_list_page(staged_page, data)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        staged_files = [(staged_data, data_path), (staged_page, root / "reading-list.md")]
        if state is not None:
            staged_state = Path(temporary) / "reading_list_state.json"
            _write_json(staged_state, state)
            staged_files.append((staged_state, state_path))
        for source, destination in staged_files:
            pending = destination.with_suffix(destination.suffix + ".pending")
            shutil.copyfile(source, pending)
            pending.replace(destination)
    if state is None:
        print(
            f"Imported {verified_added} PubMed-indexed publication(s) from the history export; "
            f"skipped {skipped_publications} unverified or non-publication item(s)."
        )
    else:
        print(
            f"Telegram returned {update_count} update(s), including {channel_post_count} "
            f"channel/group post(s); imported {verified_added} PubMed-indexed publication(s) "
            f"and skipped {skipped_publications} unverified or non-publication item(s)."
        )


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
