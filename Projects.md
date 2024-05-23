---
title: Projects
layout: default
---
### [Home](index.md) | [Publications](Publications.md) | [Projects](Projects.md) | [Research](Research.md) | [Our Team](Team.md) | [Contact](Contact.md) |

## Our AIDA toolbox
<img    src="img/AIDA_Logo.png"
            alt="aidalogo"
            style="width: 400px; height: auto; float: right; margin-right: 10px;" />
With the Atlas-based Imaging Data Analysis Pipeline AIDA we provide a set of analysis tools for structural and functional MRI of the mouse brain. Please check out our different project repositories listed below!

### [AIDA*mri*](https://github.com/Aswendt-Lab/AIDAmri)
AIDA*mri* is a fully automatized and containerized pipeline for anatomical, diffusion-weighted and functional MRI data processing. It provides raw data conversion and batch processing, including bias field correction, brain extraction and atlas registration, while organizing data according to the Brain Imaging Data Structure (BIDS[^1]) format. AIDA*mri* is exclusively available as a Docker[^2] image to allow for cross-platform usage and easy installation.
### [AIDA*qc*](https://github.com/Aswendt-Lab/AIDAqc)
AIDA*qc* is an automated and simple Python tool for fast quality analysis of animal MRI. It is easily installable and provides a conda environment for fast and simple usage. Quality evaluation includes (temporal) signal-to-noise ratio ((t)SNR), motion artifacts, and spacial resolution homogeneity.
### [AIDA*histo*](https://github.com/Aswendt-Lab/AIDAhisto)
AIDA*histo* is a MATLAB tool for cell detection in immunostainings and histological stainings of mouse brain and spinal cord sections. It provides Allen Mouse Brain and Spinal Cord Atlas registration with microscopy files in ImageJ and automated cell counting.
### [AIDA*connect*](https://github.com/Aswendt-Lab/AIDAconnect)
AIDA*connect* is a comprehensive MATLAB toolbox for mouse brain MRI data analysis and connectivity analysis using graph theory.

[^1]: [https://bids.neuroimaging.io/](https://bids.neuroimaging.io/)
[^2]: [https://www.docker.com/](https://www.docker.com/)