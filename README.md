# Aswendt Lab website

Jekyll website for the Aswendt Lab’s research on experimental stroke, neuroimaging, and neuromodulation.

**Live website:** https://aswendtlab.com/

## Local development

Use a modern Ruby installation compatible with Bundler 2.5.10 (Ruby 3.1 or newer).

```sh
gem install bundler -v 2.5.10
bundle install
bundle exec jekyll serve
```

Open http://localhost:4000/. To check a production build:

```sh
JEKYLL_ENV=production bundle exec jekyll build
```

The generated site is written to `_site/`, which is ignored by Git. Dependencies are pinned in `Gemfile.lock`; keep this file when updating the site.

## Editing content

- `index.md`: homepage, research introduction, featured publication, and news highlights.
- `_data/partners.yml`: collaborator names, institutions, and logos shown on the homepage.
- `projects.md`: research themes; `software.md`: AIDA tools, data workflows, tutorials, and poster downloads.
- `opportunities.md`: student inquiries and application guidance.
- `paper.md`, `team.md`, `news.md`: publications, team profiles, and news archive.
- `contact.md`, `imprint.md`: contact details and legal notice.
- `assets/main.scss`: shared black theme, responsive layouts, and accessible focus styles.
- `_includes/footer.html`: footer navigation; `_layouts/landing.html`: homepage layout.

Use descriptive image alternative text. Add `loading="lazy"` to images below the first screen. Homepage news highlights and the featured-paper selection are curated manually. The latest-publication cards and Publications page update automatically from the report output.

## Deployment

The site uses GitHub Pages-compatible Jekyll dependencies. `_config.yml` sets `url: https://aswendtlab.com` and `baseurl: ""`. Use Jekyll’s `relative_url` filter for internal links so links resolve correctly at the custom-domain root.

Deployment is managed through the repository’s GitHub Pages settings. Confirm the configured branch or workflow there before publishing; local edits alone do not deploy the site.

## Contributing

