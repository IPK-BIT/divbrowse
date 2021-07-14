import json
import os
from timeit import default_timer as timer
from types import SimpleNamespace
from typing import Tuple

import allel
import numpy as np
import pandas as pd
import zarr
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from lib.utils import ApiError


def calculate_mean(submatrix_of_snps: np.ndarray) -> np.ndarray:
    """Calculate the mean for each SNP of a SNP matrix array holding the number of alternate alleles

    Note:
        Missing SNP call are excluded from the mean calculation

    Args:
        submatrix_of_snps (numpy.ndarray): Numpy array representing a SNP matrix holding the number of alternate allele calls

    Returns:
        numpy.ndarray: Numpy array holding the means per SNP
    """

    submatrix_of_snps_missing_values_to_nan = np.where(submatrix_of_snps == -1, np.nan, submatrix_of_snps)
    return np.nanmean(submatrix_of_snps_missing_values_to_nan, axis=0) #, keepdims=True


def impute_with_mean(submatrix_of_snps: np.ndarray) -> np.ndarray:
    """SNP matrix array for that missing values should be imputed (replaced) with the mean for the SNP

    Args:
        submatrix_of_snps (numpy.ndarray): Numpy array representing a SNP matrix holding the number of alternate allele calls

    Returns:
        numpy.ndarray: Imputed version of the input SNP matrix array
    """

    imputed = np.copy(submatrix_of_snps).astype(np.float32)
    means = calculate_mean(submatrix_of_snps)
    indices_missing = np.where(submatrix_of_snps == -1)
    imputed[indices_missing] = np.take(means, indices_missing[1])
    imputed = np.nan_to_num(imputed)
    return imputed


def calculate_pca_in_snp_window(snps, samples_selected):
    """Calculate a PCA for a SNP matrix array

    Args:
        snps (numpy.ndarray): Numpy array representing a SNP matrix holding the number of alternate allele calls

    Returns:
        numpy.ndarray: PCA result aligned with the sample IDs in the first column
    """

    sample_ids = np.array(samples_selected).reshape((-1, 1)).copy()
    snps_imputed = impute_with_mean(snps)
    scaler = StandardScaler()
    snps_imputed_scaled = np.nan_to_num(scaler.fit_transform(snps_imputed))
    start = timer()
    pca_model = PCA(n_components=2, whiten=False, svd_solver='randomized', iterated_power=6).fit(snps_imputed_scaled)
    pca_result = pca_model.transform(snps_imputed_scaled)
    print("==== PCA calculation time: ", timer() - start)
    pca_result_combined = np.concatenate((sample_ids, pca_result), axis=1)
    return pca_result_combined




