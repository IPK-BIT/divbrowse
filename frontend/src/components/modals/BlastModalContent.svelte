<script>
export let close;

import { getContext } from 'svelte';

const context = getContext('app');
let { controller } = context.app();

import getStores from '/utils/store';
const { snpPosHighlights } = getStores();

import LoadingAnimation from '/components/utils/LoadingAnimation.svelte';
let showLoadingAnimation = false;

let doCalcBtnDisabled = false;

let params = {
    query: '',
}


function exampleQuery() {
    let query = '';
    query = 'AATAAAAGGCAGTCACACACTAGTTACTTCCACACATCTCACCCAGTTTCAGGCAGTGCAAGCACCTTGG';
    query += 'AGGGAACAAAACAAGTGTACACATGGCGAGCACAAGCTTGTGTATGTGCTTCTTCCTCGTGTTTCTTGGA';
    query += 'CTGTCCTTCAATTTGGCACTCGGCCAAGTCCTATTTCAGGGCTTCAACTGGGAATCCTGGAAGCAGAACG';
    query += 'GGGGATGGTACAAATTCCTGATGGACAAGGTGGACGACATCGCCGAGGCCGGCATCACCCACGTCTGGCT';
    query += 'CCCTCCGCCGTCGCACTCTGTCGCCGAGCAAGGCTACCTGCCGGGGCGCCTGTACGATCTTGATGCGTCC';
    query += 'AAGTACGGCAACAAGGCGCAGCTCAAGTCCCTGATCAAGGCGTTCCACGACAAGGGCGTCAAGGTCATCG';
    query += 'CCGACATCGTCATCAACCACCGCACGGCGGAGCACAAGGACGGCCGCGGCATCTACTGCCTCTTCGAGGG';
    query += 'CGGCACGTCGGACTCCCGCCTCGACTGGGGCCCCCACATGATCTGCAGGGACGACAAGGCGTACTCCGAT';
    query += 'GGAACGGGGAACCTCGACACCGGCCTGGACTTTCCCGGCGCACCGGACATCGACCACCTCAACAAGCGCG';
    query += 'TCCAGCGCGAGCTCATCGGCTGGCTCAAATGGCTCCAGACGGACATCGGCTTCGACGCGTGGCGCCTCGA';
    query += 'CTTCGCCAAGGGCTACTCCGCTGAGGTTGCCAAGATCTTTATCGACAACGCCAAGCCCTCGTTCGCCGTC';
    query += 'GCCGAGCTGTGGAGCTCGCTGGCCTACGGCGGCGACGGCAAGCCTTTGCAGGACCAGAACGCGCACCGGC';
    query += 'AGGAGCTGGTGAACTGGGTGGATCGTGTCGGCGGCAAGGCCAGCCCGGCCACGACGTTCGACTTCACCAC';
    query += 'CAAGGGCATCCTCAACGTCGCCGTCGATGGCGAGCTGTGGAGGCTGCGCGGCGCCGACGGCAAGGCGCCT';
    query += 'GGTATGATTGGGTGGTGGCCGGCCAAGGCCGTCACCTTCGTCGACAACCACGACACTGGCTCCACGCAGC';
    query += 'ACATGTGGCCTTTCCCCGCAGACAAGGTCATTCAGGGCTACGCCTACATCCTCACACACCCGGGGAACCC';
    query += 'GTGCATCTTCTACGATCATTTCTTCGACTCGGGCCTCAAGAATGAGATCGCGCAACTGGTGTCCATCAGG';
    query += 'AACCGCCACGGGATCCAGCCGGACAGCAAGCTGCGCATCATCAAGGCCGACGCAGACCTGTACCTCGCTG';
    query += 'AGATCGACGACAAGGTCATCGTGAAGATCGGGCCAAGATTCGGTGCTTCGCAGCTCATCCCAGGAGGCTT';
    query += 'CCAGGTCGTAGCGCACGGAAATGGCTACGCCGTCTGGGAGAAAATCTGAGCCAAATTTGTGCCTCGTCCG';
    query += 'GGACGAAGAGTTTTAGCAGATTGGACCTGCATTTTTCCTAGCTTACTTCTAATACGGGATAGCTACAGCC';
    query += 'TGTATTCGAGAATAAGCACTTCATCTGTTAACAACGCGAGGATGAGGGGCATACATACATTAATTTGAGG';
    query += 'AATAATTTGAGGGCCACACTGGATCATATGATGAACGCTCTGTCACAGGGGACAAAGCCATGCGTTTTTT';
    query += 'TCAGCCCGTTTCATTTGCAACCTCTACCAAATCAATTTATTTGATATCCTTTACTCGAAAACACTTCAGT';
    query += 'GAGGTCACTTACCATCATGTTCTCGAGTGAGAGTTACCCTCTTGTGCATTGAAATACTCTTGCTTAGGGG';
    query += 'GTATTTGGCACTGCTCCACAAACTCTACTATGGAGCAGCTCTAAAAAAAAACTGGAATTCGTGGAGTACC';
    query += 'TCTTCAGCTTTTTTTTCTTGAATTGAATACGTAGAGCTGAAACTGTTTGGCTAAAAAACGTAGAGCAAAA';
    query += 'CTGAAAAACGTGAAGCAGAGCAGTCCCAAACACCCTCTAACTCTCTCAAGATGCAATGAACACCTTCAAA';
    query += 'GTGCCATGGAGATGGAGAATAACCAGAGTGCCACGACCAATCACCATTCACCATTGGGTAAGTAGTAGCA';
    query += 'GGACCATTGACAGGGCAGCGTGTTACTTTATTTATCGGCATTCTCTGTAACGTGAATAAGGGGACATATT';
    query += 'CTTTTTTGCTACGACAATAC';
    return query;
}

