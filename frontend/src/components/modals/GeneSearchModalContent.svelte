<script>
export let close;

import { getContext, onMount } from 'svelte';

const context = getContext('app');
let { controller } = context.app();

import getStores from '/utils/store';
const { snpPosHighlights } = getStores();

import LoadingAnimation from '/components/utils/LoadingAnimation.svelte';
let showLoadingAnimation = false;

import DataFrame from 'dataframe-js';
import Fuse from 'fuse.js'
import { Datatable, rows } from 'svelte-simple-datatables';

import { pageNumber } from 'svelte-simple-datatables/src/stores/state.js'
const reset = () => {
    pageNumber.set(1)
}


import GeneDetailsModalContent from '/components/modals/GeneDetailsModalContent.svelte';
const { open } = getContext('2nd-modal');
const openGeneDetailsModal = (featureId) => {
    open(GeneDetailsModalContent, { featureId: featureId });
};


const flip = obj => Object.assign({}, ...Object.entries(obj).map(([a,b]) => ({[b]: a })));
const chromMap = flip(controller.metadata.gff3.gff3_to_vcf_chromosome_mapping);

const debounce = (callback, wait) => {
    let timeoutId = null;
    return (...args) => {
        window.clearTimeout(timeoutId);
        timeoutId = window.setTimeout(() => {
        callback.apply(null, args);
        }, wait);
    };
};

let query = '';
let result = false;
let resultRowCount = 0;


// vars for 'search in interval' feature
let searchInInterval = false;
let selectedChromosome = controller.chromosome;
let startpos;
let endpos;


const fuseOptions = {
    includeScore: false,
    findAllMatches: false,
    threshold: 0.3, // 0.3 is a good value
    distance: 40, // 40 is a good value
    //ignoreLocation: true,
    keys: ['ID', 'description']
}

let fuse = null;
let df = null;
let data = null;

onMount(async () => {
    df = controller.metadata.gff3._dataframe;
    data = df.toCollection();
    fuse = new Fuse(data, fuseOptions);
});

function setupSearchInInterval() {
    df = controller.metadata.gff3._dataframe;
    if (searchInInterval === true) {
        let _chrom = chromMap[selectedChromosome];
        df = df.filter(row => row.get('seqid') === _chrom);
        if (startpos !== undefined && startpos > 0) {
            df = df.filter(row => row.get('start') >= startpos);
        }
        if (endpos !== undefined && endpos > 0) {
            df = df.filter(row => row.get('end') <= endpos);
        }

        //fuse = new Fuse(df.toCollection(), fuseOptions);
        doSearch(query);

    } else {
        // reset everything
        //fuse = new Fuse(df.toCollection(), fuseOptions);
        //df = controller.metadata.gff3._dataframe;
        doSearch(query);
    }
}


const clean = (query) => query.replace('-', ' ').toLowerCase();

function doSearch(query) {
    if (query === '') return false;
    showLoadingAnimation = true;
    //let resultFuzzy = fuse.search(query);
    //result = resultFuzzy.map(x => x.item);

    let queryCleaned = clean(query);
    let df_result = df.filter(row => clean(row.get('description')).includes( queryCleaned ) === true || clean(row.get('ID')).includes( queryCleaned ) === true);
    result = df_result.toCollection();

    resultRowCount = result.length;
    showLoadingAnimation = false;
    reset();
}

const debouncedDoSearch = debounce(doSearch, 750);
const debouncedSetupSearchInInterval = debounce(setupSearchInInterval, 500);

$: debouncedDoSearch(query);



function goToPos(chrom, startpos, endpos) {
    close();
    let chromMap = controller.metadata.gff3.gff3_to_vcf_chromosome_mapping;
    controller.goToChromosomeAndPosition(chromMap[chrom], startpos)
    snpPosHighlights.set({startpos: startpos, endpos: endpos});
}


const datatableSettings = {
    sortable: true,
    pagination: true,
    rowPerPage: 10,
    columnFilter: true,
    scrollY: false,
    css: false,
    blocks: {
        searchInput: false, 
        paginationButtons: true,
        paginationRowCount: true,
    }
}

</script> 
 

