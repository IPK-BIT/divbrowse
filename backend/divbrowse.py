from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
import os
os.environ['NUMEXPR_MAX_THREADS'] = '144'
import allel
import numpy as np
import pandas as pd
import sys
import json
from pprint import pprint
from sklearn.metrics import pairwise_distances
from timeit import default_timer as timer
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.tools.inputs import inputs
import socket
hostname = socket.gethostname()

from lib.utils import ApiError
from lib.genotype_data import GenotypeData
from lib.annotation_data import AnnotationData
from lib.genotype_data import impute_with_mean, calculate_pca_in_snp_window



# =========================================================================
# PLEASE EDIT VARIABLES BELOW FOR CONFIGURATION
# =========================================================================
filename_config_ini = 'divbrowse.ini'




# =========================================================================
# PLEASE DON'T CHANGE ANYTHING BELOW UNLESS YOU KNOW WHAT YOU'RE DOING.
# =========================================================================
app = Flask(__name__)
#app.run(debug=True)


import yaml
with open('divbrowse.config.yaml') as fd:
    config = yaml.load(fd)

pprint(config)
#print("~~~~~~~~~~~~~~~~~~~~~~")
#exit()



def pl():
    print("========================================================================================")


pl()


gd = GenotypeData(config)
ad = AnnotationData(config, gd)

#print(gd.available_calldata)
#print(gd.available_variants_metadata)


def process_request_vars(vars):

    try:
        # conversion to Python list from stringified JSON is necessary for form-data POST requests of vcf_export
        if type(vars['samples']) is str:
            vars['samples'] = json.loads(vars['samples'])

        samples = gd.map_input_sample_ids_to_vcf_sample_ids(vars['samples'])

        processed = {
            'chrom': vars['chrom'],
            'samples': samples
        }

        processed['count'] = None
        if 'count' in vars:
            processed['count'] = int(vars['count'])

        processed['startpos'] = None
        if 'startpos' in vars:
            processed['startpos'] = int(vars['startpos'])

        processed['endpos'] = None
        if 'endpos' in vars:
            processed['endpos'] = int(vars['endpos'])

        processed['variant_filter_settings'] = None
        if 'variant_filter_settings' in vars:
            # conversion to Python list from stringified JSON is necessary for form-data POST requests of vcf_export
            if type(vars['variant_filter_settings']) is str:
                vars['variant_filter_settings'] = json.loads(vars['variant_filter_settings'])
            processed['variant_filter_settings'] = vars['variant_filter_settings']

        return processed

    except KeyError:
        raise ApiError('Some input data is missing.')




@app.route("/snp_window_summary", methods = ['GET', 'POST', 'OPTIONS'])
def __snp_window_summary():

    if request.method == 'POST':
        input = process_request_vars(request.get_json(silent=True))
    else:
        return 'ERROR'

    _result = gd.get_slice_of_snps(
        chrom = input['chrom'],
        startpos = input['startpos'],
        endpos = input['endpos'],
        samples = input['samples'],
        variant_filter_settings = input['variant_filter_settings']
    )

    return jsonify(_result.stats)



@app.route("/pca", methods = ['GET', 'POST', 'OPTIONS'])
def __pca():

    if request.method == 'POST':
        input = process_request_vars(request.get_json(silent=True))
    else:
        return 'ERROR'

    _result = gd.get_slice_of_snps(
        chrom = input['chrom'],
        startpos = input['startpos'],
        endpos = input['endpos'],
        samples = input['samples'],
        variant_filter_settings = input['variant_filter_settings']
    )

    pca_result = calculate_pca_in_snp_window(_result.snps_to_alt, _result.samples_selected_mapped)

    result = {
        'pca_result': pca_result.tolist()
    }

    return jsonify(result)