//let query = exampleQuery();
let query = '';


let blastResult = controller.lastBlastResult;
let blastResultHistory = controller.blastResultHistory;
let selectedPastBlastResult = '';

if (blastResultHistory.length > 0) {
    selectedPastBlastResult = blastResultHistory.slice(-1)[0].timestamp;
}

const doCalculation = () => {
    if (query === '') {
        return false;
    }

    doCalcBtnDisabled = true;
    showLoadingAnimation = true;

    controller.blast(query, result => {
        console.log(result);
        showLoadingAnimation = false;
        doCalcBtnDisabled = false;
        blastResult = result;
        blastResultHistory = controller.blastResultHistory;
        selectedPastBlastResult = blastResultHistory.slice(-1)[0].timestamp;
    });

};


function goToPos(chrom, startpos, endpos) {
    close();
    controller.goToChromosomeAndPosition(chrom, startpos)
    snpPosHighlights.set({startpos: startpos, endpos: endpos});
}

function reset() {
    query = '';
    blastResult = false;
    selectedPastBlastResult = '';
}


function handleChangeBlastResult(selectedPastBlastResultTimestamp) {
    for (let _result of blastResultHistory) {
        if (_result.timestamp === selectedPastBlastResultTimestamp) {
            blastResult = _result.blast_hits;
        }
    }
}

</script> 
 

