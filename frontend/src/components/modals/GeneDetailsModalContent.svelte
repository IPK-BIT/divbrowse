<script>
export let featureId;

import { getContext } from 'svelte';

const context = getContext('app');
let { controller } = context.app();


const df = controller.metadata.gff3._dataframe;
let filtered = df.filter(row => row.get('ID').includes(featureId) === true);
let result = filtered.toCollection()[0];
let goTerms = result.Ontology_term.split(',');

let oLinkTemplate = controller.metadata.gff3.external_link_ontology_term;
let ontologyLinks = [];
if (oLinkTemplate !== '' && oLinkTemplate !== null) {
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
 

<div style="min-height: 400px;">
    <div class="divbrowse-modal-dialogue-headline">Gene details</div>

    <table>
        <tr>
            <td>ID</td>
            <td>{result.ID}</td>
        </tr>
        <tr>
            <td>Description</td>
            <td>{result.description}</td>
        </tr>
        <tr>
            <td>Primary confidence class</td>
            <td>{result.primary_confidence_class}</td>
        </tr>
        {#if controller.metadata.gff3.count_exon_variants !== undefined && controller.metadata.gff3.count_exon_variants === true}
        <tr>
            <td>SNPs on whole gene</td>
            <td>{result.number_of_variants}</td>
        </tr>
        <tr>
            <td>SNPs on exons</td>
            <td>{result.number_of_exon_variants}</td>
        </tr>
        {/if}
    </table>

    {#if externalLinks.length > 0}
    <p>External Links:<br />
    {#each externalLinks as link}
    <a target="_blank" href="{link.url}">{link.text}</a><br />
    {/each}
    </p>
    {/if}

    {#if ontologyLinks.length > 0}
    <hr />
    <p class="goterms" style="width: 550px;overflow-wrap:normal;">
        GO Terms:<br />
        {#each ontologyLinks as o}
        <span><a target="_blank" href="{o.url}">{o.text}</a></span>&ensp;
        {/each}
    </p>
    {/if}

</div>

<style>

p.goterms span {
    margin-right: 10px;
}

p {
    font-size: 0.85rem;
}

table { 
    border-spacing: 0px;
    border-collapse: collapse;
    font-size: 0.85rem;
}

table tr td {
    vertical-align: top;
    border: 1px solid black;
    border-collapse: collapse;
    padding: 5px;
    margin: 0px;
}
</style>