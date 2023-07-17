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
                self.status_messages.append({
                    'message': 'variantDbId seems to be malformatted. It should have the format `chromosome:position`. Example: `1:56242`',
                    'messageType': 'ERROR'
                })

        input['page'] = request.args.get('page', default = 0, type = int)
        input['pageSize'] = request.args.get('pageSize', default = 1000, type = int)

        self.input = input



    def _count_variants(self):
    
        self.slice_variant_calls = False

        if self.has_variant_db_id:
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