@app.route("/variants", methods = ['GET', 'POST', 'OPTIONS'])
def __variants():

    start_all = timer()

    if request.method == 'POST':
        input = process_request_vars(request.get_json(silent=True))
    else:
        #raise ApiError('Method not allowed', status_code=405)
        return ''

    if input['chrom'] not in gd.list_chrom:
        return jsonify({
            'success': False, 
            'status': 'error', 
            'message': 'The provided chromosome number '+str(input['chrom'])+' is not included in the SNP matrix.'
        })
    
    print("==== 0 => calculation time: ", timer() - start_all)

    start = timer()

    _result = gd.get_slice_of_snps(
        chrom = input['chrom'],
        startpos = input['startpos'],
        endpos = input['endpos'],
        count = input['count'],
        samples = input['samples'],
        variant_filter_settings = input['variant_filter_settings']
    )

    snps_to_alt = _result.snps_to_alt
    _slice_snps = _result.slice_snps
    _sliced_snps = _result.sliced_snps
    samples_mask = _result.samples_mask
    samples_selected_mapped = _result.samples_selected_mapped
    positions = _result.positions
    location_start = _result.location_start
    location_end = _result.location_end

    # calculate some allel stats like MAF etc.
    per_snp_stats = gd.calculate_per_snp_stats(snps_to_alt)

    # impute with mean
    imputed = impute_with_mean(snps_to_alt)
    ref_vec = np.zeros(snps_to_alt.shape[1]).reshape(1, snps_to_alt.shape[1])
    print("==== gd.get_snp_matrix() + gd.calculate_per_snp_stats() + impute_with_mean() => calculation time: ", timer() - start)

    start = timer()
    distances = pairwise_distances(imputed, ref_vec, n_jobs=1, metric='hamming')
    distances = distances * snps_to_alt.shape[1]
    distances = distances.astype(np.int16);
    sample_ids = np.array(samples_selected_mapped).reshape(gd.samples[samples_mask].shape[0], 1)
    distances_combined = np.concatenate((sample_ids, distances), axis=1)
    print("==== pairwise_distances() calculation time: ", timer() - start)

    # Get the reference nucleotides (as letters ATCG)
    sliced_reference = gd.reference_allele[_slice_snps]

    # Get the alternate nucleotides (as letters ATCG)
    sliced_alternates = gd.alternate_alleles[_slice_snps]


    variants_samples = {}
    variants_gt = {}
    if _sliced_snps.ndim == 2:
        _sliced_snps = _sliced_snps.T # transpose GenotypeArray so that samples are in the 1st dimension and not the SNP-calls

    if _sliced_snps.ndim == 3:
        _sliced_snps = _sliced_snps.transpose(1, 0, 2) # transpose GenotypeArray so that samples are in the 1st dimension and not the SNP-calls

    i = 0
    
    for sample in samples_selected_mapped:
        variants_samples[sample] = snps_to_alt[i].tolist()
        variants_gt[sample] = _sliced_snps[i].tolist()
        i += 1

    start = timer()

    result = {
        'coordinate_first': int(gd.pos[location_start]),
        'coordinate_last': int(gd.pos[location_end-1]),
        'coordinate_first_next': int(gd.pos[location_end]),
        'coordinate_last_prev': int(gd.pos[location_start-1]),
        'coordinate_first_chromosome': gd.chrom[location_start],
        'coordinate_last_chromosome': gd.chrom[location_end],
        'variants_coordinates': positions.tolist(),
        'variants': variants_samples,
        'variants_gt': variants_gt,
        'reference': sliced_reference.tolist(),
        'alternates': sliced_alternates.tolist(),
        'hamming_distances_to_reference': distances_combined.tolist()
    }

    # get DP values
    if 'DP' in gd.available_calldata:
        DP_values = {}
        sliced_DP = gd.callset['calldata/DP'].get_orthogonal_selection((_slice_snps, samples_mask)).T
        DP_values = {}
        i = 0
        for sample in samples_selected_mapped:
            DP_values[sample] = sliced_DP[i].tolist()
            i += 1
        result['dp'] = DP_values


    # get DV values
    if 'DV' in gd.available_calldata:
        DV_values = {}
        sliced_DV = gd.callset['calldata/DV'].get_orthogonal_selection((_slice_snps, samples_mask)).T
        DV_values = {}
        i = 0
        for sample in samples_selected_mapped:
            DV_values[sample] = sliced_DV[i].tolist()
            i += 1
        result['dv'] = DV_values


    #### QUAL #########################
    if 'QUAL' in gd.available_variants_metadata:
        sliced_qual = gd.variants_qual.get_basic_selection(_slice_snps)
        per_snp_stats['vcf_qual'] = sliced_qual.tolist()



    result['per_snp_stats'] = per_snp_stats

    #### SNPEFF #######################
    if gd.available['snpeff']:
        sliced_ann = gd.callset['variants/ANN'].get_basic_selection( _slice_snps )
        
        snpeff_variants = {}
        i = 0
        for snpeff_variant_pos in positions.tolist():
            if isinstance(sliced_ann[i], str):
                snpeff_variants[snpeff_variant_pos] = sliced_ann[i]
            else:
                snpeff_variants[snpeff_variant_pos] = sliced_ann[i].tolist()
            i += 1

        result['snpeff_variants_coordinates'] = positions.tolist()
        result['snpeff_variants'] = snpeff_variants


    #### GFF3 ###########################################
    if ad.available['gff3']:
        curr_start = int(gd.pos[location_start])
        curr_end = int(gd.pos[location_end-1])

        start = timer()
        genes_within_slice = ad.genes.loc[ ( ad.genes['start'] <= curr_start) & (ad.genes['end'] >= curr_end ) ]
        genes_starting_in_slice = ad.genes.loc[ ( ad.genes['start'] >= curr_start) & (ad.genes['start'] <= curr_end ) ]
        genes_ending_in_slice = ad.genes.loc[ ( ad.genes['end'] >= curr_start) & (ad.genes['end'] <= curr_end ) ]
        genes_all_in_slice = pd.concat([genes_within_slice, genes_starting_in_slice, genes_ending_in_slice]).drop_duplicates().reset_index(drop=True)
        genes_all_in_slice = genes_all_in_slice.loc[ (genes_all_in_slice['seqid'] == ad.chrom_gff3_map[input['chrom']]) ]
        calctime = timer() - start
        print("==== time for genes lookup: ", calctime)
        result['features'] = genes_all_in_slice.to_dict(orient='records')

        #### Nearest gene ##############################
        nearest_gene = ad.get_nearest_gene_start_pos(input['chrom'], int(gd.pos[location_start]))
        result['nearest_feature'] = nearest_gene.to_dict(orient='records')
    

    print("==== output dict creation => calculation time: ", timer() - start)

    print("==== ALL /variants => calculation time: ", timer() - start_all)

    return jsonify(result)



