<script>
export let featureId;

import { getContext } from 'svelte';

const context = getContext('app');
let { appId, controller } = context.app();

import getStores from '@/utils/store';
let store = getStores().genesBookmarks;

console.log(store);

/*const localStorageKey = appId+'-genes-bookmarks';
const bookmarkedGenes = localStorage.getItem(localStorageKey);

if (bookmarkedGenes !== null) {
    const bookmarkedGenesSet = new Set(JSON.parse(bookmarkedGenes));
    store.set(bookmarkedGenesSet);
}*/

let isGeneBookmarked = false;
$: isGeneBookmarked = $store.has(featureId);
$: console.log($store);



const df = controller.metadata.gff3._dataframe;
let filtered = df.filter(row => row.get('ID').includes(featureId) === true);
let result = filtered.toCollection()[0];
let goTerms = result.Ontology_term.split(',');

let oLinkTemplate = controller.metadata.gff3.external_link_ontology_term;
let ontologyLinks = [];
if (oLinkTemplate !== '' && oLinkTemplate !== null && oLinkTemplate !== false) {
    for (let term of goTerms) {
        ontologyLinks.push({
            url: oLinkTemplate.replace('{ID}', term),
            text: term
        });
    }
}



let externalLinks = [];
if (Array.isArray(controller.metadata.gff3.external_links) && controller.metadata.gff3.external_links.length > 0) {
    for (let link of controller.metadata.gff3.external_links) {
        externalLinks.push({
            url: link.url.replace('{FEATURE_ID}', result[link.feature_attribute]),
            text: link.linktext
        });
    }
}


</script> 
 

<div style="min-height: 400px; font-size: 90%;">
    <div class="divbrowse-modal-dialogue-headline">
        Gene Details
        {#if isGeneBookmarked}
        <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="rgb(0,0,255)" stroke="rgb(0,0,255)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-star"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
        {/if}
    </div>

    <!--
    {#if isGeneBookmarked}
    <strong>Bookmarked!</strong>
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="#000" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-star"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
    {:else}
    <a href="#" on:click|preventDefault={ () => bookmarkGene(result.ID) }>Bookmark</a>
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-star"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
    {/if}
    -->

    <table>
        <tr>
            <td>ID</td>
            <td>{result.ID}</td>
        </tr>
        <tr>
            <td>Type</td>
            <td>{result.type}</td>
        </tr>
        <tr>
            <td>Chromosome</td>
            <td>{result.seqid}</td>
        </tr>
        <tr>
            <td>Position</td>
            <td>{result.start} - {result.end}</td>
        </tr>
        <tr>
            <td>Strand</td>
            <td>{result.strand}</td>
        </tr>
        <tr>
            <td>Description</td>
            <td>{result.description}</td>
        </tr>

        {#if controller.metadata.gff3.key_confidence !== undefined && controller.metadata.gff3.key_confidence !== false}
        <tr>
            <td>Primary confidence class</td>
            <td>{result.primary_confidence_class}</td>
        </tr>
        {/if}

        {#if controller.metadata.gff3.count_exon_variants !== undefined && controller.metadata.gff3.count_exon_variants === true}
        <tr>
            <td>Variants on whole gene</td>
            <td>{result.number_of_variants}</td>
        </tr>
        <tr>
            <td>Variants on exons of this gene</td>
            <td>{result.number_of_exon_variants}</td>
        </tr>
        {/if}
    </table>

    {#if externalLinks.length > 0}
    <div class="links">
        <p style="margin-bottom: 5px;"><strong>External Links</strong></p>
        <p>
        {#each externalLinks as link}
        <a target="_blank" href="{link.url}">{link.text}</a><br />
        {/each}
        </p>
    </div>
    {/if}

    {#if ontologyLinks.length > 0}
    
    <div class="links">
        <p style="margin-bottom: 5px;"><strong>GO Terms</strong></p>
        <p class="goterms" style="width: 550px;overflow-wrap:normal;">
            {#each ontologyLinks as o}
            <span><a target="_blank" href="{o.url}">{o.text}</a></span>&ensp;
            {/each}
        </p>
    </div>
    {/if}


    <div style="margin-top: 15px;">
    {#if isGeneBookmarked}
    <button disabled={false} on:click|preventDefault={() => store.unbookmarkGene(result.ID)} class="divbrowse-btn divbrowse-btn-light">Remove from my favorite genes</button>
    {:else}
    <button disabled={false} on:click|preventDefault={() => store.bookmarkGene(result.ID)} class="divbrowse-btn divbrowse-btn-light">Add to my favorite genes</button>
    {/if}
    </div>
    
</div>

<style>

p.goterms span {
    margin-right: 10px;
}

table {
    width: 100%;
    border-spacing: 0px;
    border-collapse: collapse;
    border: 1px solid rgb(150,150,150);
}

table tr td {
    vertical-align: top;
    border-top: 0px solid rgb(120,120,120);
    border-bottom: 0px solid rgb(120,120,120);
    border-collapse: collapse;
    padding: 5px 6px;
    margin: 0px;
}

table tr:nth-child(odd) {
    background: rgb(240,240,240);
}

table tr td:nth-child(1) {
    
}

div.links {
    margin-top: 20px;
    border: 1px solid rgb(150,150,150);
    padding: 6px;
}

div.links p {
    margin: 0;
    padding: 0;
}
</style>