class GenotypeData:
    """Class for managing all genotype data related data structures and methods"""

    def __init__(self, config):

        self.config = config

        self.datadir = config['data']['datadir']
        path_zarr_variants = self.datadir + config['data']['zarr_variants']

        if not os.path.exists(self.datadir):
            exit('ERROR: the configured datadir does not exist or is not accessible')

        if not os.path.exists(path_zarr_variants):
            exit('ERROR: the configured path for the Zarr-archive of variants does not exist or is not accessible')

        self.callset = zarr.open_group(path_zarr_variants, mode='r')
        print(self.callset.tree(expand=True))

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

        # Derive distinct chromosome ID's from snp matrix
        self.list_chrom = pd.unique(self.chrom).tolist()

        # Create index for samples
        self.idx_samples = allel.UniqueIndex(self.samples)

        # Create combined index for snp positions
        self.idx_pos = allel.ChromPosIndex(self.chrom, self.pos)

        self.samples_dict = dict(zip(self.samples.tolist(), list(range(0, self.samples.shape[0]))))


    def _setup_sample_id_mapping(self):

        if self.config['data']['sample_id_mapping']:
            self._path_sample_id_mapping = self.datadir + self.config['data']['sample_id_mapping']
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
                print("++++ Loaded Pandas index for chromosome "+str(_chr))

            except FileNotFoundError:
                print("++++ Creating Pandas index for chromosome "+str(_chr))
                chrom_range = self.idx_pos.locate_key(_chr)
                chrom_indices[_chr] = pd.Series(data=np.arange(chrom_range.start, chrom_range.stop), index=self.pos[chrom_range])
                chrom_indices[_chr].to_hdf(cached_index_path, key='s', mode='w', complevel=5, complib='blosc:zstd')
        
        self.chrom_indices = chrom_indices



    def _create_list_of_chromosomes(self):

        chromosome_labels = self.config['chromosome_labels']
        centromeres_positions = self.config['centromeres_positions']
        path_chromosome_tmp_data = self.datadir+'____list_of_chromosomes____.json'

        try:
            with open(path_chromosome_tmp_data) as f:
                print("++++ Load chromosome metadata from json on disk")
                self.list_of_chromosomes = json.loads(f.read())

        except FileNotFoundError:
            print("++++ Need to create chromosome metadata on thy fly")
            self.list_of_chromosomes = []
            for _chr in self.list_chrom:
                #start = timer()
                _region = self.idx_pos.locate_range(_chr)
                #print("TIME MEASURE: _region = idx_pos.locate_range(_chr): ", timer() - start)
                self.list_of_chromosomes.append({
                    'id': _chr,
                    'label': chromosome_labels[str(_chr)],
                    'centromere_position': int(centromeres_positions[str(_chr)]),
                    'start': int(self.pos[ _region.start ]),
                    'end': int(self.pos[ _region.stop - 1 ]),
                    'count_snps': int(self.pos[_region].size)
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

        if self.available['sample_id_mapping']:
            start = timer()
            for input_sample_id in sample_ids:
                mapped_sample_ids.append( self.map_input_sample_ids_to_vcf_sample_ids_dict[input_sample_id] )
            print("==== map_input_sample_ids_to_vcf_sample_ids() calculation time: ", timer() - start)
        else:
            mapped_sample_ids = sample_ids

        return mapped_sample_ids


    def map_vcf_sample_ids_to_input_sample_ids(self, sample_ids: list) -> list:
        """Map VCF sample IDs to input sample IDs according to the configured mapping table

        Args:
            sample_ids (list): List with sample IDs

        Returns:
            list: List of mapped sample IDs
        """
        
        mapped_sample_ids = []

        if self.available['sample_id_mapping']:
            start = timer()
            for input_sample_id in sample_ids:
                mapped_sample_ids.append( self.map_vcf_sample_ids_to_input_sample_ids_dict[input_sample_id] )
            print("==== map_vcf_sample_ids_to_input_sample_ids() calculation time: ", timer() - start)
        else:
            mapped_sample_ids = sample_ids

        return sample_ids


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
            samples_mapped = self.map_vcf_sample_ids_to_input_sample_ids(self.samples[samples_mask].tolist())
        except KeyError:
            raise ApiError('At least one sample-ID is not included in the sample ID list of the SNP matrix.')

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
            #print("++++ direct lookup")
            return lookup, 'direct_lookup'
        except KeyError:
            # do fuzzy search via nearest neighbor search
            nearest = pd_series.index.get_loc(pos, method='nearest')
            lookup = pd_series.iloc[nearest]
            #print("++++ nearest lookup")
            return lookup, 'nearest_lookup'


    def get_snp_matrix(self, sliced_snps):
        """Returns a tupel consisting of a boolean mask for found sample Ids and a list of mapped sample IDs

        Args:
            sliced_snps (numpy.ndarray): SNP matrix array holding the allele calls (0/0  0/1  1/1)

        Returns:
            numpy.ndarray: SNP matrix array holding the number of alternate allele calls
        """

        print(type(sliced_snps))

        # monoploid / haploid
        if sliced_snps.ndim == 2:
            snps_to_alt = allel.HaplotypeArray(sliced_snps).T

        # diploid
        if sliced_snps.ndim == 3:
            # Transform each genotype call into the number of non-reference alleles and then transpose it via .T to row-major order
            snps_to_alt = allel.GenotypeArray(sliced_snps).to_n_alt(fill=-1).T

        return snps_to_alt


    def count_snps_in_window(self, chrom, startpos, endpos) -> int:
        """Counts number of SNPs in a genomic region

        Args:
            chrom (str): The chromosome of the genomic region.
            startpos (int): The first position of the genommic region.
            endpos (int): The last position of the genommic region.

        Returns:
            int: Number of SNPs in the genomic region

        """

        location_start, lookup_type_start = self.get_posidx_by_genome_coordinate(chrom, startpos)
        location_end, lookup_type_end = self.get_posidx_by_genome_coordinate(chrom, endpos)
        location_end = location_end + 1
        positions = self.pos[location_start:location_end]

        count = 0
        for i in range(positions.shape[0]):
            if positions[i] >= startpos and positions[i] <= endpos:
                count = count + 1
        
        return count


    def calculate_minor_allele_freq(self, submatrix_of_snps):
        """Calculates minor allele frequency

        Args:
            submatrix_of_snps (numpy.ndarray): Numpy array representing a SNP matrix holding the number of alternate allele calls

        Returns:
            numpy.ndarray: Numpy array (1d) holding the calculated minor allele frequencies per each SNP
        """

        if self.ploidy == 1:
            means = calculate_mean(submatrix_of_snps)
            maf = np.where(means < 0.5, means, 1 - means)
            return np.nan_to_num(maf, nan=-1).tolist()

        if self.ploidy == 2:
            means_halfed = calculate_mean(submatrix_of_snps) / 2
            maf = np.where(means_halfed < 0.5, means_halfed, 1 - means_halfed)
            return np.nan_to_num(maf, nan=-1).tolist()


    def calculate_per_snp_stats(self, submatrix_of_snps):    
        result = {}

        result['maf'] = self.calculate_minor_allele_freq(submatrix_of_snps)

        df_snps = pd.DataFrame(submatrix_of_snps)
        counts = df_snps.apply(pd.Series.value_counts, axis=0, normalize=True).fillna(0)
        result['missing_freq'] = counts.loc[-1].values.tolist()

        df_snps_with_nan = df_snps.replace(-1, np.nan)
        counts_without_missing = df_snps_with_nan.apply(pd.Series.value_counts, axis=0, normalize=True, dropna=True).fillna(0)
        counts_without_missing.index = counts_without_missing.index.astype(int, copy=False)
        result['heterozygosity_freq'] = counts_without_missing.loc[1].values.tolist()

        return result


    def apply_variant_filter_settings(self, fs, snps_to_alt, _slice_snps):
        per_snp_stats = self.calculate_per_snp_stats(snps_to_alt)

        #### QUAL #########################
        if 'QUAL' in self.available_variants_metadata:
            sliced_qual = self.variants_qual.get_basic_selection(_slice_snps)
            per_snp_stats['vcf_qual'] = sliced_qual.tolist()
        
        per_snp_stats['positions_indices'] = list(range(_slice_snps.start, _slice_snps.stop))
        df = pd.DataFrame(per_snp_stats)

        print(df)

        if 'filterByMaf' in fs and fs['filterByMaf'] == True:
            df = df[ df['maf'].between(fs['maf'][0], fs['maf'][1]) ]

        if 'filterByMissingFreq' in fs and fs['filterByMissingFreq'] == True:
            df = df[ df['missing_freq'].between(fs['missingFreq'][0], fs['missingFreq'][1]) ]

        if 'filterByHeteroFreq' in fs and fs['filterByHeteroFreq'] == True:
            df = df[ df['heterozygosity_freq'].between(fs['heteroFreq'][0], fs['heteroFreq'][1]) ]

        if 'filterByVcfQual' in fs and fs['filterByVcfQual'] == True and 'QUAL' in self.available_variants_metadata:
            df = df[ df['vcf_qual'].between(fs['vcfQual'][0], fs['vcfQual'][1]) ]

        if snps_to_alt[:, df.index.values].shape[1] >= 2:
            snps_to_alt = snps_to_alt[:, df.index.values]

        return snps_to_alt, df['positions_indices'].values


    def get_slice_of_snps(self, chrom, startpos=None, endpos=None, count=None, samples=None, variant_filter_settings=None):

        lookup_type_start = False
        lookup_type_end = False

        samples_mask, samples_selected_mapped = self.get_samples_mask(samples)

        if count is None:
            location_start, lookup_type_start = self.get_posidx_by_genome_coordinate(chrom, startpos)
            location_end, lookup_type_end = self.get_posidx_by_genome_coordinate(chrom, endpos)
            location_end = location_end + 1
        else:
            if startpos is not None:
                # Get start coordinate (allows automatic position fuzzy search if coordinate does not exist in the SNP matrix!)
                location_start, lookup_type_start = self.get_posidx_by_genome_coordinate(chrom, startpos)

                # calculate location_end from start and count
                location_end = location_start + count
                

            if endpos is not None:
                # Get start coordinate (allows automatic position fuzzy search if coordinate does not exist in the SNP matrix!)
                location_end, lookup_type_end = self.get_posidx_by_genome_coordinate(chrom, endpos)
                location_end = location_end + 1

                # calculate location_start from end and count
                location_start = location_end - count

                if location_start < 0:
                    location_start = 0
                    location_end = location_start + count


        # create slice() object for later going into get_orthogonal_selection()
        slice_snps = slice(location_start, location_end, None)

        positions = self.pos[slice_snps]

        # get the SNP slice from Zarr dataset
        sliced_snps = self.calldata.get_orthogonal_selection((slice_snps, samples_mask))   # samples_mask

        # Transform each genotype call into the number of non-reference alleles and then transpose it via .T to row-major order
        snps_to_alt = self.get_snp_matrix(sliced_snps)

        filtered_positions_indices = np.asarray(range(slice_snps.start, slice_snps.stop)) #None
        if variant_filter_settings is not None:
            snps_to_alt, filtered_positions_indices = self.apply_variant_filter_settings(variant_filter_settings, snps_to_alt, slice_snps)

        stats = {
            'count_snps_in_window': int(positions.shape[0]),
            'count_snps_in_window_filtered': int(snps_to_alt.shape[1]),
            'startpos': int(positions[0]),
            'endpos': int(positions[-1]),
            'lookup_type_start': str(lookup_type_start),
            'lookup_type_end': str(lookup_type_end)
        }

        result = {
            'snps_to_alt': snps_to_alt,
            'slice_snps': slice_snps,
            'sliced_snps': sliced_snps,
            'samples_mask': samples_mask,
            'samples_selected_mapped': samples_selected_mapped,
            'positions': positions,
            'filtered_positions_indices': filtered_positions_indices,
            'location_start': location_start,
            'location_end': location_end,
            'stats': stats
        }

        return SimpleNamespace(**result)
