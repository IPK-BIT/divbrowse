from icecream import ic
from timeit import default_timer as timer

import numpy as np

from sklearn.decomposition import PCA
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import pairwise_distances
import umap

from divbrowse import log
from divbrowse.lib.variant_calls_slice import VariantCallsSlice



def calculate_mean(sliced_variant_calls: np.ndarray) -> np.ndarray:
    """Calculate the mean for each variant of a variant matrix array holding the number of alternate alleles

    Note:
        Missing variant calls are excluded from the mean calculation

    Args:
        sliced_variant_calls (numpy.ndarray): Numpy array representing a variant matrix holding the number of alternate allele calls

    Returns:
        numpy.ndarray: Numpy array holding the means per variant
    """

    sliced_variant_calls_missing_values_to_nan = np.where(sliced_variant_calls == -1, np.nan, sliced_variant_calls)
    return np.nanmean(sliced_variant_calls_missing_values_to_nan, axis=0) #, keepdims=True


def impute_with_mean(sliced_variant_calls: np.ndarray) -> np.ndarray:
    """variant matrix array for that missing values should be imputed (replaced) with the mean for the variant

    Args:
        sliced_variant_calls (numpy.ndarray): Numpy array representing a variant matrix holding the number of alternate allele calls

    Returns:
        numpy.ndarray: Imputed version of the input variant matrix array
    """

    imputed = np.copy(sliced_variant_calls).astype(np.float32)
    means = calculate_mean(sliced_variant_calls)
    indices_missing = np.where(sliced_variant_calls == -1)
    imputed[indices_missing] = np.take(means, indices_missing[1])
    imputed = np.nan_to_num(imputed)
    return imputed



class Analysis:

    def __init__(self, variant_calls_slice: VariantCallsSlice):
        self.variant_calls_slice = variant_calls_slice # self.variant_calls_slice.samples_selected_mapped
        self.imputed_calls = None


    def get_imputed_calls(self):
        if self.imputed_calls is None:
            self.imputed_calls = impute_with_mean(self.variant_calls_slice.numbers_of_alternate_alleles)
        
        return self.imputed_calls


    def calc_distance_to_reference(self, samples):

        calls_imputed = self.get_imputed_calls()

        ref_vec = np.zeros(self.variant_calls_slice.numbers_of_alternate_alleles.shape[1]).reshape(1, self.variant_calls_slice.numbers_of_alternate_alleles.shape[1])

        start = timer()
        distances = pairwise_distances(calls_imputed, ref_vec, n_jobs=1, metric='hamming')
        distances = distances * self.variant_calls_slice.numbers_of_alternate_alleles.shape[1]
        distances = distances.astype(np.int16);
        sample_ids = np.array(self.variant_calls_slice.samples_selected_mapped).reshape(samples[self.variant_calls_slice.samples_mask].shape[0], 1)
        distances_combined = np.concatenate((sample_ids, distances), axis=1)
        log.debug("==== pairwise_distances() calculation time: %f", timer() - start)
        return distances_combined

    
    def calc_distance_matrix(self, samples):
        calls_imputed = self.get_imputed_calls()

        start = timer()
        distances = pairwise_distances(calls_imputed, n_jobs=4, metric='hamming')
        distances = distances * self.variant_calls_slice.numbers_of_alternate_alleles.shape[1]
        distances = distances.astype(np.int16);
        #sample_ids = np.array(self.variant_calls_slice.samples_selected_mapped).reshape(samples[self.variant_calls_slice.samples_mask].shape[0], 1)
        #distances_combined = np.concatenate((sample_ids, distances), axis=1)
        #log.debug("==== pairwise_distances() calculation time: %f", timer() - start)
        #return distances_combined
        return distances


    def pca(self):
        """Calculate a PCA for a variant matrix array

        Args:
            slice_of_variant_calls (numpy.ndarray): Numpy array representing a variant matrix holding the number of alternate allele calls

        Returns:
            numpy.ndarray: PCA result aligned with the sample IDs in the first column
        """

        sample_ids = np.array(self.variant_calls_slice.samples_selected_mapped).reshape((-1, 1)).copy()
        #calls_imputed = impute_with_mean(self.variant_calls_slice.numbers_of_alternate_alleles)
        calls_imputed = self.get_imputed_calls()
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


    def umap(self, n_neighbors=15):
        """Calculate UMAP for a variant matrix array

        Args:
            n_neighbors (int): `n_neighbors` parameter of umap.UMAP() method

        Returns:
            numpy.ndarray: PCA result aligned with the sample IDs in the first column
        """

        sample_ids = np.array(self.variant_calls_slice.samples_selected_mapped).reshape((-1, 1)).copy()
        #calls_imputed = impute_with_mean(self.variant_calls_slice.numbers_of_alternate_alleles)
        calls_imputed = self.get_imputed_calls()

        start = timer()
        umap_result = umap.UMAP(n_components = 2, n_neighbors=n_neighbors, metric='euclidean', random_state=42).fit_transform(calls_imputed) # , random_state=42, densmap=True  , min_dist=0.5   , dens_lambda=5
        log.debug("==== UMAP calculation time: %f", timer() - start)
        umap_result_combined = np.concatenate((sample_ids, umap_result), axis=1)
        return umap_result_combined