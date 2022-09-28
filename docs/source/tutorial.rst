========
Tutorial
========

Here we describe the setup of a DivBrowse instance with a VCF file of Homo sapiens step by step.


Setup a directory structure for the new instance
================================================

- Create a new project directory for your DivBrowse instance: ::

    $ mkdir ~/divbrowse_instance_homo_sapiens
    $ cd ~/divbrowse_instance_homo_sapiens

- Create a new directory `data` within your previously created project directory and switch this new directory: ::

    $ mkdir data
    $ cd data


Obtaining VCF files from the European Nucleotide Archive
========================================================

- Download the VCF files for all chromosomes from the following EBI-ENA web page: https://www.ebi.ac.uk/ena/browser/view/PRJEB30460
- Concatenate all 23 VCF files into one combined VCF file with bcftools:

.. code-block::

   $ bcftools concat --output-type z -o ./ALL.shapeit2_integrated_v1a.GRCh38.20181129.phased.vcf.gz \
   ALL.chr1.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr2.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr3.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr4.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr5.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr6.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr7.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr8.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr9.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr10.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr11.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr12.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr13.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr14.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr15.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr16.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr17.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr18.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr19.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr20.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chr21.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz ALL.chr22.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz \
   ALL.chrX.shapeit2_integrated_v1a.GRCh38.20181129.GRCh38.phased.vcf.gz

- Convert the concatenated VCF file to a Zarr archive with the DivBrowse CLI: ::

    $ divbrowse vcf2zarr --path-vcf ./ALL.shapeit2_integrated_v1a.GRCh38.20181129.phased.vcf.gz --path-zarr ./ALL.shapeit2_integrated_v1a.GRCh38.20181129.phased.zarr



Obtaining the gene annotation from ensemble.org
===============================================

- Download the file ``Homo_sapiens.GRCh38.107.chr.gff3.gz`` from: http://ftp.ensembl.org/pub/release-107/gff3/homo_sapiens/ ::

    $ wget http://ftp.ensembl.org/pub/release-107/gff3/homo_sapiens/Homo_sapiens.GRCh38.107.chr.gff3.gz

- Uncompress the gzipped file: ::

    $ gzip -d Homo_sapiens.GRCh38.107.chr.gff3.gz

- Now you should have ``ALL.shapeit2_integrated_v1a.GRCh38.20181129.phased.zarr`` and ``Homo_sapiens.GRCh38.107.chr.gff3`` in the path ``~/divbrowse_instance_homo_sapiens/data``


Setup configuration file
========================

- Switch to the project directory: ::

    $ cd ~/divbrowse_instance_homo_sapiens

- And download the configuration file ``divbrowse.config.yml`` from the Github repository: ::

    $ wget https://www.github.com



Start intergrated web server to serve the instance
==================================================

- Now you can start the configured instance by executing the following command: ::

    $ divbrowse start
