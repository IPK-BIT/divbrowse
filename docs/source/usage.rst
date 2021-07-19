=====
Usage
=====

After installation you can use the DivBrowse CLI to start a local instance of DivBrowse on your computer.
You only have to provide a *.vcf/*.vcf.gz file and a *.gff/*.gff3 file in a subdirectory.
Within the subdirectory you can start a DivBrowse instance via the following command::

    $ divbrowse start --infer-config

An attempt is made to infer the configuration from the data provided.

If you want to improve and customize the configuration, you can take the example config YAML file `divbrowse.config.yml.example` 
`(click to open) https://raw.githubusercontent.com/IPK-BIT/divbrowse/main/divbrowse/divbrowse.config.yml.example`__
file from the GitHub repository, rename it to `divbrowse.config.yml` and edit it to fit your requirements.

If you provide a `divbrowse.config.yml` you can start a DivBrowse instance using this customized configuration by executing the following CLI command in the directory consisting the config YAML file::

    $ divbrowse start




Installation from sources on Github via conda
=============================================

You can install the latest version from the main branch of the GitHub repository with the following shell commands::

    $ git clone https://github.com/IPK-BIT/divbrowse
    $ cd divbrowse
    $ conda env create -f environment.yml