@app.route("/vcf_export_check", methods = ['GET', 'POST', 'OPTIONS'])
def __vcf_export_check():
    
    if request.method == 'POST':
        input = process_request_vars(request.get_json(silent=True))
    else:
        #raise ApiError('Method not allowed', status_code=405)
        return ''

    if input['chrom'] not in gd.list_chrom:
        return jsonify({
            'success': False, 
            'status': 'error_missing_chromosome', 
            'message': 'The provided chromosome number '+str(input['chrom'])+' is not included in the SNP matrix.'
        })

    _result = gd.get_slice_of_snps(
        chrom = input['chrom'],
        startpos = input['startpos'],
        endpos = input['endpos'],
        count = input['count'],
        samples = input['samples'],
        variant_filter_settings = input['variant_filter_settings']
    )

    if _result.stats['count_snps_in_window_filtered'] > 5000:
        return jsonify({
            'success': False, 
            'status': 'error_snp_window_too_big', 
            'message': 'The requested SNP window size is bigger than 5000 SNPs and is therefore too big. Please decrease the window size to not exceed 5000 SNPs.'
        })

    return jsonify({
        'success': True, 
        'status': 'export_possible',
        'message': _result.stats['count_snps_in_window_filtered']
    })


@app.route("/vcf_export", methods = ['GET', 'POST', 'OPTIONS'])
def __vcf_export():

    if request.method == 'POST':
        input = process_request_vars(request.form.to_dict())
    else:
        #raise ApiError('Method not allowed', status_code=405)
        return ''

    if input['chrom'] not in gd.list_chrom:
        return jsonify({
            'success': False, 
            'status': 'error_missing_chromosome', 
            'message': 'The provided chromosome number '+str(input['chrom'])+' is not included in the SNP matrix.'
        })

    _result = gd.get_slice_of_snps(
        chrom = input['chrom'],
        startpos = input['startpos'],
        endpos = input['endpos'],
        samples = input['samples'],
        variant_filter_settings = input['variant_filter_settings']
    )

    snps_to_alt = _result.snps_to_alt
    _slice_snps = _result.slice_snps
    _sliced_snps = _result.sliced_snps
    samples_mask = _result.samples_mask
    samples_selected_mapped = _result.samples_selected_mapped
    positions = _result.positions
    filtered_positions_indices = _result.filtered_positions_indices
    location_start = _result.location_start
    location_end = _result.location_end


    vcf_lines_header = [
        '##fileformat=VCFv4.0',
        #'##fileDate=20190225',
        #'##source=SeqArray_Format_v1.0',
        #'##reference=Morex v2',
        #'##INFO=<ID=MQ,Number=1,Type=Integer,Description="Average mapping quality">',
        '##FILTER=<ID=PASS,Description="All filters passed">',
        '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
        #'##FORMAT=<ID=DP,Number=.,Type=Integer,Description="Read depth">',
        #'##FORMAT=<ID=DV,Number=.,Type=Integer,Description="Read depth of the alternative allele">'
    ]

    vcf_genotypes = gd.map_vcf_sample_ids_to_input_sample_ids(gd.samples[samples_mask].astype(str).tolist())
    vcf_line_variants_header = ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT'] + vcf_genotypes
    vcf_lines_header.append("\t".join(vcf_line_variants_header)) 

    ref = gd.reference_allele.get_orthogonal_selection( (filtered_positions_indices) )
    alts = gd.alternate_alleles.get_orthogonal_selection( (filtered_positions_indices) )
    qual = gd.callset['variants/QUAL'].get_orthogonal_selection( (filtered_positions_indices) )
    #mq = callset['variants/MQ'].get_orthogonal_selection( (filtered_positions_indices) )

    def generate():
        
        yield "\n".join(vcf_lines_header) + "\n"

        i = 0
        for pos_idx in filtered_positions_indices.tolist():

            vcf_line = [
                str(input['chrom']),
                str(positions[pos_idx]),
                '.',
                str(ref[i]),
                ','.join([ _alt for _alt in (alts[i].astype(str).tolist()) if _alt != '' ]), #','.join([ _alt for _alt in (alts[i].astype(str).tolist()) if _alt != '' ]),
                str(qual[i]),
                'NA',
                '', #'MQ='+str(mq[i]),
                'GT' #'GT:DP:DV'
            ]

            if 'samples' in input:
                gt_slice = gd.callset['calldata/GT'].get_orthogonal_selection( ([pos_idx], samples_mask, slice(None)) )
            else:
                gt_slice = gd.callset['calldata/GT'].get_orthogonal_selection( ([pos_idx], slice(None), slice(None)) )
            ga = allel.GenotypeArray(gt_slice)
            gt = ga.to_gt()

            vcf_line = vcf_line + gt[0].astype(str).tolist()
            yield "\t".join(vcf_line)+"\n"
            i = i + 1

    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition":"attachment; filename=custom_export.vcf"})





