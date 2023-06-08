import math
import numpy as np
#from icecream import ic

class BrapiAllelematrix():

    def __init__(self, gd, request):

        self.gd = gd
        self.request = request

        self.status_messages = []
        self.data_matrices = []

        self._parse_request(request)
        self._count_variants()
        self._count_samples()
        self._setup_pagination()
        self._add_sample_ids()
        self._add_calldata()
        self._add_call_level_metadata()

        self.status_messages.append({
            'message': 'Request accepted, response successful',
            'messageType': 'INFO'
        })


    def _parse_request(self, request):

        self.has_position_range = False
        input = {}

        position_range = request.args.get('positionRange', default = '', type = str)

        if position_range:
            try:
                position_range_splitted = position_range.split(":")
                input['chrom'] = position_range_splitted[0]
                req_pos_splitted = position_range_splitted[1].split("-")
                input['startpos'] = int(req_pos_splitted[0])
                input['endpos'] = int(req_pos_splitted[1])
                self.has_position_range = True

            except:
                print('ERROR: positionRange seems to be malformatted')


        samples = request.args.get('germplasmDbId', default = '', type = str)
        if samples:
            input['samples'] = samples.split(',')
        else:
            input['samples'] = self.gd.samples.tolist()


        input['dimensionVariantPage'] = request.args.get('dimensionVariantPage', default = 0, type = int)
        input['dimensionCallSetPage'] = request.args.get('dimensionCallSetPage', default = 0, type = int)

        input['dimensionVariantPageSize'] = request.args.get('dimensionVariantPageSize', default = 100, type = int)
        input['dimensionCallSetPageSize'] = request.args.get('dimensionCallSetPageSize', default = 100, type = int)


        input['preview'] = False
        preview = request.args.get('preview', default = 'false', type = str)
        if preview == 'true':
            input['preview'] = True

        input['dataMatrixAbbreviations'] = request.args.get('dataMatrixAbbreviations', default = None, type = str)

        if input['dataMatrixAbbreviations']:
            input['dataMatrixAbbreviations'] = input['dataMatrixAbbreviations'].split(',')

        self.input = input


    def _count_variants(self):

        self.slice_variant_calls = False

        if self.has_position_range:

            location_start, lookup_type_start = self.gd.get_posidx_by_genome_coordinate(self.input['chrom'], self.input['startpos'])
            location_end, lookup_type_end = self.gd.get_posidx_by_genome_coordinate(self.input['chrom'], self.input['endpos'])
            location_end = location_end + 1

            self.slice_variant_calls = slice(location_start, location_end, None)
            self.slice_variants_indices = np.arange(location_start, location_end, 1)
            positions = self.gd.pos[self.slice_variant_calls]

            self.count_variants = len(positions)

        else:
            self.count_variants = self.gd.count_variants



    def _count_samples(self):
        self.count_samples = len(self.input['samples'])



    def _setup_pagination(self):

        samples_mask, samples_selected_mapped = self.gd.get_samples_mask(self.input['samples'])
        self.samples_selected_mapped = samples_selected_mapped
        self.sample_mask_integer_indices = np.where(samples_mask)[0]

        total_pages_variants = math.ceil(self.count_variants / self.input['dimensionVariantPageSize'])

        count_samples = len(samples_selected_mapped)
        total_pages_samples = math.ceil(count_samples / self.input['dimensionCallSetPageSize'])


        if self.input['dimensionVariantPage'] >= total_pages_variants:
            self.input['dimensionVariantPage'] = total_pages_variants - 1
            
            self.status_messages.append({
                'message': 'Given parameter `dimensionVariantPage` was bigger than corresponding `totalPages` would allow. `dimensionVariantPage` was set to the biggest possible value of '+str(self.input['dimensionVariantPage']),
                'messageType': 'WARNING'
            })


        if self.input['dimensionCallSetPage'] >= total_pages_samples:
            self.input['dimensionCallSetPage'] = total_pages_samples - 1

            self.status_messages.append({
                'message': 'Given parameter `dimensionCallSetPage` was bigger than corresponding `totalPages` would allow. `dimensionCallSetPage` was set to the biggest possible value of '+str(self.input['dimensionCallSetPage']),
                'messageType': 'WARNING'
            })

        
        self.pagination = {
            'VARIANTS': {
                'dimension': 'VARIANTS',
                'page': self.input['dimensionVariantPage'],
                'pageSize': self.input['dimensionVariantPageSize'],
                'totalCount': self.count_variants,
                'totalPages': total_pages_variants
            },
            'CALLSETS': {
                'dimension': 'CALLSETS',
                'page': self.input['dimensionCallSetPage'],
                'pageSize': self.input['dimensionCallSetPageSize'],
                'totalCount': self.count_samples,
                'totalPages': total_pages_samples
            }
        }


        samples_start = self.input['dimensionCallSetPage'] * self.input['dimensionCallSetPageSize']
        samples_end = samples_start + self.input['dimensionCallSetPageSize']

        if samples_end >= len(samples_selected_mapped):
            samples_end = len(samples_selected_mapped)

        slice_samples_axis = slice(samples_start, samples_end, None)
        self.slice_samples_axis = slice_samples_axis
        self.sample_mask_integer_indices_sliced = self.sample_mask_integer_indices[slice_samples_axis]



    def _add_sample_ids(self):
        self.callset_db_ids = self.samples_selected_mapped[self.slice_samples_axis]




    def _add_calldata(self):

        variants_start = self.input['dimensionVariantPage'] * self.input['dimensionVariantPageSize']
        variants_end = variants_start + self.input['dimensionVariantPageSize']

        if self.has_position_range:
            slice_variant_axis = self.slice_variants_indices[slice(variants_start, variants_end, None)]

        else:
            slice_variant_axis = slice(variants_start, variants_end, None)
        
        self.slice_variant_axis = slice_variant_axis


        if not self.input['preview']:
            if not (self.input['dataMatrixAbbreviations'] and 'GT' not in self.input['dataMatrixAbbreviations']):

                sliced_variant_calls = self.gd.callset['calldata/GT'].get_orthogonal_selection((self.slice_variant_axis, self.sample_mask_integer_indices_sliced))
                sliced_variant_calls = sliced_variant_calls.transpose(1, 0, 2) # transpose GenotypeArray so that samples are in the 1st dimension and not the variant-calls

                calls = []

                for i in range(sliced_variant_calls.shape[0]):
                    _sample_variant_calls = ['/'.join(map(str, m)) for m in sliced_variant_calls[i]]
                    calls.append(_sample_variant_calls)

                self.data_matrices.append({
                    'dataMatrix': calls,
                    'dataMatrixAbbreviation': 'GT',
                    'dataMatrixName': 'Genotype',
                    'dataType': 'string'
                })

        chrom = self.gd.callset['variants/CHROM'].get_orthogonal_selection((slice_variant_axis))
        positions = self.gd.pos[slice_variant_axis]
        self.variant_db_ids = [str(chrom[idx])+':'+str(pos) for (idx, pos) in enumerate(positions.tolist())]


    def _add_call_level_metadata(self):

        if self.input['preview']:
            return

        if self.input['dataMatrixAbbreviations'] and 'DP' not in self.input['dataMatrixAbbreviations']:
            return

        # add possible DP values
        if 'DP' in self.gd.available_calldata:
            sliced_DP = self.gd.callset['calldata/DP'].get_orthogonal_selection((self.slice_variant_axis, self.sample_mask_integer_indices_sliced)).T

            self.data_matrices.append({
                'dataMatrix': sliced_DP.tolist(),
                'dataMatrixAbbreviation': 'DP',
                'dataMatrixName': 'Read depth',
                'dataType': 'integer'
            })



    def get_response_object(self):

        brapi_response = {
            "@context": [
                "https://brapi.org/jsonld/context/metadata.jsonld"
            ],
            "metadata": {
                "datafiles": [],
                "pagination": None,
                "status": self.status_messages
            },
            "result": {
                "callSetDbIds": self.callset_db_ids,
                "dataMatrices": self.data_matrices,
                "expandHomozygotes": True,
                "pagination": [
                    self.pagination['VARIANTS'],
                    self.pagination['CALLSETS']
                ],
                "sepPhased": "|",
                "sepUnphased": "/",
                "unknownString": ".",
                "variantSetDbIds": None,
                "variantDbIds": self.variant_db_ids
            }
        }

        return brapi_response