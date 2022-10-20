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


def calculate_mean(slice_of_variant_calls: np.ndarray) -> np.ndarray:
    """Calculate the mean for each variant of a variant matrix array holding the number of alternate alleles

    Note:
        Missing variant calls are excluded from the mean calculation

    Args:
        slice_of_variant_calls (numpy.ndarray): Numpy array representing a variant matrix holding the number of alternate allele calls

    Returns:
        numpy.ndarray: Numpy array holding the means per variant
    """

    slice_of_variant_calls_missing_values_to_nan = np.where(slice_of_variant_calls == -1, np.nan, slice_of_variant_calls)
    return np.nanmean(slice_of_variant_calls_missing_values_to_nan, axis=0) #, keepdims=True


def impute_with_mean(slice_of_variant_calls: np.ndarray) -> np.ndarray:
    """variant matrix array for that missing values should be imputed (replaced) with the mean for the variant

    Args:
        slice_of_variant_calls (numpy.ndarray): Numpy array representing a variant matrix holding the number of alternate allele calls

    Returns:
        numpy.ndarray: Imputed version of the input variant matrix array
    """

    imputed = np.copy(slice_of_variant_calls).astype(np.float32)
    means = calculate_mean(slice_of_variant_calls)
    indices_missing = np.where(slice_of_variant_calls == -1)
    imputed[indices_missing] = np.take(means, indices_missing[1])
    imputed = np.nan_to_num(imputed)
    return imputed


def calc_pca_for_slice_of_variant_calls(slice_of_variant_calls, samples_selected):
    """Calculate a PCA for a variant matrix array

    Args:
        slice_of_variant_calls (numpy.ndarray): Numpy array representing a variant matrix holding the number of alternate allele calls

    Returns:
        numpy.ndarray: PCA result aligned with the sample IDs in the first column
    """

    sample_ids = np.array(samples_selected).reshape((-1, 1)).copy()
    calls_imputed = impute_with_mean(slice_of_variant_calls)
    scaler = RobustScaler()
    calls_imputed_scaled = np.nan_to_num(scaler.fit_transform(calls_imputed))
    start = timer()

    n_components = 10
    if calls_imputed_scaled.shape[1] < n_components:
        n_components = calls_imputed_scaled.shape[1]

    try:
        pca_model = PCA(n_components=n_components, whiten=False, svd_solver='randomized', iterated_power=6).fit(calls_imputed_scaled)
        pca_result = pca_model.transform(calls_imputed_scaled)
        log.debug("==== PCA calculation time: %f", timer() - start)
        pca_result_combined = np.concatenate((sample_ids, pca_result), axis=1)
        return pca_result_combined, pca_model.explained_variance_ratio_

    except ValueError:
        return False