[Open an issue](https://github.com/Aswendt-Lab/website/issues) or submit a pull request. Include a description and screenshots for visual changes. Before submitting, build the site and check navigation, mobile layouts, and links.

Explore the lab’s [software repositories](https://github.com/Aswendt-Lab).

## Automatic publications and citation report

The **Update publications** GitHub Actions workflow runs Mondays at 05:23 UTC and can be run manually from the Actions tab. It also runs when its collector/configuration changes on `main`.

It runs a pinned revision of [CitationsReport](https://github.com/Aswendt-Lab/Tools/tree/main/CitationsReport), reads the generated `works_summary_*.csv`, and updates:

- `_data/publications.json`: publication list, citation counts, and annual citation history.
- `data/publications.csv`: downloadable bibliographic data from the report.
- `pdf/citations-latest.pdf`: detailed citation report.

The Publications page and homepage consume the same snapshot. The previous hand-written list remains in `_includes/publications-fallback.md` and is used only until the first complete successful refresh. New uncited papers are included in the list; the detailed PDF includes works with retrievable citing publications.

### One-time GitHub setup

1. Enable GitHub Actions for this repository and permit the workflow to write repository contents. Branch protection must allow its snapshot commits, or the workflow will stop without publishing.
2. Add an `OPENALEX_API_KEY` repository Actions secret for a dedicated OpenAlex API budget. Without it, requests use OpenAlex’s shared unauthenticated IP budget and may fail on shared runners. Never put the key into tracked files.
3. This workflow preserves the existing **Deploy from a branch** GitHub Pages setup (`main`, `/`). After committing a validated snapshot it explicitly requests a Pages rebuild, because commits made with `GITHUB_TOKEN` do not trigger one automatically. If Pages is configured to use a custom Actions deployment instead, adapt the final rebuild step to invoke that deployment.
4. Run **Update publications → Run workflow** and confirm both the update and Pages build succeed.

The author is fixed to OpenAlex `A5088353298` and ORCID `0000-0003-1423-0934` in `scripts/publications-config.json`. The refresh verifies both and never searches by name. The export contains all works returned for that author, including work before the lab was established; this is not an aggregate bibliography of every lab member. `display_types` sets the published-work types displayed on the website. `exclude_ids` and `exclusion_notes` identify known conference abstracts misclassified by OpenAlex; these exclusions affect display only, never the complete CSV export.

The runner uses the original report generator with strict complete pagination, fixed author selection, and OpenAlex-only bibliographic metadata (optional per-citation Crossref enrichment is disabled to avoid thousands of extra requests). It stages output in a temporary directory and stops on incomplete downloads, malformed CSV, mismatched author identity, or a large drop in the existing publication list. A production Jekyll build must pass before the workflow commits anything. Failed runs leave the last published snapshot in place; check failed-run notifications in GitHub Actions.

Citation counts count links to the listed works, not unique citing papers; one citing paper can contribute more than one link. The downloadable CSV retains every fetched record, including preprints and conference contributions; the PDF provides detailed citation reports for cited works across all record types. The website list, homepage cards, publication count, citation count, and annual chart use published journal articles, reviews, data papers, books, and book chapters. Repository-only records, abstracts, presentations, and preprints are excluded from display. Duplicate DOIs, JoVE article/video pairs, and matching-title versions from the same venue and first author are counted once on the website while all source rows remain in the CSV. Annual history reflects the recent-year window supplied by OpenAlex. SCImago 2025 values are explicitly labelled citations per document (2 years), not official Clarivate JIFs; that bundled journal-metrics year does not refresh automatically.

To change the featured publication, edit its DOI in `index.md`. Recent publications below it are selected automatically. Bibliographic corrections should be made upstream in OpenAlex where possible.

### Run locally

Use Python 3.12 in a virtual environment, then:

```sh
pip install -r scripts/requirements-publications.txt
python -m unittest discover -s tests -v
python scripts/update_publications.py
JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter
```

Set `OPENALEX_API_KEY` through your environment or secret manager if needed. A complete report retrieves citing works for every cited publication and can take several minutes. The reporter revision is pinned in `scripts/update_publications.py`; update it deliberately when upgrading the tool.

Validation also checks internal links and anchors with `bundle exec ruby scripts/check_links.rb` and filter behavior with `node --test tests/publications.test.js`. The report adapter corrects PMID values read as floating-point numbers by pandas. The page distinguishes OpenAlex’s indexed citation counts from the report’s actually retrieved citation links.

The adapter embeds DejaVu Sans fonts from Matplotlib and normalizes typographic hyphens so author names and publication titles render correctly in the PDF.

The shared AIDA video and GitHub repository overview are defined in `_includes/tools-feature.html` and shown on both the homepage and Software & Data page. The feature displays `img/AIDA-Tools-Animation.gif` as an automatically looping image, with a pause/resume button. Visitors who prefer reduced motion see `img/AIDA-Tools-Illustration.jpg` instead. The MP4 remains the source asset for future GIF regeneration.

Team profiles are stored in `_data/team.yml`. The Team page renders them as portrait tiles that start in color. On devices with mouse hover, hovering a tile turns all other portraits grayscale; leaving the tile restores their color, including in grid gaps. Touch devices keep all portraits in color. Native details/summary elements support keyboard and touch interaction; `assets/team.js` adds mouse-hover disclosure.

The CSV adds `type`, `source_type`, and `displayed_on_website` columns so the full export can be audited against the filtered publication list. Source/type information and explicit conference exclusions are applied automatically on every refresh.

The custom domain is declared in `CNAME` (`aswendtlab.com`). DNS is managed through Namecheap BasicDNS. HTTPS certificates are provisioned by GitHub Pages; enable Enforce HTTPS in the repository’s Pages settings once certificate issuance completes.