<div>
    <div class="divbrowse-modal-dialogue-headline">BLAST</div>


    {#if blastResult !== false || blastResultHistory.length > 1}
    <div class="clearfix" style="margin-bottom: 10px; padding-bottom: 10px; border-bottom: 2px solid rgb(190,190,190);">

        {#if blastResult !== false}
        <button type="button" on:click|preventDefault={reset} class="divbrowse-btn divbrowse-btn-light" style="float:left; margin-right:80px;">Perform another BLAST search</button>
        {/if}


        {#if blastResultHistory.length > 1}
        <div style="float: left;">
        Display one of your previous BLAST search results: 
        <select class="divbrowse-form-control" bind:value={selectedPastBlastResult} on:change|preventDefault="{handleChangeBlastResult(selectedPastBlastResult)}">
            <option disabled hidden value=""></option>
            {#each blastResultHistory as pastBlastResult}
            <option value="{pastBlastResult.timestamp}">{pastBlastResult.timestamp}</option>
            {/each}
        </select>
        </div>
        {/if}

    </div>
    {/if}

    {#if blastResult === false}
    <div class="form-inline" style="">
        <label class="form-label" for="" style="font-size: 1rem; display:block; margin-bottom:4px;">Please enter a query sequence to BLAST with:</label>
        <textarea id="divbrowse-blast-query" bind:value={query}></textarea>

        <div style="margin-top: 5px;" class="clearfix">
            <button type="button" on:click|preventDefault={doCalculation} disabled="{doCalcBtnDisabled}" class="divbrowse-btn divbrowse-btn-light" style="float:left;">Start BLAST search</button>

            {#if showLoadingAnimation}
            <div style="float:left;margin-left:20px;">
                <LoadingAnimation size="small" />
            </div>
            {/if}
        </div>
    </div>
    {/if}


    {#if blastResult !== false}
    <div class="box" style="background: rgb(242,242,242);padding: 10px;">
        <h3 style="font-weight:bold;margin-bottom:20px;font-size:1.2rem;padding:0;margin-top:0px;">Result of the BLAST search:</h3>
        <table id="blast-result" cellpadding="0" cellspacing="0">
        <thead>
            <tr>
                {#if params.database === 'morex_v2.all.cds'}
                <th>Gene / Feature</th>
                {:else}
                <th>Chromosome</th>
                {/if}
                <th>Number of SNPs</th>
                <th>E-value</th>
                <th>Bit score</th>
                <th>Percentage of identical matches</th>
                <th>Alignment length</th>
                <th>Number of mismatches</th>
                <th>Number of gap openings</th>
                <th>Start of alignment in query</th>
                <th>End of alignment in query</th>
                <th>Start of alignment in subject</th>
                <th>End of alignment in subject</th>
                <th></th>
                
            </tr>
        </thead>
        <tbody>
            {#each blastResult as hit}
            <tr>
                {#if params.database === 'morex_v2.all.cds'}
                <td><a href="https://apex.ipk-gatersleben.de/apex/f?p=284:50:::::P50_GENE_NAME:{hit[1]}" target="_blank">{hit[1]}</a></td>
                {:else}
                <td>{controller.metadata.chromosomes[hit.chromosome].label}</td>
                {/if}
                <td>{hit.snp_count}</td>
                <td>{hit.e_value}</td>
                <td>{hit.bit_score}</td>
                <td>{hit.percentage_of_identical_matches} %</td>
                <td>{hit.alignment_length}</td>
                <td>{hit.number_of_mismatches}</td>
                <td>{hit.number_of_gap_openings}</td>
                <td>{hit.start_of_alignment_in_query}</td>
                <td>{hit.end_of_alignment_in_query}</td>
                <td>{hit.start_of_alignment_in_subject}</td>
                <td>{hit.end_of_alignment_in_subject}</td>
                <td><a href="#" on:click|preventDefault={ () => goToPos(hit.chromosome, hit.start_of_alignment_in_subject, hit.end_of_alignment_in_subject) }>show</a></td>
            </tr>
            {/each}
        </tbody>
        </table>
    </div>
    {/if}


</div>

<style>

textarea#divbrowse-blast-query {
    padding: 8px;
    width: 100%;
    min-height: 200px;
    font-size: 0.8rem;
    color: rgb(100,100,100);
    box-sizing: border-box;
}


table#blast-result {
    font-size: 0.85rem;

}

table#blast-result th {
    text-align: center;
    padding: 0;
    margin: 0;
    vertical-align: top;
}

table#blast-result td {
    text-align: center;
    padding: 3px 0px;
    margin: 0;
    border-bottom: 1px solid rgb(140,140,140);
}
</style>