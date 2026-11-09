---
title: Software & Data
layout: page
---

Open tools for preclinical imaging, atlas registration, quality control, and reproducible research.

[Browse all repositories](https://github.com/Aswendt-Lab) · [Explore shared datasets](https://gin.g-node.org/Aswendt_Lab) · [Open office hour on Zoom](https://uni-frankfurt.zoom-x.de/j/63112745009?pwd=JBTjMVbuaTw9cZvFnppTwCPjGdQEyx.1) — Thursdays, 15:00 Europe/Berlin

{% include tools-feature.html %}

## The AIDA toolbox

<div class="software-detail" markdown="1">
<div class="software-copy" markdown="1">

Working with in vivo and ex vivo imaging at different spatial resolutions requires a common atlas registration for cross-modality comparisons. For example, if we detect connectivity change in primary motor cortex with MRI, it will be of interest to investigate the same brain area with histology. In order to merge in vivo MRI with 2D histology, we have created software pipelines for automated processing of structural and functional mouse brain MRI (AIDAmri) and automated cell counting - optimised for mouse brain histology and immunostainings (AIDAhisto). These pipelines include accurate approaches to register whole brain (MRI) and single slices (histology) respectively with the Allen Mouse Brain Atlas.
With the Atlas-based Imaging Data Analysis Pipeline AIDA we provide a set of analysis tools for structural and functional MRI of the mouse brain. Please check out our different project repositories listed below!

</div>
<div class="software-media">
<figure class="pdf-preview"><a href="{{ '/pdf/Neuroinformatics_Aswendt_2022.pdf' | relative_url }}" target="_blank" rel="noopener"><img src="{{ '/img/Neuroinformatics_Aswendt_2022-preview.jpg' | relative_url }}" alt="First-page preview of the AIDA toolbox poster" loading="lazy" decoding="async"><span>AIDA toolbox poster · Open PDF ↗</span></a></figure>
</div>
</div>

### [AIDA*mri*](https://github.com/Aswendt-Lab/AIDAmri)

<div class="software-detail" markdown="1">
<div class="software-copy" markdown="1">

AIDA*mri* is a fully automatized and containerized pipeline for anatomical, diffusion-weighted and functional MRI data processing. It provides raw data conversion and batch processing, including bias field correction, brain extraction and atlas registration, while organizing data according to the Brain Imaging Data Structure (BIDS[^1]) format. AIDA*mri* is exclusively available as a Docker[^2] image to allow for cross-platform usage and easy installation.

</div>
<div class="software-media">
<figure class="pdf-preview"><a href="{{ '/pdf/TOPIM2018_MA.pdf' | relative_url }}" target="_blank" rel="noopener"><img src="{{ '/img/TOPIM2018_MA-preview.jpg' | relative_url }}" alt="First-page preview of the AIDAmri poster" loading="lazy" decoding="async"><span>AIDAmri poster · Open PDF ↗</span></a></figure>
</div>
</div>

### [AIDA*qc*](https://github.com/Aswendt-Lab/AIDAqc)

<div class="software-detail" markdown="1">
<div class="software-copy" markdown="1">

AIDA*qc* is an automated and simple Python tool for fast quality analysis of animal MRI. It is easily installable and provides a conda environment for fast and simple usage. Quality evaluation includes (temporal) signal-to-noise ratio ((t)SNR), motion artifacts, and spatial resolution homogeneity.
[Watch Video](https://www.youtube.com/watch?v=SP4sWW313DQ)

</div>
<div class="software-media">
<a class="qc-visual" href="https://github.com/Aswendt-Lab/AIDAqc"><img src="{{ '/img/AIDAqc-logo-wide.png' | relative_url }}" alt="AIDAqc quality control toolbox" loading="lazy"><img src="{{ '/img/AIDAqc-workflow.png' | relative_url }}" alt="AIDAqc workflow from MRI input through quality assessment and reports" loading="lazy"></a>
</div>
</div>

### [AIDA*histo*](https://github.com/Aswendt-Lab/AIDAhisto)
AIDA*histo* is a MATLAB tool for cell detection in immunostainings and histological stainings of mouse brain and spinal cord sections. It provides Allen Mouse Brain and Spinal Cord Atlas registration with microscopy files in ImageJ and automated cell counting.
### [AIDA*connect*](https://github.com/Aswendt-Lab/AIDAconnect)
AIDA*connect* is a comprehensive MATLAB toolbox for mouse brain MRI data analysis and connectivity analysis using graph theory.


## Data management of large, multimodal animal data
<div class="software-detail" markdown="1">
<div class="software-copy" markdown="1">

### Animal research database

To obtain valid scientific results in pre-clinical research, standardization of experimental protocols and data handling need to be set before starting the actual experiment. Efficient data management becomes more and more important with the increasing number and variety of experimental procedures. However, to date, preclinical research is still in a transition phase. While the recorded data type is predominantly electronic data, the documentation is still the lab notebook. We designed a database template which is useful for all labs working with laboratory animals and the adaption to specific research projects requires no prior scripting expertise [Pallast et al. Database 2018](https://doi.org/10.1093/database/bay124). The database works operating-system independent through the web browser and allows multiple user to work simultaneously. The data entry is monitored and restricted for particular tests according to the user management in order to keep for example users during the experiment blinded for the experimental group
[Watch the database tutorial]({{ '/videos/Database_Tutorial.mp4' | relative_url }}).

</div>
<div class="software-media">
<figure class="pdf-preview"><a href="{{ '/pdf/Poster_RDB_Aswendt_v1.pdf' | relative_url }}" target="_blank" rel="noopener"><img src="{{ '/img/Poster_RDB_Aswendt_v1-preview.jpg' | relative_url }}" alt="First-page preview of the Database poster" loading="lazy" decoding="async"><span>Database poster · Open PDF ↗</span></a></figure>
</div>
</div>

<div class="software-detail" markdown="1">
<div class="software-copy" markdown="1">

### FAIR data workflows

FAIR workflow for multimodal datasets using DataLad from [Kalantari et al. Scientific Data 2023](https://doi.org/10.1038/s41597-023-02242-8).

Furthermore, we have established an efficient workflow to store and share the experimental data according to FAIR principles [Kalantari et al. Scientific Data 2023](https://doi.org/10.1038/s41597-023-02242-8).
[Read the workflow supplement (PDF)](https://static-content.springer.com/esm/art%3A10.1038%2Fs41597-023-02242-8/MediaObjects/41597_2023_2242_MOESM1_ESM.pdf)

</div>
<div class="software-media">
<figure class="pdf-preview"><a href="{{ '/pdf/Poster_RDM_Final_AKalantari_EMIM.pdf' | relative_url }}" target="_blank" rel="noopener"><img src="{{ '/img/Poster_RDM_Final_AKalantari_EMIM-preview.jpg' | relative_url }}" alt="First-page preview of the Research data management poster" loading="lazy" decoding="async"><span>Research data management poster · Open PDF ↗</span></a></figure><a href="{{ '/img/DataladWorkflow.png' | relative_url }}"><img class="data-workflow" src="{{ '/img/DataladWorkflow.png' | relative_url }}" alt="DataLad workflow for managing multimodal animal datasets" loading="lazy"></a>
</div>
</div>

[^1]: [https://bids.neuroimaging.io/](https://bids.neuroimaging.io/)
[^2]: [https://www.docker.com/](https://www.docker.com/)
