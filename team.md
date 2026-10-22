---
title: Team
layout: page
---

<figure class="team-group"><img src="{{ '/img/team_2026-rund_V2.png' | relative_url }}" alt="Aswendt Lab team, 2026" width="1120" loading="eager"></figure>

## Meet the team

<div class="team-grid">
{% for member in site.data.team %}
  <article class="team-tile">
    <img src="{{ member.image | relative_url }}" alt="Portrait of {{ member.name | escape }}" loading="lazy" decoding="async" width="400" height="500">
    <span class="team-name">{{ member.name | escape }}</span>
    <details class="team-details">
      <summary class="team-info" aria-label="Details for {{ member.name | escape }}">Info</summary>
      <div class="team-panel">
        <div class="team-biography"><h3>{{ member.name | escape }}</h3><p>{{ member.biography }}</p></div>
      </div>
    </details>
  </article>
{% endfor %}
</div>
<script src="{{ '/assets/team.js' | relative_url }}" defer></script>

<details>
<summary><strong>Alumni</strong></summary>
<div>
    <div class="alumni-entry">
        <b>Aref Kalantari</b> <span class="year">(2021-2025)</span><br>
        PhD thesis (Cologne, Neuroscience): A unified framework for multimodla animal studies: data management, MRI quality control, and proportional recovery in mice<br>
        Next position: Postdoc (<a href="https://www.uniklinik-freiburg.de/imbi-en/research-data-management.html" title="Research Data Management group led by Dr. Klaus Kaiser">Research Data Management group led by Dr. Klaus Kaiser</a>, University Hospital Freiburg)
    </div>
    <div class="alumni-entry">
        <b>Irem Dilara Sen</b> <span class="year">(2024-2025)</span><br>
        Master thesis (Bremen, Neuroscience): Long-term cognitive and motor deficits after internal capsule stroke in mice<br>
    </div>
    <div class="alumni-entry">
        <b>Marko Schmelzer</b> <span class="year">(2025)</span><br>
        Bachelor thesis (Cologne, Biology): Histological characterization of stroke induced changes in the white matter<br>
    </div>
    <div class="alumni-entry">
        <b>Carolin Hambrock</b> <span class="year">(2023-2024)</span><br>
        Master thesis (Cologne, Neuroscience): Spontaneous recovery after ischemic stroke: effects of stroke location and reactive astrocytes on thalamic secondary neurodegeneration in mice<br>
    </div>
    <div class="alumni-entry">
        <b>Thomas Kühnel</b> <span class="year">(2023)</span><br>
        Student assistant: histology<br>
        Next position: Master of Biological Sciences (University of Cologne)
    </div>
    <div class="alumni-entry">
        <b>Luca Ruthe</b> <span class="year">(2023-2024)</span><br>
        Bachelor thesis (Neuroscience): Characterization of secondary neurodegeneration in white matter tracts after experimental stroke<br>
        Next position: Internship pharmaceutical industry
    </div>
    <div class="alumni-entry">
        <b>Marc Schneider</b> <span class="year">(2023-2024)</span><br>
        Student assistant: AIDA tools support and further development (adding BIDS-compatibility)<br>
        Next position: Master studies
    </div>
    <div class="alumni-entry">
        <b>Elizabete Vetra</b> <span class="year">(2023)</span><br>
        Student assistant: histology<br>
        Next position: Bachelor studies in Neuroscience (University of Cologne)
    </div>
    <div class="alumni-entry">
        <b>Léon Schulte-Holtey</b> <span class="year">(2022-2023)</span><br>
        Master thesis (Biology): Chemogenetic manipulation of the rubrospinal tract in mice<br>
        Next position: Master studies in Neuroscience (University of Cologne)
    </div>
    <div class="alumni-entry">
        <b>Victor Vera Frazão</b> <span class="year">(2022-2024)</span><br>
        Research assistant: AIDA tools support and further development (debugging and containerization); database maintenance<br>
    </div>
    <div class="alumni-entry">
        <b>Annika Vohn</b> <span class="year">(2022)</span><br>
        Bachelor thesis: Characterization of secondary neurodegeneration in the spinal cord after experimental stroke<br>
        Next position: Master thesis (<a href="https://www.immunosensation.de/members/prof-dr-frank-bradke" title="lab of Frank Bradke">lab of Frank Bradke</a>, Bonn)
    </div>
    <div class="alumni-entry">
        <b>Tim Fleiner</b> <span class="year">(2021)</span><br>
        Internship: AIDAmri<br>
    </div>
    <div class="alumni-entry">
        <b>Prisca Kuhnhäuser</b> <span class="year">(2021-2022)</span><br>
        Master thesis: Identification and manipulation of spasticity-related extrapyramidal motor nuclei in mice<br>
        Next position: PhD student (<a href="https://anatomie.uni-koeln.de/institut-ii/ag-prof-vogt" title="lab of Johannes Vogt">lab of Johannes Vogt</a>, University of Cologne)
    </div>
    <div class="alumni-entry">
        <b>Jule Ullert</b> <span class="year">(2021-2023)</span><br>
        Bachelor thesis (Biology)<br>
    </div>
    <div class="alumni-entry">
        <b>Philip Baxter Aßmann</b> <span class="year">(2020-2021)</span><br>
        Student assistant: histology<br>
    </div>
    <div class="alumni-entry">
        <b>Jan Götz</b> <span class="year">(2020-2022)</span><br>
        Research assistant and master thesis: Longitudinal gene expression analysis in experimental stroke<br>
        Next position: PhD student (<a href="https://anatomie.uni-koeln.de/institut-ii/ag-prof-vogt" title="lab of Johannes Vogt">lab of Johannes Vogt</a>, University of Cologne)
    </div>
    <div class="alumni-entry">
        <b>Sebastian Kloubert</b> <span class="year">(2020-2021)</span><br>
        Bachelor thesis (Biology): Automated movement analysis of mouse beam walking using neural networks<br>
    </div>
    <div class="alumni-entry">
        <b>Leon Scharwächter</b> <span class="year">(2020-2021)</span><br>
        Student assistant: AIDA tools<br>
    </div>
    <div class="alumni-entry">
        <b>Mayan Baues</b> <span class="year">(2020-2022)</span><br>
        Student assistant: histology<br>
        Next position: Research associate (<a href="https://www.neurosciences.univ-bonn.de/people/staff-research-group-leader/michael-wenzel" title="lab of Michael Wenzel">lab of Michael Wenzel</a>, University Hospital Bonn)
    </div>
    <div class="alumni-entry">
        <b>Nicole Kuschel</b> <span class="year">(2019-2021)</span><br>
        Student assistant: video analysis<br>
    </div>
    <div class="alumni-entry">
        <b>Veronika Fritz</b> <span class="year">(2018-2021)</span><br>
        Student assistant and Bachelor thesis: Neuronal tracing in mice with cortical stroke<br>
        Next position: PhD student (<a href="https://www.cecad.uni-koeln.de/research/principal-investigators/prof-dr-natalia-kononenko/" title="CECAD Kononenko Lab">lab of Natalia Kononenko</a>, University of Cologne)
    </div>
    <div class="alumni-entry">
        <b>Alina Jakobs</b> <span class="year">(2018)</span><br>
        Student assistant: histology<br>
    </div>
    <div class="alumni-entry">
        <b>Olivia Käsgen</b> <span class="year">(2018-2020)</span><br>
        Biological technical assistant<br>
    </div>
    <div class="alumni-entry">
        <b>Joshua Strelow</b> <span class="year">(2018-2019)</span><br>
        Student assistant: behavior analysis<br>
        Next position: PhD student (lab of Michael Barbe, University Hospital Cologne)
        </div>
    <div class="alumni-entry">
         <b>Marieke Nill</b> <span class="year">(2017-2020)</span><br>
        Biological technical assistant<br>
        Next position: BTA (Lab of Roland Ullrich, University Hospital Cologne)
    </div>
    <div class="alumni-entry">
        <b>Niklas Pallast</b> <span class="year">(2017-2020)</span><br>
         PhD thesis: A versatile registration and analysis pipeline for multimodal brain imaging data<br>
        Next position: Head of Product Management (<a href="https://www.synlab.de/" title="SYNLAB Holding Deutschland GmbH">SYNLAB Holding Deutschland GmbH</a>)
    </div>
    <div class="alumni-entry">
        <b>Frederique Wieters</b> <span class="year">(2017-2021)</span><br>
        PhD thesis: Evaluation of spasticity in experimental models of ischemic stroke<br>
        Next position: Medical science Liaison Manager und CIDP (<a href="https://www.argenx.de/" title="Argenx">Argenx</a>)
        </div>
    </div>
</details>
