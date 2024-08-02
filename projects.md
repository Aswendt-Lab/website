---
title: Projects
layout: page
---

## Spontaneous recovery after stroke
Loss of function after stroke is caused by cell death and breakdown of the functional networks in the infarcted and connected brain regions. To some extent, the affected limb regains function, in a form of spontaneous recovery during the first 3 months after stroke. However, this recovery is generally incomplete and the underlying neural and molecular mechanisms are still unknown. In this project we are investigating brain/circuit activation patterns and analyse the transcriptome in the ipsi- and contralesional hemispheres of recovered vs. non-recovered mice after experimental stroke.

## Our AIDA toolbox
<img    src="img/AIDA_Logo.png"
            alt="aidalogo"
            style="width: 200px; height: auto; float: right; margin-right: 10px;" />
Working with in vivo and ex vivo imaging at different spatial resolutions requires a common atlas registration for cross-modality comparisons. For example, if we detect connectivity change in primary motor cortex with MRI, it will be of interest to investigate the same brain area with histology. In order to merge in vivo MRI with 2D histology, we have created software pipelines for automated processing of structural and functional mouse brain MRI (AIDAmri) and automated cell counting - optimised for mouse brain histology and immunostainings (AIDAhisto). These pipelines include accurate approaches to register whole brain (MRI) and single slices (histology) respectively with the Allen Mouse Brain Atlas. 
With the Atlas-based Imaging Data Analysis Pipeline AIDA we provide a set of analysis tools for structural and functional MRI of the mouse brain. Please check out our different project repositories listed below!

### [AIDA*mri*](https://github.com/Aswendt-Lab/AIDAmri)
AIDA*mri* is a fully automatized and containerized pipeline for anatomical, diffusion-weighted and functional MRI data processing. It provides raw data conversion and batch processing, including bias field correction, brain extraction and atlas registration, while organizing data according to the Brain Imaging Data Structure (BIDS[^1]) format. AIDA*mri* is exclusively available as a Docker[^2] image to allow for cross-platform usage and easy installation.
### [AIDA*qc*](https://github.com/Aswendt-Lab/AIDAqc)
AIDA*qc* is an automated and simple Python tool for fast quality analysis of animal MRI. It is easily installable and provides a conda environment for fast and simple usage. Quality evaluation includes (temporal) signal-to-noise ratio ((t)SNR), motion artifacts, and spacial resolution homogeneity.
### [AIDA*histo*](https://github.com/Aswendt-Lab/AIDAhisto)
AIDA*histo* is a MATLAB tool for cell detection in immunostainings and histological stainings of mouse brain and spinal cord sections. It provides Allen Mouse Brain and Spinal Cord Atlas registration with microscopy files in ImageJ and automated cell counting.
### [AIDA*connect*](https://github.com/Aswendt-Lab/AIDAconnect)
AIDA*connect* is a comprehensive MATLAB toolbox for mouse brain MRI data analysis and connectivity analysis using graph theory.

### Data management of large, multimodal animal data 
To obtain valid scientific results in pre-clinical research, standardization of experimental protocols and data handling need to be set before starting the actual experiment. Efficient data management becomes more and more important with the increasing number and variety of experimental procedures. However, to date, preclinical research is still in a transition phase. While the recorded data type is predominantly electronic data, the documentation is still the lab notebook. We designed a database template which is useful for all labs working with laboratory animals and the adaption to specific research projects requires no prior scripting expertise. The database works operating-system independent through the web browser and allows multiple user to work simultaneously. The data entry is monitored and restricted for particular tests according to the user management in order to keep for example users during the experiment blinded for the experimental group. Furthermore, we have established an efficient workflow to store and share the experimental data according to FAIR prinicples.
[Video tutorial](https://static-content.springer.com/esm/art%3A10.1038%2Fs41597-023-02242-8/MediaObjects/41597_2023_2242_MOESM1_ESM.pdf)



[^1]: [https://bids.neuroimaging.io/](https://bids.neuroimaging.io/)
[^2]: [https://www.docker.com/](https://www.docker.com/)
