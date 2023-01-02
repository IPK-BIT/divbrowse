from icecream import ic
import os
from timeit import default_timer as timer
from types import SimpleNamespace
from typing import Tuple
import json

import allel
import numpy as np
import pandas as pd
import zarr
from sklearn.decomposition import PCA
from sklearn.preprocessing import RobustScaler
import umap

from divbrowse import log
from divbrowse.lib.utils import ApiError
from divbrowse.lib.variant_calls_slice import VariantCallsSlice



class GenotypeData:
    """Class for managing all genotype data related data structures and methods"""

    def __init__(self, config):

        log.debug("GenotypeData::__init__()")

        self.config = config

        self.datadir = config['datadir']
        path_zarr_variants = self.datadir + config['variants']['zarr_dir']

        if not os.path.exists(self.datadir):
            exit('ERROR: the configured datadir does not exist or is not accessible')

        if not os.path.exists(path_zarr_variants):
            exit('ERROR: the configured path for the Zarr-archive of variants does not exist or is not accessible')

        log.debug("GenotypeData::zarr.open_group()")
        self.callset = zarr.open_group(path_zarr_variants, mode='r')
        log.debug(self.callset.tree(expand=True))

        self.available = {
            'snpeff': False,
            'sample_id_mapping': False
        }

        self._load_data()
        self._setup_sample_id_mapping()
        self._create_chrom_indices()
        self._create_list_of_chromosomes()
    

    def _load_data(self):

        self.available_calldata = list(self.callset['calldata'].array_keys())
        self.available_variants_metadata = list(self.callset['variants'].array_keys())

        # set some shortcut variables
        self.reference_allele = self.callset['variants/REF']
        self.alternate_alleles = self.callset['variants/ALT']
        self.variants_qual = self.callset['variants/QUAL']
        self.calldata = self.callset['calldata/GT']

        # convert chrom, pos and samples from zarr.core.Array to numpy ndarray
        self.chrom = self.callset['variants/CHROM'][:]
        self.pos = self.callset['variants/POS'][:]
        self.samples = self.callset['samples'][:]

        self.count_variants = len(self.pos)
        self.count_samples = len(self.samples)

        # infer the ploidy from the GT field
        self.ploidy = int(self.callset['calldata']['GT'].ndim) - 1

        # check if SnpEff annotation is included
        if 'ANN' in self.available_variants_metadata:
            self.available['snpeff'] = True

        # Derive distinct chromosome ID's from variant matrix
        self.list_chrom = pd.unique(self.chrom).tolist()

        # Create index for samples
        self.idx_samples = allel.UniqueIndex(self.samples)

        # Create combined index for variant positions
        self.idx_pos = allel.ChromPosIndex(self.chrom, self.pos)

        self.samples_dict = dict(zip(self.samples.tolist(), list(range(0, self.samples.shape[0]))))


    def get_vcf_header(self):
        vcf_header_lines = None
        self._vcf_header_lines_file = self.datadir + '____vcf_export_header_lines____.vcf'
        if os.path.exists(self._vcf_header_lines_file):
            with open(self._vcf_header_lines_file, 'r') as f:
                vcf_header_lines = f.read().splitlines()

        return vcf_header_lines


    def _setup_sample_id_mapping(self):

        if self.config['variants']['sample_id_mapping_filename']:
            self._path_sample_id_mapping = self.datadir + self.config['variants']['sample_id_mapping_filename']
            if os.path.exists(self._path_sample_id_mapping):
                self.available['sample_id_mapping'] = True
            else:
                exit('ERROR: the configured path for the Sample-ID-mapping does not exist or is not accessible')
        
        if self.available['sample_id_mapping']:
            df_sample_id_mapping = pd.read_csv(self._path_sample_id_mapping, header=None)
            self.map_input_sample_ids_to_vcf_sample_ids_dict = dict(zip(df_sample_id_mapping[0], df_sample_id_mapping[1]))
            self.map_vcf_sample_ids_to_input_sample_ids_dict = dict(zip(df_sample_id_mapping[1], df_sample_id_mapping[0]))



    def _create_chrom_indices(self):

        chrom_indices = {}
        for _chr in self.list_chrom:
            cached_index_path = self.datadir + '____pandas_index_chromosome_' + str(_chr) + '_.hdf5'
            try:
                chrom_indices[_chr] = pd.read_hdf(cached_index_path, key='s')
                log.debug("++++ Loaded Pandas index for chromosome %s", str(_chr))

            except FileNotFoundError:
                log.debug("++++ Creating Pandas index for chromosome %s", str(_chr))
                chrom_range = self.idx_pos.locate_key(_chr)
                chrom_indices[_chr] = pd.Series(data=np.arange(chrom_range.start, chrom_range.stop), index=self.pos[chrom_range])
                chrom_indices[_chr].to_hdf(cached_index_path, key='s', mode='w', complevel=5, complib='blosc:zstd')
        
        self.chrom_indices = chrom_indices



    def _create_list_of_chromosomes(self):

        chromosome_labels = {str(key): str(value) for key, value in self.config['chromosome_labels'].items()}
        centromeres_positions = {str(key): str(value) for key, value in self.config['centromeres_positions'].items()}

        path_chromosome_tmp_data = self.datadir+'____list_of_chromosomes____.json'

        try:
            with open(path_chromosome_tmp_data) as f:
                log.debug("++++ Load chromosome metadata from json on disk")
                self.list_of_chromosomes = json.loads(f.read())

        except FileNotFoundError:
            log.debug("++++ Need to create chromosome metadata on thy fly")
            self.list_of_chromosomes = []
            for _chr in self.list_chrom:
                _region = self.idx_pos.locate_range(_chr)
                self.list_of_chromosomes.append({
                    'id': _chr,
                    'label': chromosome_labels[str(_chr)],
                    'centromere_position': int(centromeres_positions[str(_chr)]),
                    'start': int(self.pos[ _region.start ]),
                    'end': int(self.pos[ _region.stop - 1 ]),
                    'number_of_variants': int(self.pos[_region].size)
                })
            with open(path_chromosome_tmp_data, 'w') as outfile:
                json.dump(self.list_of_chromosomes, outfile)


    def sample_ids_to_mask(self, sample_ids: list) -> np.ndarray:
        """Creates a boolean mask based on the input sample IDs that could be found in the samples array of the Zarr storage

        Args:
            sample_ids (list): List with sample IDs

        Returns:
            numpy.ndarray: Boolean mask, True for found sample IDs
        """

        samples_mask = np.zeros(self.samples.shape[0], dtype=bool)
        for sample_id in sample_ids:
            if sample_id in self.samples_dict:
                pos = self.samples_dict[sample_id]
                samples_mask[pos] = True

        return samples_mask


    def map_input_sample_ids_to_vcf_sample_ids(self, sample_ids: list) -> list:
        """Map input sample IDs to VCF sample IDs according to the configured mapping table

        Args:
            sample_ids (list): List with sample IDs

        Returns:
            list: List of mapped sample IDs
        """

        mapped_sample_ids = []
        unmapable_sample_ids = []

        if self.available['sample_id_mapping']:
            start = timer()
            mapped_sample_ids = [self.map_input_sample_ids_to_vcf_sample_ids_dict[id] for id in sample_ids if id in self.map_input_sample_ids_to_vcf_sample_ids_dict]
            unmapable_sample_ids = [id for id in sample_ids if id not in self.map_input_sample_ids_to_vcf_sample_ids_dict]
            log.debug(mapped_sample_ids)
            log.debug(unmapable_sample_ids)
            log.debug("==== map_input_sample_ids_to_vcf_sample_ids() calculation time: %f", timer() - start)
        else:
            mapped_sample_ids = [id for id in sample_ids if id in self.samples_dict]
            unmapable_sample_ids = [id for id in sample_ids if id not in self.samples_dict]

        return mapped_sample_ids, unmapable_sample_ids


    def map_vcf_sample_ids_to_input_sample_ids(self, sample_ids: list) -> list:
        """Map VCF sample IDs to input sample IDs according to the configured mapping table

        Args:
            sample_ids (list): List with sample IDs

        Returns:
            list: List of mapped sample IDs
        """
        
        mapped_sample_ids = []
        unmapable_sample_ids = []

        if self.available['sample_id_mapping']:
            start = timer()
            for input_sample_id in sample_ids:
                if input_sample_id in self.map_vcf_sample_ids_to_input_sample_ids_dict:
                    mapped_sample_ids.append(self.map_vcf_sample_ids_to_input_sample_ids_dict[input_sample_id])
                else:
                    unmapable_sample_ids.append(input_sample_id)
            log.debug("==== map_vcf_sample_ids_to_input_sample_ids() calculation time: %f", timer() - start)
        else:
            mapped_sample_ids = sample_ids

        return mapped_sample_ids, unmapable_sample_ids


    def get_samples_mask(self, sample_ids):
        """Returns a tupel consisting of a boolean mask for found sample Ids and a list of mapped sample IDs

        Args:
            sample_ids (list): List with sample IDs

        Returns:
            numpy.ndarray: Boolean mask, True for found sample IDs
            list: mapped sample IDs
        """

        try:
            samples_mask = self.sample_ids_to_mask(sample_ids)
            samples_mapped, unmapable_sample_ids = self.map_vcf_sample_ids_to_input_sample_ids(self.samples[samples_mask].tolist())
        except KeyError:
            raise ApiError('The following sample-IDs could not be resolved: '+', '.join(unmapable_sample_ids))

        return samples_mask, samples_mapped


    def get_posidx_by_genome_coordinate(self, chrom, pos, method='nearest') -> Tuple[int, str]:
        """Returns array coordinates for given physical position on a given chromosome

        Args:
            chrom (str): ID of the chromosome
            pos (int): Physical position on the chromosome

        Returns:
            lookup (int) Array coordinate of the found physical position on the chromosome
            lookup_type (str): Type of the lookup, could be either 'direct_lookup' or 'nearest_lookup'
        """
        
        pd_series = self.chrom_indices[chrom]
        try:
            lookup = pd_series.at[pos]
            return lookup, 'direct_lookup'
        except KeyError:
            # do fuzzy search via nearest neighbor search
            nearest = pd_series.index.get_indexer([pos], method=method)[0]
            lookup = pd_series.iloc[nearest]
            return lookup, 'nearest_lookup'



    def count_variants_in_window(self, chrom, startpos, endpos) -> int:
        """Counts number of variants in a genomic region

        Args:
            chrom (str): The chromosome of the genomic region.
            startpos (int): The first position of the genommic region.
            endpos (int): The last position of the genommic region.

        Returns:
            int: Number of variants in the genomic region

        """

        if startpos > endpos:
            startpos, endpos = endpos, startpos

        location_start, lookup_type_start = self.get_posidx_by_genome_coordinate(chrom, startpos)
        location_end, lookup_type_end = self.get_posidx_by_genome_coordinate(chrom, endpos)
        location_end = location_end + 1
        positions = self.pos[location_start:location_end]

        count = 0
        for i in range(positions.shape[0]):
            if positions[i] >= startpos and positions[i] <= endpos:
                count = count + 1
        
        return count



    def get_slice_of_variant_calls(
            self,
            chrom,
            startpos = None,
            endpos = None,
            count = None,
            samples = None,
            variant_filter_settings = None,
            with_call_metadata = False,
            flanking_region_include = False,
            flanking_region_length = 1500,
            flanking_region_direction = 'both'
        ) -> VariantCallsSlice:

        lookup_type_start = False
        lookup_type_end = False

        if samples is None:
            samples = self.samples

        samples_mask, samples_selected_mapped = self.get_samples_mask(samples)

        if count is None:

            if flanking_region_include:
                startpos = startpos - flanking_region_length
                endpos = endpos + flanking_region_length
                location_start, lookup_type_start = self.get_posidx_by_genome_coordinate(chrom, startpos, method='backfill')
                location_end, lookup_type_end = self.get_posidx_by_genome_coordinate(chrom, endpos, method='pad')

            else:
                location_start, lookup_type_start = self.get_posidx_by_genome_coordinate(chrom, startpos)
                location_end, lookup_type_end = self.get_posidx_by_genome_coordinate(chrom, endpos)
                location_end = location_end + 1
        else:
            if startpos is not None:
                # Get start coordinate (allows automatic position fuzzy search if coordinate does not exist in the variant matrix!)
                location_start, lookup_type_start = self.get_posidx_by_genome_coordinate(chrom, startpos)

                # calculate location_end from start and count
                location_end = location_start + count
                

            if endpos is not None:
                # Get start coordinate (allows automatic position fuzzy search if coordinate does not exist in the variant matrix!)
                location_end, lookup_type_end = self.get_posidx_by_genome_coordinate(chrom, endpos)
                location_end = location_end + 1

                # calculate location_start from end and count
                location_start = location_end - count

                if location_start < 0:
                    location_start = 0
                    location_end = location_start + count


        # create slice() object for later going into get_orthogonal_selection()
        slice_variant_calls = slice(location_start, location_end, None)

        positions = self.pos[slice_variant_calls]

        # get the variant slice from Zarr dataset
        sliced_variant_calls = self.calldata.get_orthogonal_selection((slice_variant_calls, samples_mask))


        metadata = {}
        if with_call_metadata:
            # get DP values
            if 'DP' in self.available_calldata:
                metadata['DP'] = {}
                sliced_DP = self.callset['calldata/DP'].get_orthogonal_selection((slice_variant_calls, samples_mask)).T
                i = 0
                for sample in samples_selected_mapped:
                    metadata['DP'][sample] = sliced_DP[i].tolist()
                    i += 1


            # get DV values
            if 'DV' in self.available_calldata:
                metadata['DV'] = {}
                sliced_DV = self.callset['calldata/DV'].get_orthogonal_selection((slice_variant_calls, samples_mask)).T
                i = 0
                for sample in samples_selected_mapped:
                    metadata['DV'][sample] = sliced_DV[i].tolist()
                    i += 1


        variant_calls_slice = VariantCallsSlice(
            gd = self,
            sliced_variant_calls = sliced_variant_calls,
            positions = positions,
            location_start = location_start,
            location_end = location_end,
            samples_mask = samples_mask,
            samples_selected_mapped = samples_selected_mapped,
            variant_filter_settings = variant_filter_settings,
            calls_metadata = metadata
        )

        return variant_calls_slice