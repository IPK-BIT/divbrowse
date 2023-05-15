<script>
export let close;

import { getContext } from 'svelte';

const context = getContext('app');
let { controller } = context.app();

import getStores from '@/utils/store';
const { snpPosHighlights } = getStores();

import LoadingAnimation from '@/components/utils/LoadingAnimation.svelte';
let showLoadingAnimation = false;

let doCalcBtnDisabled = false;

let params = {
    query: '',
    blast_type: 'blastn'
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
    if (params.query === '') {
        return false;
    }

    doCalcBtnDisabled = true;
    showLoadingAnimation = true;

    controller.blast(params, result => {
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
 

<div style="width: 70vw;">
    <div class="divbrowse-modal-dialogue-headline">BLAST</div>

    <div style="font-size: 90%; margin-bottom:10px;">
        <span>BLAST type: </span>
        <input type="radio" name="mode" bind:group={params.blast_type} value={'blastn'} id="blastn"> <label for="blastn">blastn</label>
        <input type="radio" name="mode" bind:group={params.blast_type} value={'tblastn'} id="tblastn"> <label for="tblastn">tblastn</label>
    </div>


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
    <div class="form-inline" style="margin-top: 20px;">
        <label class="form-label" for="" style="font-size: 90%; display:block; margin-bottom:6px;">Please enter your query sequence:</label>
        <textarea id="divbrowse-blast-query" bind:value={params.query}></textarea>

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
    <div class="box" id="results" style="">

        <div id="results-inner">
            <h3 style="font-weight:bold;margin-bottom:20px;font-size: 110%;padding:0;margin-top:0px;">Result of the BLAST search:</h3>
            <table id="blast-result" cellpadding="0" cellspacing="0">
            <thead>
                <tr>
                    <th>Chromosome</th>
                    <th>Number of variants</th>
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
                    <th>Strand</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {#each blastResult as hit}
                <tr>
                    <td>{controller.metadata.chromosomesById[hit.chromosome].label}</td>
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
                    <td>
                        {#if hit.end_of_alignment_in_subject > hit.start_of_alignment_in_subject}
                        +
                        {:else}
                        -
                        {/if}
                    </td>
                    <td><a href="#" on:click|preventDefault={ () => goToPos(hit.chromosome, hit.start_of_alignment_in_subject, hit.end_of_alignment_in_subject) }>show</a></td>
                </tr>
                {/each}
            </tbody>
            </table>
        </div>
    </div>
    {/if}


</div>

<style>

#results {
    max-height: 50vh;
    overflow-y: scroll;
}

#results-inner {
    background: rgb(242,242,242);
    border-radius: 6px;
    border: 0px solid blue;
    padding: 20px;
    margin-right: 3px;
}


textarea#divbrowse-blast-query {
    padding: 8px;
    width: 100%;
    min-height: 200px;
    font-size: 90%;
    color: rgb(100,100,100);
    box-sizing: border-box;
}


table#blast-result {
    font-size: 85%;

}

table#blast-result th {
    text-align: center;
    padding: 0 10px 16px 10px;
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