<script>
import { getContext } from 'svelte';

const context = getContext('app');
let { controller } = context.app();

function sampleDisplayName(sampleId) {
    if (controller.config.sampleDisplayNameTransformer !== undefined && typeof controller.config.sampleDisplayNameTransformer === "function") {
        sampleId = controller.config.sampleDisplayNameTransformer(sampleId);
    }
    return sampleId;
}

</script>

<div>
    <div class="divbrowse-modal-dialogue-headline">Data Summary</div>

    <table>
        <tr>
            <td style="width: 200px;">General description:</td>
            <td>{controller.metadata.dataset_descriptions.general_description}</td>
        </tr>
        {#if controller.metadata.dataset_descriptions.vcf_doi !== ""}
        <tr>
            <td style="width: 200px;">DOI of VCF:</td>
            <td><a href="{controller.metadata.dataset_descriptions.vcf_doi}" target="_blank">{controller.metadata.dataset_descriptions.vcf_doi}</a></td>
        </tr>
        {/if}
        <tr>
            <td style="width: 200px;">DOI of VCF reference genome:</td>
            <td><a href="{controller.metadata.dataset_descriptions.vcf_reference_genome_doi}" target="_blank">{controller.metadata.dataset_descriptions.vcf_reference_genome_doi}</a></td>
        </tr>
        <tr>
            <td style="width: 200px;">DOI of genome annotation:</td>
            <td><a href="{controller.metadata.dataset_descriptions.gff3_doi}" target="_blank">{controller.metadata.dataset_descriptions.gff3_doi}</a></td>
        </tr>
        <tr>
            <td>Number of genotypes:</td>
            <td>{controller.metadata.count_genotypes}</td>
        </tr>
        <tr>
            <td style="width: 200px;">Number of SNP variants:</td>
            <td>{controller.metadata.count_variants}</td>
        </tr>
        <tr>
            <td style="width: 200px;">Number of SNP variants per chromosome:</td>
            <td>
                {#each controller.metadata.chromosomes as chrom}
                {chrom.label}: {chrom.count_snps}<br/>
                {/each}
            </td>
        </tr>
        {#if controller.metadata.gff3.has_gff3 === true}
        <tr>
            <td>Number of genes provided by annotation:</td>
            <td>{controller.metadata.gff3.count_genes}</td>
        </tr>
        {/if}
        <tr>
            <td>Genotypes list:</td>
            <td>
                <div style="height: 400px; overflow-y: scroll; padding-right: 40px;">{@html controller.metadata.samples.map(x => sampleDisplayName(x) ).join('<br />')}</div>
            </td>
        </tr>
    </table>
</div>

<style>

table { 
    border-spacing: 0px;
    border-collapse: collapse;
}

table tr td {
    vertical-align: top;
    border: 1px solid black;
    border-collapse: collapse;
    padding: 5px;
    margin: 0px;
}

</style>