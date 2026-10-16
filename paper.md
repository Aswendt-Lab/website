---
title: Publications
layout: page
---
{% assign bibliography = site.data.publications %}
{% if bibliography %}
<p>Publications by {{ bibliography.author.name | escape }} and collaborators, retrieved from OpenAlex. Preprints and conference presentations are excluded from this list and its totals. Refreshed weekly; last successful update: <time datetime="{{ bibliography.updated_at | escape }}">{{ bibliography.updated_at | date: "%d %B %Y" }}</time>.</p>
<div class="publication-stats" aria-label="Publication summary">
  <p><strong>{{ bibliography.publication_count }}</strong><span>Publications</span></p>
  <p><strong>{{ bibliography.citation_count }}</strong><span>Citation links in OpenAlex</span></p>
</div>
<div class="actions"><a class="button" href="{{ bibliography.report_url | relative_url }}">Download citation report (PDF)</a><a class="button secondary" href="{{ bibliography.csv_url | relative_url }}">Download all records (CSV)</a></div>
<p class="publication-note">Counts cover the publications listed below and can change as OpenAlex updates its index. The CSV retains all {{ bibliography.total_record_count }} records, including preprints and conference contributions. The detailed PDF contains {{ bibliography.report_citation_count }} retrieved citation links across all record types; its scope is broader than the filtered totals shown here. A paper citing two listed works contributes two citation links. SCImago journal metrics in the PDF are citations per document (2 years), not Clarivate Journal Impact Factors.</p>
{% if bibliography.annual_citations.size > 0 %}
<details class="citation-history"><summary>Citation history</summary>
<p class="publication-note">Annual citation links for the years available in the current OpenAlex records. This recent-year window is not a complete lifetime history.</p>
<ul class="citation-bars" aria-label="Annual citation links">
{% for point in bibliography.annual_citations %}<li><span>{{ point.year }}</span><span class="citation-track" aria-hidden="true"><span style="width: {{ point.width }}%"></span></span><strong>{{ point.count }}</strong></li>{% endfor %}
</ul></details>
{% endif %}
<form class="publication-filters" role="search" onsubmit="return false" hidden>
  <div><label for="publication-search">Search publications</label><input id="publication-search" type="search" placeholder="Title, author, journal, or DOI" autocomplete="off"></div>
  <div><label for="publication-year">Year</label><select id="publication-year"><option value="">All years</option>{% assign years = bibliography.publications | group_by: 'year' %}{% for year in years %}<option value="{{ year.name }}">{{ year.name }}</option>{% endfor %}</select></div>
  <div><label for="publication-type">Type</label><select id="publication-type"><option value="">All types</option><option value="article">Articles</option><option value="review">Reviews</option><option value="data-paper">Data papers</option><option value="book-chapter">Book chapters</option><option value="book">Books</option></select></div>
</form>
<p id="publication-results" role="status" aria-live="polite" hidden></p>
<div id="publication-list">
{% assign groups = bibliography.publications | group_by: 'year' %}
{% for group in groups %}
<section class="publication-year" aria-labelledby="year-{{ group.name }}"><h2 id="year-{{ group.name }}">{{ group.name }}</h2>
<ul class="publication-entries">
{% for publication in group.items %}
<li class="publication-entry" data-year="{{ publication.year }}" data-type="{{ publication.type | escape }}">
  <h3><a href="{{ publication.url | escape }}">{{ publication.title | escape }}</a></h3>
  <p>{{ publication.authors | escape }}</p>
  <p class="publication-citation"><em>{{ publication.journal | default: 'Source not specified' | escape }}</em> · {{ publication.year }}{% if publication.volume != '' %}; {{ publication.volume | escape }}{% endif %}{% if publication.issue != '' %}({{ publication.issue | escape }}){% endif %}{% if publication.pages != '' %}: {{ publication.pages | escape }}{% endif %}</p>
  <p class="publication-labels"><span>{{ publication.type | capitalize | escape }}</span><a href="{{ publication.openalex_id | escape }}">{{ publication.cited_by_count }} citations in OpenAlex</a>{% if publication.doi != '' %}<span>DOI: {{ publication.doi | escape }}</span>{% endif %}</p>
</li>
{% endfor %}
</ul></section>
{% endfor %}
</div>
<script src="{{ '/assets/publications.js' | relative_url }}" defer></script>
{% else %}
{% capture fallback %}{% include publications-fallback.md %}{% endcapture %}
{{ fallback | markdownify }}
{% endif %}
