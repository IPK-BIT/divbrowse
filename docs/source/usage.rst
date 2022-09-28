=====
Usage
=====

After installation you can use the DivBrowse CLI to start a local instance of DivBrowse on your computer.
You only have to provide a *.vcf/*.vcf.gz file and a *.gff/*.gff3 file in a subdirectory.
Within the subdirectory you can start a DivBrowse instance via the following command::

    $ divbrowse start --infer-config

An attempt is made to infer the configuration from the data provided. 
A Zarr archive of the provided VCF file is automatically created and save in the same directory as the VCF file with `.zarr` appended to the original filename of the provided VCF file.

If you want to improve and customize the configuration, you can take the example config YAML file `divbrowse.config.yml.example` 
`(click to open)`_ file from the GitHub repository, rename it to `divbrowse.config.yml` and edit it to fit your requirements.

.. _(click to open): https://raw.githubusercontent.com/IPK-BIT/divbrowse/main/divbrowse/divbrowse.config.yml.example

__ 

If you provide a manually written `divbrowse.config.yml`, you can start a DivBrowse instance using this customized configuration by executing the following CLI command in the directory consisting your custom config YAML file::

    $ divbrowse start


Manual conversion of VCF file to Zarr format
============================================

The CLI allows to convert VCF files to Zarr archives independently:

    $ divbrowse vcf2zarr --path-vcf /path/to/my_variants.vcf.gz --path-zarr /path/to/my_variants.zarr

The created Zarr archive can then be used in the configuration settings file `divbrowse.config.yml` as data source for the variant data:

.. code-block:: yaml

   datadir: /path/to/

   variants:
     zarr_dir: my_variants.zarr


DivBrowse CLI reference
=======================

.. click:: divbrowse.cli:main
   :prog: divbrowse
   :nested: full
   :commands: start
