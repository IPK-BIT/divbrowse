============
Installation
============

Installation via pip
====================

It is strongly recommended to create a virtual environment beforehand, e.g. via conda or virtualenv.

You can then install DivBrowse from PyPI via pip::

    $ pip install divbrowse



Installation via Docker or Podman
=================================

Pull the image::

    $ sudo docker pull ipkbit/divbrowse

or with Podman::

    $ podman pull docker.io/ipkbit/divbrowse

Start a container from the image::

    $ sudo docker run --name divbrowse -v /home/myusername/divbrowse_data:/opt/divbrowse/:Z -it -p 8080:8080 ipkbit/divbrowse:latest

or with Podman::

    $ podman run --name divbrowse -v /home/myusername/divbrowse_data:/opt/divbrowse/:Z -it -p 8080:8080 ipkbit/divbrowse:latest




Installation from sources on Github via conda
=============================================

You can install the latest version from the main branch of the GitHub repository with the following shell commands::

    $ git clone https://github.com/IPK-BIT/divbrowse
    $ cd divbrowse
    $ conda env create -f environment.yml