<script>
    export let close;
    export let data;
    
    import { getContext, onMount } from 'svelte';
    
    const context = getContext('app');
    let { controller, eventbus } = context.app();
    
    import getStores from '@/utils/store';
    const { snpPosHighlights } = getStores();

    import { writable } from 'svelte/store';

    const pagination = writable({
        pageSize: 15,
        pages: 1,
        currentPage: 0,
        hasPreviousPage: false,
        hasNextPage: true
    });

    $: $pagination.pages = Math.ceil($data.length / $pagination.pageSize);
    $: $pagination.hasPreviousPage = ($pagination.currentPage > 0) ? true : false;
    $: $pagination.hasNextPage = (($pagination.currentPage + 1) < $pagination.pages) ? true : false;

    function getDataSlice($pagination) {
        let start = ($pagination.currentPage) * $pagination.pageSize;
        let end = ($pagination.currentPage * $pagination.pageSize) + $pagination.pageSize;
        let dataSlice = $data.slice(start, end);
        return dataSlice;
    }

    let dataSlice = [];
    $: dataSlice = getDataSlice($pagination);


    const openGeneDetailsModal = (featureId) => {
        eventbus.emit('modal:open', {
            component: 'GeneDetails',
            props: {
                featureId: featureId
            }
        });
    };

    function goToPos(chrom, startpos, endpos) {
        close();
        let chromMap = controller.metadata.gff3.gff3_to_vcf_chromosome_mapping;
        controller.goToChromosomeAndPosition(chromMap[chrom], startpos)
        snpPosHighlights.set({startpos: startpos, endpos: endpos});
    }

</script>


<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Description</th>
            <th>Chromosome</th>
            <th>Start position</th>
            <th>End position</th>
            <th>Primary<br />confidence<br />class</th>
            {#if controller.metadata.gff3.count_exon_variants !== undefined && controller.metadata.gff3.count_exon_variants === true}
            <th>Number of<br />variants (on exons)</th>
            {/if}
            <th></th>
        </tr>
    </thead>
    <tbody>
        {#each dataSlice as row}
        <tr>
            <td>
                <a href="#" on:click|preventDefault|stopPropagation={openGeneDetailsModal(row.ID)}>{row.ID}</a>
            </td>
            <td>{row.type}</td>
            <td class="description">
                <abbr title={row.description}>{row.description}</abbr>
            </td>
            <td>{row.seqid}</td>
            <td>{row.start}</td>
            <td>{row.end}</td>
            <td>{row.primary_confidence_class}</td>
            {#if controller.metadata.gff3.count_exon_variants !== undefined && controller.metadata.gff3.count_exon_variants === true}
            <td>{row.number_of_variants} ({row.number_of_exon_variants})</td>
            {/if}
            <td>
                <a href="#" on:click|preventDefault|stopPropagation={ () => goToPos(row.seqid, row.start, row.end) }>view</a>
            </td>
        </tr>
        {/each}
    </tbody>
</table>

<div style="margin-top:15px; display: flow-root;">

    <div style="width: 49%; float: left;">
        <slot name="buttons"></slot>
    </div>

    <div style="width: 49%; float: right; text-align: right;">
        <button on:click={() => $pagination.currentPage--} disabled={!$pagination.hasPreviousPage} class="divbrowse-btn divbrowse-btn-light">Previous page</button>
        <span style="padding: 0 20px;">Page {$pagination.currentPage + 1} out of {$pagination.pages}</span>
        <button on:click={() => $pagination.currentPage++} disabled={!$pagination.hasNextPage} class="divbrowse-btn divbrowse-btn-light">Next page</button>
    </div>
</div>


<style lang="less">

table {
    width: 100%;
    border: 0px solid black;
    border-collapse: collapse;
    font-size: 95%;
}

table thead tr th {
    padding: 0 5px 10px 0;
    border-bottom: 1px solid rgb(170,170,170);
    text-align: center;
}

table tbody tr {
    border-bottom: 1px solid rgb(170,170,170);
}

table tbody tr td {
    padding: 4px 10px;
    text-align: center;

    &.description {
        text-align: left;
        width: 250px;
        max-width: 250px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
}

abbr[title] {
    text-decoration: none;
}

a {
    color: blue;
}

</style>