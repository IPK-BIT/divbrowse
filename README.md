[![Documentation Status](https://readthedocs.org/projects/divbrowse/badge/?version=latest)](https://divbrowse.readthedocs.io/?badge=latest)
[![Python](https://img.shields.io/pypi/pyversions/divbrowse.svg?style=plastic)](https://badge.fury.io/py/divbrowse)
[![PyPI version](https://badge.fury.io/py/divbrowse.svg)](https://badge.fury.io/py/divbrowse)
[![PyPI Downloads](https://img.shields.io/pypi/dm/divbrowse.svg?label=PyPI%20downloads)](https://pypi.org/project/divbrowse/)
[![Preprint on bioRxiv.org](https://img.shields.io/badge/DOI-10.1101%2F2022.09.22.509016-green)](https://doi.org/10.1101/2022.09.22.509016)

- **Website:** https://divbrowse.ipk-gatersleben.de
- **Documentation:** https://divbrowse.readthedocs.io/

# DivBrowse

  - [About DivBrowse](#about-divbrowse)
  - [Try out DivBrowse](#try-out-divbrowse)
  - [Screenshots](#screenshots)
  - [Usage workflow concept](#usage-workflow-concept)
  - [Architecture](#architecture)


## About DivBrowse

DivBrowse is a web application for interactive exploration and analysis of very large SNP matrices.

It offers a novel approach for interactive visualization and analysis of genomic diversity data and optionally also gene annotation data. The use of standard file formats for data input supports interoperability and seamless deployment of application instances based on established bioinformatics pipelines. The possible integration into 3rd-party web applications supports interoperability and reusability.

The integrated ad-hoc calculation of variant summary statistics and principal component analysis enables the user to perform interactive analysis of population structure for single genetic features like genes, exons and promoter regions. Data interoperability is achieved by the possibility to export genomic diversity data for genomic regions of interest in standardized VCF files.


## Try out DivBrowse

If you want to test DivBrowse please visit the demo instance online at:
https://divbrowse.ipk-gatersleben.de/demo/


## Screenshots

![DivBrowse GUI](https://github.com/IPK-BIT/divbrowse/blob/main/docs/source/images/divbrowse_main_gui_screenshot.png?raw=true)


## Usage workflow concept

![Usage workflow concept](https://github.com/IPK-BIT/divbrowse/blob/main/docs/source/images/paper_figures_usage_concept.png?raw=true)


## Architecture

![Architecture](https://github.com/IPK-BIT/divbrowse/blob/main/docs/source/images/paper_figures_general_architecture.png?raw=true)