@app.route("/blast", methods = ['GET', 'POST', 'OPTIONS'])
def __blast():

    if request.method != 'POST':
        return ''

    if config['blast']['active'] is not True:
        return 'BLAST is not allowed'

    gi = GalaxyInstance(url = config['blast']['galaxy_server_url'], email = config['blast']['galaxy_user'], password = config['blast']['galaxy_pass'])

    json_request_vars = request.get_json(force=True, silent=True)

    blast_parameters = {
        'query': str(json_request_vars['query']),
        'database': str(config['blast']['blast_database']),
        'type': config['blast']['blast_type'],
        'galaxy_tool_id': config['blast']['galaxy_tool_id']
    }

    histories = gi.histories.get_histories()
    history_id = histories[0]['id']

    paste_content_result = gi.tools.paste_content(blast_parameters['query'], history_id, file_name='blast_query.fasta')
    paste_content_dataset_id = paste_content_result['outputs'][0]['id']

    tool_inputs = (
        inputs().set_dataset_param("query", paste_content_dataset_id, src='hda')
        .set_param('db_opts', 'db')
        .set_param('db_opts|database', [blast_parameters['database']])
        .set_param('blast_type', blast_parameters['type'])
    )
    run_tool_result = gi.tools.run_tool(history_id, blast_parameters['galaxy_tool_id'], tool_inputs)
    result_dataset_id = run_tool_result['outputs'][0]['id']

    blast_chromosome_mapping = config['blast']['blast_result_to_vcf_chromosome_mapping']

    blast_result_dataset = gi.datasets.download_dataset(result_dataset_id)
    blast_result_json = []

    blast_result_lines = blast_result_dataset.decode('utf-8').split("\n")
    for line in blast_result_lines:
        if line != "":
            line_parts = line.split("\t")
            _chromosome_vcf = str(blast_chromosome_mapping[line_parts[1]])
            _single_blast_hit = {
                'chromosome': _chromosome_vcf,
                'percentage_of_identical_matches': line_parts[2],
                'alignment_length': line_parts[3],
                'number_of_mismatches': line_parts[4],
                'number_of_gap_openings': line_parts[5],
                'start_of_alignment_in_query': line_parts[6],
                'end_of_alignment_in_query': line_parts[7],
                'start_of_alignment_in_subject': line_parts[8],
                'end_of_alignment_in_subject': line_parts[9],
                'e_value': line_parts[10],
                'bit_score': line_parts[11],
                'snp_count': gd.count_snps_in_window(_chromosome_vcf, int(line_parts[8]), int(line_parts[9]))
            }
            blast_result_json.append(_single_blast_hit)
    
    return jsonify({
        'success': True,
        'blast_result': str(blast_result_dataset.decode('utf-8')),
        'blast_hits': blast_result_json
    })



