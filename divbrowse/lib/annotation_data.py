import json
import os
from timeit import default_timer as timer

import allel
import numpy as np
import pandas as pd
import zarr
from pandarallel import pandarallel
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

pandarallel.initialize(nb_workers=3, progress_bar=True)


class AnnotationData:

    def __init__(self, config, gd):

        self.config = config
        self.gd = gd
        self.datadir = config['data']['datadir']

        self.available = {
            'gff3': False
        }

        if config['gff3']['filename']:
            self.path_gff3 = self.datadir + config['gff3']['filename']
            if os.path.exists(self.path_gff3):
                self.available['gff3'] = True
            else:
                exit('ERROR: the configured path for the GFF3 file does not exist or is not accessible')

        self.metadata_gff3 = {
            'has_gff3': self.available['gff3'],
            'count_genes': 0,
        }
        self.genes_list = []

        if self.available['gff3']:
            self._load_gff3_data()


    def _load_gff3_data(self):

        gff3_chromosome_labels = self.config['gff3_chromosome_labels']
        self.metadata_gff3['gff3_to_vcf_chromosome_mapping'] = {v: k for k, v in self.config['gff3_chromosome_labels'].items()}

        self.chrom_gff3_map = { str(key): value for (key, value) in gff3_chromosome_labels.items()}

        key_confidence = 'primary_confidence_class'
        if self.config['gff3']['key_confidence']:
            key_confidence = str(self.config['gff3']['key_confidence'])

        key_ontology = 'Ontology_term'
        if self.config['gff3']['key_ontology']:
            key_ontology = str(self.config['gff3']['key_ontology'])

        self.genes = allel.gff3_to_dataframe(self.path_gff3, attributes=['ID', key_confidence, 'Parent', 'description', key_ontology])
        self.genes.rename(columns={key_confidence: "primary_confidence_class", key_ontology: "Ontology_term"}, inplace=True)

        genes_only = self.genes.loc[(self.genes['type'] == 'gene')] # gene or transcript
        
        self.metadata_gff3['count_genes'] = int(len(genes_only.index))
        self.metadata_gff3.update(dict(self.config['gff3']))

        # list of genes with descriptions and start+end positions
        # TODO: make this configureable via ini file
        genes_with_descriptions = self.genes.loc[(self.genes['type'] == 'mRNA')] # gene or transcript


        def count_exon_snps(row):
            _chromosome_gff3 = row['seqid']
            _chromosome_vcf = self.metadata_gff3['gff3_to_vcf_chromosome_mapping'][ _chromosome_gff3 ]
            count_snps = self.gd.count_snps_in_window(_chromosome_vcf, row['start'], row['end'])
            return count_snps

        def count_gene_snps(row):
            _chromosome_gff3 = row['seqid']
            _chromosome_vcf = metadata_gff3['gff3_to_vcf_chromosome_mapping'][ _chromosome_gff3 ]
            count_snps = self.gd.count_snps_in_window(_chromosome_vcf, row['start'], row['end'])
            exons = self.genes.loc[(self.genes['Parent'] == row['ID']) & (self.genes['type'] == 'exon')]
            exons_counts = exons.apply(count_exon_snps, axis=1)
            return pd.Series( [count_snps, exons_counts.sum() ], index=['count_snps', 'count_exon_snps'])


        geneStatsCacheFilename = self.datadir+'____gene_stats_.hdf5'
        try:
            gene_list = pd.read_hdf(geneStatsCacheFilename, key='s')
            print("++++ Loaded Pandas Dataframe for gene stats")

            genes_counted_snps = gene_list[ ['count_snps', 'count_exon_snps'] ].copy()
            merged = pd.concat([genes_with_descriptions, genes_counted_snps], axis=1)
            gene_list = merged[ ['ID', 'seqid', 'start', 'end', 'primary_confidence_class', 'description', 'Ontology_term', 'count_snps', 'count_exon_snps'] ].copy()

        except FileNotFoundError:
            start = timer()
            genes_counted_snps = genes_with_descriptions.parallel_apply(count_gene_snps, axis=1, result_type='expand')
            print("==== genes_with_descriptions.parallel_apply() calculation time: ", timer() - start)

            merged = pd.concat([genes_with_descriptions, genes_counted_snps], axis=1)

            gene_list = merged[ ['ID', 'seqid', 'start', 'end', 'primary_confidence_class', 'description', 'count_snps', 'count_exon_snps'] ].copy()
            gene_list.to_hdf(geneStatsCacheFilename, key='s', mode='w', complevel=5, complib='blosc:zstd')


        genes_list = gene_list.to_dict('split')

        genes_grouped_by_seqid = genes_only.groupby(self.genes.seqid)
        list_chrom_gff3 = pd.unique(genes_only['seqid']).tolist()
        genes_start_positions = {}
        for _chr in list_chrom_gff3:
            _curr_group = genes_grouped_by_seqid.get_group(_chr)
            genes_start_positions[_chr] = pd.DataFrame(_curr_group['start'].drop_duplicates(keep='first'))
            genes_start_positions[_chr].set_index('start', drop=False, inplace=True)
            genes_start_positions[_chr] = genes_start_positions[_chr].sort_index()

        self.genes_list = genes_list
        self.genes_grouped_by_seqid = genes_grouped_by_seqid
        self.genes_start_positions = genes_start_positions


    def get_nearest_gene_start_pos(self, chrom, pos):
        seqid = self.chrom_gff3_map[chrom]
        nearest = self.genes_start_positions[seqid].index.get_loc(pos, method='nearest')
        start_pos = int(self.genes_start_positions[seqid].iloc[nearest].start)
        _genes = self.genes_grouped_by_seqid.get_group(seqid)
        return _genes.loc[(_genes['start'] == start_pos)]