<div style="min-height: 600px;">
    <div class="divbrowse-modal-dialogue-headline">Gene Search</div>
   
    <div style="position: relative; float:left;">
        <input type="text" bind:value={query} placeholder="The ID and the description can be searched..." style="font-size: 1rem; padding-left: 35px; width: 25rem;" class="divbrowse-form-control">
        <!--<span class="material-icons" style="position: absolute; top: 9px; left: 6px;">search</span>-->
        <div style="position: absolute; top: 9px; left: 6px;">
            <svg style="width:24px;height:24px" viewBox="0 0 24 24">
            <path fill="currentColor" d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
            </svg>
        </div>

        {#if showLoadingAnimation}
            <div style="position: absolute; top: 6px; left: 25.7rem;">
                <LoadingAnimation size="small" />
            </div>
        {/if}
    </div>

    <div style="float:left; margin: 10px 0 0 10px;">
        <input type="checkbox" style="vertical-align: -2px;" bind:checked={searchInInterval} on:change={() => setupSearchInInterval()}>
        <label>Search within interval</label>
    </div>

    {#if searchInInterval}
    <div style="float:left; margin: 4px 0 0 25px;">
        <label class="form-label" for="chromosome-selector">Chromosome: </label>
        <select class="divbrowse-form-control" bind:value={selectedChromosome} on:change|preventDefault="{() => setupSearchInInterval()}">
            {#each controller.metadata.chromosomes as chromosome}
            <option value="{chromosome.id}">{chromosome.label}</option>
            {/each}
        </select>
    </div>

    <div style="float:left; margin: 0 0 0 10px;">
        <label class="form-label" for="startpos">Start: </label>
        <input bind:value={startpos} on:keyup|preventDefault="{() => debouncedSetupSearchInInterval()}" type="number" id="startpos" class="divbrowse-form-control" style="width:7rem;">
    </div>

    <div style="float:left; margin: 0 0 0 10px;">
        <label class="form-label" for="endpos">End: </label>
        <input bind:value={endpos} on:keyup|preventDefault="{() => debouncedSetupSearchInInterval()}" type="number" id="endpos" class="divbrowse-form-control" style="width:7rem;">
    </div>
    {/if}

    <div style="clear:left"></div>


    {#if result !== false}
    <div class="box" style="margin-top:15px; background: rgb(242,242,242);padding: 10px;">
        <h3 style="font-weight:bold;margin-bottom:20px;font-size:1.1rem;padding:0;margin-top:0px;">Search result</h3>
        <p>{resultRowCount} genes were found that match your search query.</p>


        <Datatable  settings={datatableSettings} data={result}>
            <thead>
                <th data-key="id">ID</th>
                <th data-key="description">Description</th>
                <th data-key="seqid">Chromosome</th>
                <th data-key="start">Start position</th>
                <th data-key="end">End position</th>
                <th data-key="primary_confidence_class">Primary confidence class</th>
                {#if controller.metadata.gff3.count_exon_variants !== undefined && controller.metadata.gff3.count_exon_variants === true}
                <th data-key="number_of_variants">Number of SNPs / Exon-SNPs</th>
                {/if}
                <th></th>
            </thead>
            <tbody>
                {#each $rows as row}
                <tr>
                    <td class="id" style="width:230px;"><a href="#" on:click|preventDefault={openGeneDetailsModal(row.ID)}>{row.ID}</a></td>
                    <td class="desc" style="width:330px;">{row.description}</td>
                    <td class="centered">{row.seqid}</td>
                    <td class="centered">{row.start}</td>
                    <td class="centered">{row.end}</td>
                    <td class="centered">{row.primary_confidence_class}</td>
                    {#if controller.metadata.gff3.count_exon_variants !== undefined && controller.metadata.gff3.count_exon_variants === true}
                    <td class="centered">{row.number_of_variants} / {row.number_of_exon_variants}</td>
                    {/if}
                    <td><a href="#" on:click|preventDefault={ () => goToPos(row.seqid, row.start, row.end) }>show</a></td>
                </tr>
                {/each}
            </tbody>
        </Datatable>
        
    </div>
    {/if}


</div>

<style>

.centered {
    text-align: center;
}

:global(section.dt-pagination) {
    font-size: 0.85rem;
    padding-top: 20px !important;
}

:global(section.datatable table) {
    border-collapse: collapse;
    width: 99%;
    font-size: 0.8rem;
}


:global(section.datatable table th) {
    font-size: 0.80rem;
    padding: 3px 15px 3px 15px;
}

:global(section.datatable table td) {
    font-size: 0.80rem;
    border-top: 1px solid rgb(120,120,120);
    border-bottom: 1px solid rgb(120, 120, 120);
    padding: 5px 10px 5px 10px;
}

:global(section.datatable table tr:hover td) {
    background: white;
}

:global(section.datatable table td.id) {
    width: 230px;
}

:global(section.datatable table td.desc) {
    width: 450px;
}

:global(section.dt-pagination-buttons button) {
    padding: 3px 14px 3px 14px;
    background: white;
    border: 1px solid rgb(90,90,90);
    line-height: 0.8rem !important;
}

:global(section.dt-pagination-buttons button.active) {
    background: rgb(200,200,200);
}

:global(.dt-pagination-rowcount) {
    padding-top: 15px;
}

</style>