def calc_umap_for_slice_of_variant_calls(slice_of_variant_calls, samples_selected, n_neighbors=15):
    """Calculate UMAP for a variant matrix array

    Args:
        slice_of_variant_calls (numpy.ndarray): Numpy array representing a variant matrix holding the number of alternate allele calls

    Returns:
        numpy.ndarray: PCA result aligned with the sample IDs in the first column
    """

    sample_ids = np.array(samples_selected).reshape((-1, 1)).copy()
    calls_imputed = impute_with_mean(slice_of_variant_calls)

    #start = timer()
    #pca_model = PCA(n_components=2, whiten=False, svd_solver='randomized', iterated_power=6).fit(calls_imputed_scaled)
    #pca_result = pca_model.transform(calls_imputed_scaled)
    #log.debug("==== PCA calculation time: %f", timer() - start)
    #pca_result_combined = np.concatenate((sample_ids, pca_result), axis=1)
    #return pca_result_combined

    start = timer()
    umap_result = umap.UMAP(n_components = 2, n_neighbors=n_neighbors, metric='euclidean', random_state=42).fit_transform(calls_imputed) # , random_state=42, densmap=True  , min_dist=0.5   , dens_lambda=5
    log.debug("==== UMAP calculation time: %f", timer() - start)
    umap_result_combined = np.concatenate((sample_ids, umap_result), axis=1)
    return umap_result_combined




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
            for input_sample_id in sample_ids:
                if input_sample_id in self.map_input_sample_ids_to_vcf_sample_ids_dict:
                    mapped_sample_ids.append( self.map_input_sample_ids_to_vcf_sample_ids_dict[input_sample_id] )
                else:
                    unmapable_sample_ids.append(input_sample_id)
            log.debug("==== map_input_sample_ids_to_vcf_sample_ids() calculation time: %f", timer() - start)
        else:
            #mapped_sample_ids = sample_ids
            for input_sample_id in sample_ids:
                if input_sample_id in self.samples_dict:
                    mapped_sample_ids.append(input_sample_id)
                else:
                    unmapable_sample_ids.append(input_sample_id)

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


    def get_posidx_by_genome_coordinate(self, chrom, pos) -> Tuple[int, str]:
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
            nearest = pd_series.index.get_indexer([pos], method='nearest')[0]
            lookup = pd_series.iloc[nearest]
            return lookup, 'nearest_lookup'


    def count_alternate_alleles(self, sliced_variant_calls):
        """Returns a tupel consisting of a boolean mask for found sample Ids and a list of mapped sample IDs

        Args:
            sliced_variant_calls (numpy.ndarray): variant matrix array holding the allele calls (0/0  0/1  1/1)

        Returns:
            numpy.ndarray: variant matrix array holding the number of alternate allele calls
        """

        # monoploid / haploid
        if sliced_variant_calls.ndim == 2:
            numbers_of_alternate_alleles = allel.HaplotypeArray(sliced_variant_calls).T

        # diploid
        if sliced_variant_calls.ndim == 3:
            # Transform each genotype call into the number of non-reference alleles and then transpose it via .T to row-major order
            numbers_of_alternate_alleles = allel.GenotypeArray(sliced_variant_calls).to_n_alt(fill=-1).T

        return numbers_of_alternate_alleles


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


    def calculate_minor_allele_freq(self, numbers_of_alternate_alleles):
        """Calculates minor allele frequency

        Args:
            numbers_of_alternate_alleles (numpy.ndarray): Numpy array representing a variant matrix holding the number of alternate allele calls

        Returns:
            numpy.ndarray: Numpy array (1d) holding the calculated minor allele frequencies per each variant
        """

        if self.ploidy == 1:
            means = calculate_mean(numbers_of_alternate_alleles)
            maf = np.where(means < 0.5, means, 1 - means)
            return np.nan_to_num(maf, nan=-1).tolist()

        if self.ploidy == 2:
            means_halfed = calculate_mean(numbers_of_alternate_alleles) / 2
            maf = np.where(means_halfed < 0.5, means_halfed, 1 - means_halfed)
            return np.nan_to_num(maf, nan=-1).tolist()


    def calc_variants_summary_stats(self, numbers_of_alternate_alleles):    
        result = {}

        result['maf'] = self.calculate_minor_allele_freq(numbers_of_alternate_alleles)

        df_numbers_of_alternate_alleles = pd.DataFrame(numbers_of_alternate_alleles)
        counts = df_numbers_of_alternate_alleles.apply(pd.Series.value_counts, axis=0, normalize=True).fillna(0)

        try:
            result['missing_freq'] = counts.loc[-1].values.tolist()
        except KeyError:
            result['missing_freq'] = np.zeros(counts.columns.size).tolist()

        df_numbers_of_alternate_alleles_with_nan = df_numbers_of_alternate_alleles.replace(-1, np.nan)
        counts_without_missing = df_numbers_of_alternate_alleles_with_nan.apply(pd.Series.value_counts, axis=0, normalize=True, dropna=True).fillna(0)
        counts_without_missing.index = counts_without_missing.index.astype(int, copy=False)

        try:
            result['heterozygosity_freq'] = counts_without_missing.loc[1].values.tolist()
        except KeyError:
            result['heterozygosity_freq'] = np.zeros(counts_without_missing.columns.size).tolist()

        return result


    def apply_variant_filter_settings(self, fs, numbers_of_alternate_alleles, _slice_variant_calls):
        variants_summary_stats = self.calc_variants_summary_stats(numbers_of_alternate_alleles)

        if 'QUAL' in self.available_variants_metadata:
            sliced_qual = self.variants_qual.get_basic_selection(_slice_variant_calls)
            variants_summary_stats['vcf_qual'] = sliced_qual.tolist()
        
        variants_summary_stats['positions_indices'] = list(range(_slice_variant_calls.start, _slice_variant_calls.stop))
        df = pd.DataFrame(variants_summary_stats)

        log.debug(df)

        if 'filterByMaf' in fs and fs['filterByMaf'] == True:
            df = df[ df['maf'].between(fs['maf'][0], fs['maf'][1]) ]

        if 'filterByMissingFreq' in fs and fs['filterByMissingFreq'] == True:
            df = df[ df['missing_freq'].between(fs['missingFreq'][0], fs['missingFreq'][1]) ]

        if 'filterByHeteroFreq' in fs and fs['filterByHeteroFreq'] == True:
            df = df[ df['heterozygosity_freq'].between(fs['heteroFreq'][0], fs['heteroFreq'][1]) ]

        if 'filterByVcfQual' in fs and fs['filterByVcfQual'] == True and 'QUAL' in self.available_variants_metadata:
            df = df[ df['vcf_qual'].between(fs['vcfQual'][0], fs['vcfQual'][1]) ]

        if numbers_of_alternate_alleles[:, df.index.values].shape[1] >= 2:
            numbers_of_alternate_alleles = numbers_of_alternate_alleles[:, df.index.values]

        return numbers_of_alternate_alleles, df['positions_indices'].values


    def get_slice_of_variant_calls(self, chrom, startpos=None, endpos=None, count=None, samples=None, variant_filter_settings=None):

        lookup_type_start = False
        lookup_type_end = False

        samples_mask, samples_selected_mapped = self.get_samples_mask(samples)

        if count is None:
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
        sliced_variant_calls = self.calldata.get_orthogonal_selection((slice_variant_calls, samples_mask))   # samples_mask

        # Transform each genotype call into the number of non-reference alleles and then transpose it via .T to row-major order
        numbers_of_alternate_alleles = self.count_alternate_alleles(sliced_variant_calls)

        filtered_positions_indices = np.asarray(range(slice_variant_calls.start, slice_variant_calls.stop)) #None
        if variant_filter_settings is not None:
            numbers_of_alternate_alleles, filtered_positions_indices = self.apply_variant_filter_settings(variant_filter_settings, numbers_of_alternate_alleles, slice_variant_calls)

        stats = {
            'number_of_variants_in_window': int(positions.shape[0]),
            'number_of_variants_in_window_filtered': int(numbers_of_alternate_alleles.shape[1]),
            'startpos': int(positions[0]),
            'endpos': int(positions[-1]),
            'lookup_type_start': str(lookup_type_start),
            'lookup_type_end': str(lookup_type_end)
        }

        result = {
            'numbers_of_alternate_alleles': numbers_of_alternate_alleles,
            'slice_variant_calls': slice_variant_calls,
            'sliced_variant_calls': sliced_variant_calls,
            'samples_mask': samples_mask,
            'samples_selected_mapped': samples_selected_mapped,
            'positions': positions,
            'filtered_positions_indices': filtered_positions_indices,
            'location_start': location_start,
            'location_end': location_end,
            'stats': stats
        }

        return SimpleNamespace(**result)
