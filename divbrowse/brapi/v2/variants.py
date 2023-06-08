import math
import numpy as np
#from icecream import ic

class BrapiVariants():

    def __init__(self, gd, request):

        self.gd = gd
        self.request = request

        self.status_messages = []
        self.data_matrices = []

        self._parse_request(request)
        self._count_variants()
        self._setup_pagination()

        self._add_data()

        #self._add_calldata()
        #self._add_call_level_metadata()

        self.status_messages.append({
            'message': 'Request accepted, response successful',
            'messageType': 'INFO'
        })


    def _parse_request(self, request):

        self.has_variant_db_id = False
        input = {}

        variant_db_id = request.args.get('variantDbId', default = '', type = str)

        if variant_db_id:
            try:
                variant_db_id_splitted = variant_db_id.split(':')
                input['chrom'] = variant_db_id_splitted[0]
                input['pos'] = int(variant_db_id_splitted[1])
                self.has_variant_db_id = True

            except:
                print('ERROR: variantDbId seems to be malformatted. It should have the format `chromosome:position`. Example: `1:56242`')
                #self.status_messages.append({
                #    'message': 'Given parameter `page` was bigger than corresponding `totalPages` would allow. `currentPage` was set to the biggest possible value of '+str(self.input['page']),
                #    'messageType': 'WARNING'
                #})

        input['page'] = request.args.get('page', default = 0, type = int)
        input['pageSize'] = request.args.get('pageSize', default = 1000, type = int)

        self.input = input



    def _count_variants(self):

        self.slice_variant_calls = False

        if self.has_variant_db_id:

            """
            location_start, lookup_type_start = self.gd.get_posidx_by_genome_coordinate(self.input['chrom'], self.input['pos'])

            self.slice_variant_calls = slice(location_start, location_end, None)
            self.slice_variants_indices = np.arange(location_start, location_end, 1)
            positions = self.gd.pos[self.slice_variant_calls]

            self.count_variants = len(positions)
            """

            self.count_variants = 1

        else:
            self.count_variants = self.gd.count_variants




    def _setup_pagination(self):

        total_pages = math.ceil(self.count_variants / self.input['pageSize'])

        if self.input['page'] >= total_pages:
            self.input['page'] = total_pages - 1
            
            self.status_messages.append({
                'message': 'Given parameter `page` was bigger than corresponding `totalPages` would allow. `currentPage` was set to the biggest possible value of '+str(self.input['page']),
                'messageType': 'WARNING'
            })

        
        self.pagination = {
            'currentPage': self.input['page'],
            'pageSize': self.input['pageSize'],
            'totalCount': self.count_variants,
            'totalPages': total_pages
        }




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



    def _add_data(self):

        reference_bases = None
        alternate_bases = None

        if self.has_variant_db_id:

            coord, lookup_type_start = self.gd.get_posidx_by_genome_coordinate(self.input['chrom'], self.input['pos'])
            reference_bases = self.gd.callset['variants/REF'].get_basic_selection(coord)
            reference_bases = [reference_bases]

            alternate_bases = self.gd.callset['variants/ALT'].get_basic_selection(coord).tolist()
            
            chrom = self.gd.callset['variants/CHROM'].get_basic_selection(coord).tolist()
            pos = self.gd.callset['variants/POS'].get_basic_selection(coord).tolist()

        else:

            coord_start = self.input['page'] * self.input['pageSize']
            coord_end = coord_start + self.input['pageSize']

            reference_bases = self.gd.callset['variants/REF'].get_basic_selection(slice(coord_start, coord_end)).tolist()

            alternate_bases = self.gd.callset['variants/ALT'].get_basic_selection(slice(coord_start, coord_end)).tolist()

            chrom = self.gd.callset['variants/CHROM'].get_basic_selection(slice(coord_start, coord_end)).tolist()
            pos = self.gd.callset['variants/POS'].get_basic_selection(slice(coord_start, coord_end)).tolist()


        data = []

        for i, ref_base in enumerate(reference_bases):
            data.append({
                'additionalInfo': {},
                'referenceBases': ref_base,
                'alternateBases': [x for x in alternate_bases[i] if x != ''],
                'ciend': [],
                'cipos': [],
                'created': None,
                'updated': None,
                'start': pos[i],
                'end': pos[i],
                'svlen': None,
                'externalReferences': [{}],
                'filtersApplied': False,
                'filtersFailed': [],
                'filtersPassed': False,
                'referenceDbId': None,
                'referenceName': '',
                'referenceSetDbId': None,
                'referenceSetName': '',
                'variantDbId': str(chrom[i])+':'+str(pos[i]),
                'variantNames': [],
                'variantSetDbId': [],
                'variantType': 'SNV'
            })

        self.data = data



    def get_response_object(self):

        brapi_response = {
            "@context": [
                "https://brapi.org/jsonld/context/metadata.jsonld"
            ],
            "metadata": {
                "datafiles": [],
                "pagination": self.pagination,
                "status": self.status_messages
            },
            "result": {
                "data": self.data
            }
        }

        return brapi_response