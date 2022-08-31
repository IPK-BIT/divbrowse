import os, sys

sys.setrecursionlimit(1000000)

from pprint import pprint

import click
import yaml
import gzip
import allel
import zarr
import pandas as pd
import numcodecs
from waitress import serve

from divbrowse import log


from divbrowse import __version__ as DIVBROWSE_VERSION

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
@click.version_option(prog_name='DivBrowse', version=DIVBROWSE_VERSION)
def main():
    """This is the DivBrowse CLI"""
    pass


@click.command()
def calcsumstats():

    click.echo('Starting calculation of variant summary statistics...')
    log.info('Starting calculation of variant summary statistics...')

    from divbrowse.lib.annotation_data import AnnotationData
    from divbrowse.lib.genotype_data import GenotypeData

    try:
        with open('divbrowse.config.yml') as config_file:
            config = yaml.full_load(config_file)
    except FileNotFoundError:
        log.error('Divbrowse config file `divbrowse.config.yml` not found in current directory!')
        exit(1)

    gd = GenotypeData(config)
    ad = AnnotationData(config, gd)

    vcf_header_lines = gd.get_vcf_header()
    print(vcf_header_lines)





@click.command()
@click.option('--path-vcf', help='Full path to to VCF file that should be converted to a Zarr archive')
@click.option('--path-zarr', help='Full path where to save the Zarr archive')
def vcf2zarr(path_vcf: str, path_zarr: str):

    if path_vcf == None:
        vcf_files = []
        path = os.getcwd()

        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith(('.vcf', '.vcf.gz')):
                    vcf_files.append(entry.path)
        
        click.secho('The following VCF files have been found in current working directory. Please choose the one you want to convert to the Zarr format:', fg='yellow')
        i = 0
        for _vcf_file in vcf_files:
            click.secho('['+str(i)+'] '+os.path.basename(_vcf_file), fg='yellow')
            i = i + 1

        selected_vcf_number = click.prompt(click.style('Please enter the number of the VCF file', fg='yellow'), type=int)

        if selected_vcf_number >= len(vcf_files):
            log.error('The given number for a VCF file is not valid.')
            exit(1)

        path_vcf = str(vcf_files[selected_vcf_number])
        click.secho('You have selected the following VCF file:: '+path_vcf, fg='yellow')

    if path_zarr == None:
        path_zarr = path_vcf + '.zarr'


    vcf_header_lines = []
    if path_vcf.endswith('gz'):
        vcf_file = gzip.open(path_vcf, mode='rt', encoding='utf-8')
    else:
        vcf_file = open(path_vcf, mode='r', buffering=0, encoding='utf-8')

    vcf_line = vcf_file.readline()
    while vcf_line:
        if vcf_line.startswith('##'):
            vcf_header_lines.append(vcf_line)
            vcf_line = vcf_file.readline()
        else:
            break

    with open("____vcf_export_header_lines____.vcf", "w") as vcf_header_lines_file:
        vcf_header_lines_file.write("".join(vcf_header_lines))


    try:
        allel.vcf_to_zarr(path_vcf, path_zarr, group='/', fields='*', exclude_fields=['variants/numalt', 'variants/altlen', 'variants/is_snp'], log=sys.stdout, compressor=numcodecs.Blosc(cname='zstd', clevel=5, shuffle=False))
    except ValueError as error_msg:
        log.error(error_msg)


    click.secho('Conversion to Zarr finished.', fg='green')
    click.secho('The Zarr archive was saved to this path: '+path_zarr, fg='green')



@click.command()
@click.option('--host', default='0.0.0.0', help='IP address to bind the DivBrowse server to', show_default=True)
@click.option('--port', default='8080', help='Port number to bind the DivBrowse server to', show_default=True)
@click.option('--infer-config', is_flag=True, help='If set: infer a basic configuration from the provided VCF and GFF/GFF3 files and do not use an existing `divbrowse.config.yml`')
@click.option('--save-config', type=click.Path(file_okay=True, writable=True), help='Save the inferred configuration as a YAML file. Please provide a relative or absolute path.')
def start(host: str, port: str, infer_config: bool, save_config):
    from divbrowse.server import create_app

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
            i = i + 1

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

        config_runtime['datadir'] = path+'/'
        config_runtime['variants']['zarr_dir'] = os.path.basename(path_zarr)
        config_runtime['gff3']['filename'] = os.path.basename(gff3_files[0])
        config_runtime['gff3']['feature_type_with_description'] = 'gene'
        config_runtime['gff3']['main_feature_types_for_genes_track'] = ['gene']
        config_runtime['chromosome_labels'] = chromosome_labels
        config_runtime['centromeres_positions'] = centromeres_positions
        config_runtime['gff3_chromosome_labels'] = gff3_chromosome_labels

        if save_config is not None:
            with open(save_config, 'w') as yaml_file:
                yaml.dump(config_runtime, yaml_file, default_flow_style=False)

    click.secho('Starting DivBrowse server...', fg='green', bold=True)

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

    serve(app, host=host, port=int(port))





main.add_command(vcf2zarr)
main.add_command(start)
main.add_command(calcsumstats)

if __name__ == '__main__':
    main()