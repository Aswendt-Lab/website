---
title: Neuroimaging and Neuroengineering of Experimental Stroke
layout: landing
description: Discover how the Aswendt Lab studies stroke recovery through MRI, circuit mapping, neuromodulation, and open imaging tools.
---
<section class="hero" aria-labelledby="hero-title">
  <div>
    <p class="eyebrow">Aswendt Lab · Frankfurt</p>
    <h1 id="hero-title">Understanding stroke.<br>Advancing recovery.</h1>
    <p>We study how brain circuits change after experimental stroke and how neuromodulation can support recovery. Our work combines MRI, viral tracing, light sheet microscopy, and open analysis tools.</p>
    <div class="actions">
      <a class="button" href="{{ '/projects.html' | relative_url }}">Explore research</a>
      <a class="button secondary" href="{{ '/software.html' | relative_url }}">Use our tools</a>
      <a class="button secondary" href="{{ '/opportunities.html' | relative_url }}">Join the lab</a>
    </div>
  </div>
  <img src="{{ '/img/CoverDecodeStroke.png' | relative_url }}" alt="Scientific illustration introducing the lab’s stroke recovery research" fetchpriority="high">
</section>

## How we study recovery

<div class="card-grid">
  <article class="card"><h3>Brain networks</h3><p>We use MRI and circuit mapping to understand how structural and functional connections change after stroke.</p><a href="{{ '/projects.html#spontaneous-recovery-after-stroke' | relative_url }}">Explore recovery research →</a></article>
  <article class="card"><h3>Neuromodulation</h3><p>We investigate motor deficits and stimulation approaches that support plasticity and functional recovery.</p><a href="{{ '/projects.html#internal-capsule-stroke-and-spasticity-after-stroke-in-mice' | relative_url }}">Explore neuromodulation →</a></article>
  <article class="card"><h3>Open science</h3><p>We build accessible imaging tools and FAIR workflows to make preclinical research more reproducible.</p><a href="{{ '/software.html' | relative_url }}">Discover software &amp; data →</a></article>
</div>

{% assign featured = site.data.publications.publications | where: 'doi', '10.4103/nrr.nrr-d-25-00491' | first %}
<section class="publication-feature" aria-labelledby="publication-title">
  <img src="{{ '/img/Mahani2026_SC_GraphicalAbstract.png' | relative_url }}" alt="Graphical abstract accompanying the study of structural connectivity changes after stroke in mice" loading="lazy" decoding="async">
  <div>
    <p class="eyebrow">Featured publication · {{ featured.year | default: 2026 }}</p>
    <h2 id="publication-title">Mapping connectivity after stroke</h2>
    <p>How do structural brain networks change after stroke? Our longitudinal study examines connectivity changes in mice with cortical and cortico-striatal strokes.</p>
    <p class="publication-citation">{% if featured %}{{ featured.authors | split: "," | first | escape }} et al. · <em>{{ featured.journal | escape }}</em> · {{ featured.cited_by_count }} citations in OpenAlex{% else %}Mahani et al. · <em>Neural Regeneration Research</em>{% endif %}</p>
    <div class="actions"><a class="button" href="https://doi.org/10.4103/nrr.nrr-d-25-00491">Read the paper</a><a class="button secondary" href="{{ '/paper.html' | relative_url }}">All publications</a></div>
  </div>
</section>

{% include latest-publications.html %}

<div class="section-heading"><h2>Latest news</h2><a href="{{ '/news.html' | relative_url }}">All news →</a></div>
<div class="card-grid">
  <article class="card"><p class="eyebrow"><time datetime="2026-05">May 2026</time></p><h3>Connecting across Rhine-Main</h3><p>The team joined the RMN² Retreat for scientific exchange with the regional neuroscience community.</p><a href="{{ '/news.html#052026-rmn2-biennial-meeting-oberwesel' | relative_url }}">Read the retreat update →</a></article>
  <article class="card"><p class="eyebrow"><time datetime="2026-04">April 2026</time></p><h3>CoBIC opens its doors</h3><p>We celebrated the CoBIC Scientific Opening Symposium with presentations and discussions across brain research.</p><a href="{{ '/news.html#042026-cobic-scientific-opening-symposium' | relative_url }}">Read about the symposium →</a></article>
  <article class="card"><p class="eyebrow"><time datetime="2026-03">March 2026</time></p><h3>Motor control in focus</h3><p>Julian, Motahare, and Markus shared project updates at the sixth CRC 1451 Annual Retreat.</p><a href="{{ '/news.html#032026-6th-crc-1451-annual-retreat' | relative_url }}">Read the CRC 1451 update →</a></article>
</div>

<section class="join-banner" aria-labelledby="join-title">
  <div><p class="eyebrow">Join the lab</p><h2 id="join-title">Bring your curiosity to brain research.</h2><p>Explore Bachelor and Master projects in neuroscience, bioengineering, and MR physics.</p></div>
  <a class="button" href="{{ '/opportunities.html' | relative_url }}">Explore student projects</a>
</section>

## Supported by

<div class="logo-grid" aria-label="Research funders and supporting initiatives">
  <img src="{{ '/img/dfg_logo_schriftzug_blau.jpg' | relative_url }}" alt="German Research Foundation" loading="lazy">
  <img src="{{ '/img/CRC1451_Logo.png' | relative_url }}" alt="CRC 1451" loading="lazy">
  <img src="{{ '/img/FriebeLogo.png' | relative_url }}" alt="Friebe Foundation" loading="lazy">
  <img src="{{ '/img/logo_nfdi4.jpg' | relative_url }}" alt="NFDI4Health" loading="lazy">
  <img src="{{ '/img/COMULISglobe.png' | relative_url }}" alt="COMULISglobe" loading="lazy">
  <img src="{{ '/img/Chan_Zuckerberg_Initiative_Logo.svg' | relative_url }}" alt="Chan Zuckerberg Initiative" loading="lazy">
</div>

## Collaboration partners

Our collaborators bring together expertise in neuroimaging, neuroscience, and reproducible research.

<ul class="partner-grid" aria-label="Research collaborators">
  {% for partner in site.data.partners %}
  <li class="partner">
    <img src="{{ partner.image | relative_url }}" alt="{{ partner.institution | escape }}" loading="lazy" decoding="async" width="64" height="64">
    <div><h3>{{ partner.names | escape }}</h3><p>{{ partner.institution | escape }}<br><span>{{ partner.details | escape }}</span></p></div>
  </li>
  {% endfor %}
</ul>
