import os, sys, fnmatch
from pprint import pprint
import multiprocessing

import click
import yaml
import allel
import zarr
import pandas as pd
import numcodecs

from divbrowse import log
from divbrowse.lib.utils import StandaloneApplication
from divbrowse.server import create_app


def get_config_skeleton():
    path_config_skeleton = os.path.join(os.path.dirname(__file__), 'divbrowse.config.yml.skeleton')
    try:
        with open(path_config_skeleton) as config_file:
            config = yaml.full_load(config_file)
    except FileNotFoundError:
        log.error('Divbrowse config file `divbrowse.config.yml` not found in current directory!')
        exit(1)

    return config


def get_chromosomes(path_zarr):
    callset = zarr.open_group(path_zarr, mode='r')
    chromosomes = pd.unique(callset['variants/CHROM'][:]).tolist()
    return chromosomes



@click.group()
def main():
    """This is the DivBrowse CLI"""
    pass


@click.command()
def test():
    click.echo('This is a test')
    log.info('Logging info test')



@click.command()
@click.option('--host', default='0.0.0.0', help='IP address to bind the DivBrowse server to')
@click.option('--port', default='8080', help='Port number to bind the DivBrowse server to')
@click.option('--infer-config', is_flag=True)
def start(host: str, port: str, infer_config: bool):

    if infer_config:

        vcf_files = []
        path = os.getcwd()

        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith(('.vcf', '.vcf.gz')):
                    vcf_files.append(entry.path)
        
        click.secho('The following VCF files have been found. Please choose the one you want to visualize with DivBrowse:', fg='yellow')
        i = 0
        for _vcf_file in vcf_files:
            click.secho('['+str(i)+'] '+os.path.basename(_vcf_file), fg='yellow')

        selected_vcf_number = click.prompt(click.style('Please enter the number of the VCF file', fg='yellow'), type=int)

        if selected_vcf_number >= len(vcf_files):
            log.error('The given number for a VCF file is not valid.')
            exit(1)

        click.secho('Your VCF choice: '+str(vcf_files[selected_vcf_number]), fg='yellow')
        selected_vcf = vcf_files[selected_vcf_number]

        path_zarr = selected_vcf + '.zarr'
        if not os.path.isdir(path_zarr):
            allel.vcf_to_zarr(selected_vcf, path_zarr, group='/', fields='*', log=sys.stdout, compressor=numcodecs.Blosc(cname='zstd', clevel=1, shuffle=False)) # cname='zstd'


        gff3_files = []
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith(('.gff', '.gff3')):
                    gff3_files.append(entry.path)


        click.secho('The following GFF/GFF3 files have been found. Please choose the one you want to visualize with DivBrowse:', fg='yellow')
        i = 0
        for _gff3_file in gff3_files:
            click.secho('['+str(i)+'] '+os.path.basename(_gff3_file), fg='yellow')

        selected_gff3_number = click.prompt(click.style('Please enter the number of the GFF/GFF3 file', fg='yellow'), type=int)

        if selected_gff3_number >= len(gff3_files):
            log.error('The given number for a GFF/GFF3 file is not valid.')
            exit(1)

        click.secho('Your GFF/GFF3 choice: '+str(gff3_files[selected_gff3_number]), fg='yellow')
        selected_gff3 = gff3_files[selected_gff3_number]


        chromosomes_vcf = get_chromosomes(path_zarr)
        chromosome_labels = dict(zip(chromosomes_vcf, chromosomes_vcf))

        centromeres_positions = {k:'0' for k, v in chromosome_labels.items()}

        genes = allel.gff3_to_dataframe(selected_gff3)
        chromosomes_gff = genes['seqid'].unique().tolist()
        gff3_chromosome_labels = dict(zip(chromosomes_vcf, chromosomes_gff))

        config_runtime = get_config_skeleton()

        config_runtime['data']['datadir'] = path+'/'
        config_runtime['data']['zarr_variants'] = os.path.basename(path_zarr)
        config_runtime['gff3']['filename'] = os.path.basename(gff3_files[0])
        config_runtime['gff3']['feature_type_with_description'] = 'gene'
        config_runtime['gff3']['main_feature_type_for_genes_track'] = 'gene'
        config_runtime['chromosome_labels'] = chromosome_labels
        config_runtime['centromeres_positions'] = centromeres_positions
        config_runtime['gff3_chromosome_labels'] = gff3_chromosome_labels

    click.secho('Starting DivBrowse server using gunicorn...', fg='green', bold=True)

    if host == '0.0.0.0':
        import socket
        url = 'http://'+socket.gethostname()+':'+str(port)+'/index.html'
    else:
        url = 'http://'+str(host)+':'+str(port)+'/index.html'

    click.secho('DivBrowse should be available under the following URL: '+str(url), fg='green', bold=True)

    if infer_config:
        app = create_app(config_runtime=config_runtime)
    else:
        app = create_app()

    options = {
        'bind': '%s:%s' % (host, port),
        'workers': 1,
    }
    StandaloneApplication(app, options).run()



@click.command()
@click.option('--host', default='0.0.0.0', help='IP address to bind the DivBrowse server to')
@click.option('--port', default='8080', help='Port number to bind the DivBrowse server to')
def starttest(host: str, port: str):
    click.secho('Starting DivBrowse server using gunicorn...', fg='green', bold=True)
    
    app = create_app()
    options = {
        'bind': '%s:%s' % (host, port),
        'workers': 1,
    }
    StandaloneApplication(app, options).run()
    


main.add_command(test)
main.add_command(start)
main.add_command(starttest)

if __name__ == '__main__':
    main()