@app.route("/metadata", methods = ['GET', 'POST', 'OPTIONS'])
def __metadata():

    features = {
        'blast': config['blast']['active'],
        'pca': True,
    }

    result = {
        'ploidy': gd.ploidy,
        'count_genotypes': len(gd.samples),
        'count_variants': len(gd.pos),
        'count_snp_matrix_elements': len(gd.samples) * len(gd.pos),
        'chromosomes': gd.list_of_chromosomes,
        'samples': gd.map_vcf_sample_ids_to_input_sample_ids(gd.samples.tolist()),
        'gff3': ad.metadata_gff3,
        'features': features,
        'dataset_descriptions': dict(config['dataset_descriptions'])
    }

    return jsonify(result)



@app.route("/chromosomes", methods = ['GET', 'POST', 'OPTIONS'])
def __chromosomes():
    return jsonify(gd.list_of_chromosomes)


@app.route("/samples", methods = ['GET', 'POST', 'OPTIONS'])
def __samples():
    return jsonify(gd.samples.tolist())


@app.route("/genes", methods = ['GET', 'POST', 'OPTIONS'])
def __genes():
    result = {
        'genes': ad.genes_list,
    }
    return jsonify(result)


@app.route("/", methods = ['GET', 'POST', 'OPTIONS'])
def __home():
    return 'Divbrowse server is running'



@app.errorhandler(ApiError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response



@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Accept, Accept-CH, Accept-Charset, Accept-Datetime, Accept-Encoding, Accept-Ext, Accept-Features, Accept-Language, Accept-Params, Accept-Ranges, Access-Control-Allow-Credentials, Access-Control-Allow-Headers, Access-Control-Allow-Methods, Access-Control-Allow-Origin, Access-Control-Expose-Headers, Access-Control-Max-Age, Access-Control-Request-Headers, Access-Control-Request-Method, Age, Allow, Alternates, Authentication-Info, Authorization, C-Ext, C-Man, C-Opt, C-PEP, C-PEP-Info, CONNECT, Cache-Control, Compliance, Connection, Content-Base, Content-Disposition, Content-Encoding, Content-ID, Content-Language, Content-Length, Content-Location, Content-MD5, Content-Range, Content-Script-Type, Content-Security-Policy, Content-Style-Type, Content-Transfer-Encoding, Content-Type, Content-Version, Cookie, Cost, DAV, DELETE, DNT, DPR, Date, Default-Style, Delta-Base, Depth, Derived-From, Destination, Differential-ID, Digest, ETag, Expect, Expires, Ext, From, GET, GetProfile, HEAD, HTTP-date, Host, IM, If, If-Match, If-Modified-Since, If-None-Match, If-Range, If-Unmodified-Since, Keep-Alive, Label, Last-Event-ID, Last-Modified, Link, Location, Lock-Token, MIME-Version, Man, Max-Forwards, Media-Range, Message-ID, Meter, Negotiate, Non-Compliance, OPTION, OPTIONS, OWS, Opt, Optional, Ordering-Type, Origin, Overwrite, P3P, PEP, PICS-Label, POST, PUT, Pep-Info, Permanent, Position, Pragma, ProfileObject, Protocol, Protocol-Query, Protocol-Request, Proxy-Authenticate, Proxy-Authentication-Info, Proxy-Authorization, Proxy-Features, Proxy-Instruction, Public, RWS, Range, Referer, Refresh, Resolution-Hint, Resolver-Location, Retry-After, Safe, Sec-Websocket-Extensions, Sec-Websocket-Key, Sec-Websocket-Origin, Sec-Websocket-Protocol, Sec-Websocket-Version, Security-Scheme, Server, Set-Cookie, Set-Cookie2, SetProfile, SoapAction, Status, Status-URI, Strict-Transport-Security, SubOK, Subst, Surrogate-Capability, Surrogate-Control, TCN, TE, TRACE, Timeout, Title, Trailer, Transfer-Encoding, UA-Color, UA-Media, UA-Pixels, UA-Resolution, UA-Windowpixels, URI, Upgrade, User-Agent, Variant-Vary, Vary, Version, Via, Viewport-Width, WWW-Authenticate, Want-Digest, Warning, Width, X-Content-Duration, X-Content-Security-Policy, X-Content-Type-Options, X-CustomHeader, X-DNSPrefetch-Control, X-Forwarded-For, X-Forwarded-Port, X-Forwarded-Proto, X-Frame-Options, X-Modified, X-OTHER, X-PING, X-PINGOTHER, X-Powered-By, X-Requested-With'
    return response