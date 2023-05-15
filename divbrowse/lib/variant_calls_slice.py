from dataclasses import dataclass
from icecream import ic
import allel
import numpy as np
import pandas as pd
#import modin.pandas as modinpd

from timeit import default_timer as timer
from divbrowse import log


def with_gd():
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            func.__globals__['gd'] = self.gd
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


@dataclass
class VariantCallsSlice:

    gd: 'GenotypeData' = None
    type_of_slice: str = 'range'
    positional_lookup_success: bool = True
    sliced_variant_calls: np.ndarray = None
    positions: np.ndarray = None
    positions_indices: np.ndarray = None
    positions_not_found: np.ndarray = None
    location_start: int = None
    location_end: int = None
    samples_mask: np.ndarray = None
    samples_selected_mapped: list = None
    variant_filter_settings: dict = None
    calls_metadata: dict = None
    calc_summary_stats: bool = False


    def __post_init__(self):
        self.slice_variant_calls = slice(self.location_start, self.location_end, None)

        self.ploidy = int(self.sliced_variant_calls.ndim) - 1

        start = timer()
        self.count_alternate_alleles()
        log.debug("//////////////// __post_init__ count_alternate_alleles => %f", timer() - start)

        if self.calc_summary_stats and self.positions_not_found is None: # if self.positions_not_found is not None:
            start = timer()
            #self.calc_variants_summary_stats_numpy()
            self.calc_variants_summary_stats_scikitallel()
            log.debug("//////////////// __post_init__ calc_variants_summary_stats_scikitallel => %f", timer() - start)

        start = timer()
        self.apply_variant_filter_settings()
        log.debug("//////////////// __post_init__ apply_variant_filter_settings => %f", timer() - start)

        start = timer()
        self.add_stats()
        log.debug("//////////////// __post_init__ add_stats => %f", timer() - start)


    @staticmethod
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



    def count_alternate_alleles(self):
        """Returns a tupel consisting of a boolean mask for found sample Ids and a list of mapped sample IDs

        Args:
            sliced_variant_calls (numpy.ndarray): variant matrix array holding the allele calls (0/0  0/1  1/1)

        Returns:
            numpy.ndarray: variant matrix array holding the number of alternate allele calls
        """

        self.numbers_of_alternate_alleles = None

        # monoploid / haploid
        if self.sliced_variant_calls.ndim == 2:
            self.numbers_of_alternate_alleles = allel.HaplotypeArray(self.sliced_variant_calls).T

        # diploid
        if self.sliced_variant_calls.ndim == 3:
            # Transform each genotype call into the number of non-reference alleles and then transpose it via .T to row-major order
            self.numbers_of_alternate_alleles = allel.GenotypeArray(self.sliced_variant_calls).to_n_alt(fill=-1).T



    def calculate_minor_allele_freq(self):
        """Calculates minor allele frequency

        Returns:
            numpy.ndarray: Numpy array (1d) holding the calculated minor allele frequencies per each variant
        """

        if self.ploidy == 1:
            means = VariantCallsSlice.calculate_mean(self.numbers_of_alternate_alleles)
            maf = np.where(means < 0.5, means, 1 - means)
            return np.nan_to_num(maf, nan=-1).tolist()

        if self.ploidy == 2:
            means_halfed = VariantCallsSlice.calculate_mean(self.numbers_of_alternate_alleles) / 2
            maf = np.where(means_halfed < 0.5, means_halfed, 1 - means_halfed)
            return np.nan_to_num(maf, nan=-1).tolist()




    def calc_variants_summary_stats(self):    
        result = {}

        start = timer()
        result['maf'] = self.calculate_minor_allele_freq()
        log.debug("//////////////////////// calc_variants_summary_stats::calculate_minor_allele_freq => %f", timer() - start)

        start = timer()
        df_numbers_of_alternate_alleles = pd.DataFrame(self.numbers_of_alternate_alleles)
        ####np.save('_______testdata_numbers_of_alternate_alleles_______.npy', self.numbers_of_alternate_alleles)
        #ic(df_numbers_of_alternate_alleles.shape)
        counts = df_numbers_of_alternate_alleles.apply(pd.Series.value_counts, axis=0, normalize=True).fillna(0)
        #ic(counts.head())
        log.debug("//////////////////////// df_numbers_of_alternate_alleles.apply(pd.Series.value_counts) => %f", timer() - start)

        try:
            result['missing_freq'] = counts.loc[-1].values.tolist()
        except KeyError:
            result['missing_freq'] = np.zeros(counts.columns.size).tolist()

        df_numbers_of_alternate_alleles_with_nan = df_numbers_of_alternate_alleles.replace(-1, np.nan)
        #ic(df_numbers_of_alternate_alleles_with_nan.shape)
        counts_without_missing = df_numbers_of_alternate_alleles_with_nan.apply(pd.Series.value_counts, axis=0, normalize=True, dropna=True).fillna(0)
        counts_without_missing.index = counts_without_missing.index.astype(int, copy=False)

        try:
            result['heterozygosity_freq'] = counts_without_missing.loc[1].values.tolist()
        except KeyError:
            result['heterozygosity_freq'] = np.zeros(counts_without_missing.columns.size).tolist()

        #ga = allel.GenotypeArray(self.sliced_variant_calls)
        #ac = ga.count_alleles()
        #result['mean_pairwise_difference'] = allel.mean_pairwise_difference(ac).tolist()

        #pi = allel.sequence_diversity(self.positions, ac)
        #ic(pi)

        #rogers_huff_r = allel.rogers_huff_r(self.numbers_of_alternate_alleles)
        #ic(rogers_huff_r)
        #ic(rogers_huff_r.shape)

        self.variants_summary_stats = result

        return result


    def calc_variants_summary_stats_numpy(self):
        ###_calls = allel.GenotypeArray(self.sliced_variant_calls);
        ###np.save('_______testdata_sliced_variant_calls_______.npy', self.sliced_variant_calls)
        
        result = {}
        result['maf'] = self.calculate_minor_allele_freq()

        A = {-1: 0, 0: 0, 1: 0, 2: 0}
        num_samples = self.numbers_of_alternate_alleles.shape[0]

        def unique(arr):
            values, counts = np.unique(arr, return_counts=True)
            B = dict(zip(values, counts))
            result = { k: A.get(k,0) + B.get(k,0) for k in list(B.keys()) + list(A.keys()) }
            return result

        _counts = np.apply_along_axis(func1d=unique, axis=0, arr=self.numbers_of_alternate_alleles)
        counts = pd.DataFrame.from_records(_counts).T
        
        result['missing_freq'] = (counts.loc[-1].values / num_samples).tolist()
        counts_without_missing = num_samples - counts.loc[-1].values
        result['heterozygosity_freq'] = (counts.loc[1].values / counts_without_missing).tolist()

        self.variants_summary_stats = result

        return result


    def calc_variants_summary_stats_scikitallel(self):
        result = {}
        result['maf'] = self.calculate_minor_allele_freq()

        num_samples = self.sliced_variant_calls.shape[1]
        g = allel.GenotypeArray(self.sliced_variant_calls)
        
        miss = g.count_missing(axis=1)
        #print(miss)
        #print(miss.shape)
        result['missing_freq'] = (miss / num_samples).tolist()

        called = g.count_called(axis=1)
        #print(called)
        #print(called.shape)

        het = g.count_het(axis=1)
        #print(het)
        #print(het.shape)

        het_freq = het / called
        #print(het_freq)
        result['heterozygosity_freq'] = het_freq.tolist()

        self.variants_summary_stats = result

        return result


    @with_gd()
    def apply_variant_filter_settings(self):

        self.filtered_positions_indices = self.positions_indices

        if self.variant_filter_settings is None:
            return False

        fs = self.variant_filter_settings

        if 'QUAL' in gd.available_variants_metadata:
            sliced_qual = gd.variants_qual.get_coordinate_selection(self.positions_indices)
            self.variants_summary_stats['vcf_qual'] = sliced_qual.tolist()
        
        #self.variants_summary_stats['positions_indices'] = list(range(0, self.positions_indices.shape[0]))
        self.variants_summary_stats['positions_indices'] = self.positions_indices.tolist()
        df = pd.DataFrame(self.variants_summary_stats)

        log.debug(df)

        if 'filterByMaf' in fs and fs['filterByMaf'] == True:
            df = df[ df['maf'].between(fs['maf'][0], fs['maf'][1]) ]

        if 'filterByMissingFreq' in fs and fs['filterByMissingFreq'] == True:
            df = df[ df['missing_freq'].between(fs['missingFreq'][0], fs['missingFreq'][1]) ]

        if 'filterByHeteroFreq' in fs and fs['filterByHeteroFreq'] == True:
            df = df[ df['heterozygosity_freq'].between(fs['heteroFreq'][0], fs['heteroFreq'][1]) ]

        if 'filterByVcfQual' in fs and fs['filterByVcfQual'] == True and 'QUAL' in gd.available_variants_metadata:
            df = df[ df['vcf_qual'].between(fs['vcfQual'][0], fs['vcfQual'][1]) ]

        if self.numbers_of_alternate_alleles[:, df.index.values].shape[1] > 0:
            self.numbers_of_alternate_alleles = self.numbers_of_alternate_alleles[:, df.index.values]

        log.debug(df)
        self.filtered_positions_indices = df['positions_indices'].values

        return self.numbers_of_alternate_alleles, df['positions_indices'].values



    def add_stats(self):
        self.number_of_variants_in_window = int(self.positions.shape[0])
        self.number_of_variants_in_window_filtered = int(self.numbers_of_alternate_alleles.shape[1])
        self.startpos = int(self.positions[0])
        self.endpos = int(self.positions[-1])


    def get_stats_dict(self):
        result = {
            'number_of_variants_in_window': self.number_of_variants_in_window,
            'number_of_variants_in_window_filtered': self.number_of_variants_in_window_filtered,
            'startpos': self.startpos,
            'endpos': self.endpos,
            'type_of_slice': self.type_of_slice
        }

        if self.type_of_slice == 'positions':
            result['positions'] = self.positions.tolist()
            if self.positions_not_found is not None:
                result['positions_not_found'] = self.positions_not_found.tolist()

        return result


    def get_data(self):

        result = {
            'numbers_of_alternate_alleles': self.numbers_of_alternate_alleles,
            'slice_variant_calls': self.slice_variant_calls,
            'sliced_variant_calls': self.sliced_variant_calls,
            'samples_mask': self.samples_mask,
            'samples_selected_mapped': self.samples_selected_mapped,
            'positions': self.positions,
            'filtered_positions_indices': self.filtered_positions_indices,
            'location_start': self.location_start,
            'location_end': self.location_end
        }

        return result