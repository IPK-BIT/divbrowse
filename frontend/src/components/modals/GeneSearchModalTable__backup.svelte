<script>
    export let close;
    export let data;
    
    import { getContext, onMount } from 'svelte';
    
    const context = getContext('app');
    let { controller, eventbus } = context.app();
    
    import getStores from '@/utils/store';
    const { snpPosHighlights } = getStores();

    import { Render, Subscribe, createTable, createRender } from 'svelte-headless-table';
    import { addPagination } from 'svelte-headless-table/plugins';

    
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

    function setupTable() {

        const table = createTable(data, {
            page: addPagination({
                initialPageSize: 10,
            }),
        });

        const columns = table.createColumns([
            table.column({
                header: 'ID',
                accessor: 'ID',
            }),
            table.column({
                header: 'Type',
                accessor: 'type',
            }),
            table.column({
                header: 'Description',
                accessor: 'description',
            }),
            table.column({
                header: 'Chromosome',
                accessor: 'seqid',
            }),
            table.column({
                header: 'Start position',
                accessor: 'start',
            }),
            table.column({
                header: 'End position',
                accessor: 'end',
            }),
            table.column({
                header: 'Primary<br>confidence<br>class',
                accessor: 'primary_confidence_class',
            }),
            table.column({
                header: 'Number of <br>variants (on exons)',
                id: '__number_of_variants',
                accessor: (item) => item,
                cell: ({ value }) => value.number_of_variants+' ('+value.number_of_exon_variants+')',
            }),
            table.column({
                header: '',
                id: '__view',
                accessor: (item) => item,
                cell: ({ value }) => value.ID,
            }),
        ]);

        /*const {
            headerRows,
            rows,
            pageRows,
            tableAttrs,
            tableBodyAttrs,
            pluginStates,
        } = table.createViewModel(columns);*/

        let viewModel = table.createViewModel(columns);

        //const { pageIndex, pageCount, pageSize, hasNextPage, hasPreviousPage } = pluginStates.page;
        let statePagination = viewModel.pluginStates.page;

        return { viewModel, statePagination }
    }


    let headerRows, rows, pageRows, tableAttrs, tableBodyAttrs, pluginStates;
    let pageIndex, pageCount, pageSize, hasNextPage, hasPreviousPage;


    let res = setupTable();

    headerRows = res.viewModel.headerRows;
    rows = res.viewModel.rows;
    pageRows = res.viewModel.pageRows;
    tableAttrs = res.viewModel.tableAttrs;
    tableBodyAttrs = res.viewModel.tableBodyAttrs;
    pluginStates = res.viewModel.pluginStates;

    pageIndex = res.statePagination.pageIndex;
    pageCount = res.statePagination.pageCount;
    pageSize = res.statePagination.pageSize;
    hasNextPage = res.statePagination.hasNextPage;
    hasPreviousPage = res.statePagination.hasPreviousPage;


    onMount(async () => {

    });


</script>


<table {...$tableAttrs}>
    <thead>
    {#each $headerRows as headerRow (headerRow.id)}
        <Subscribe rowAttrs={headerRow.attrs()} let:rowAttrs>
        <tr {...rowAttrs}>
            {#each headerRow.cells as cell (cell.id)}
            <Subscribe attrs={cell.attrs()} let:attrs>
                <th {...attrs} class="{cell.id}">
                {@html cell.render()}
                </th>
            </Subscribe>
            {/each}
        </tr>
        </Subscribe>
    {/each}
    </thead>
    <tbody {...$tableBodyAttrs}>
        {#each $pageRows as row (row.id)}
        <Subscribe rowAttrs={row.attrs()} let:rowAttrs>
            <tr {...rowAttrs}>
                {#each row.cells as cell (cell.id)}
                <Subscribe attrs={cell.attrs()} let:attrs>
                    <td {...attrs} class="{cell.id}">
                        {#if cell.id == 'ID'}
                            <a href="#" on:click|preventDefault={openGeneDetailsModal(cell.value)}><Render of={cell.render()} /></a>
                        {:else if cell.id == 'description'}
                        <abbr title={cell.value}><Render of={cell.render()} /></abbr>
                        {:else if cell.id == '__view'}
                            <a href="#" on:click|preventDefault={ () => goToPos(cell.value.seqid, cell.value.start, cell.value.end) }>view</a>
                        {:else}
                            <Render of={cell.render()} />
                        {/if}
                    </td>
                </Subscribe>
                {/each}
            </tr>
            </Subscribe>
        {/each}
    </tbody>
</table>

<div style="margin-top:15px; text-align: right;">
    <button on:click={() => $pageIndex--} disabled={!$hasPreviousPage} class="divbrowse-btn divbrowse-btn-light">Previous page</button>
    <span style="padding: 0 20px;">Page {$pageIndex + 1} out of {$pageCount}</span>
    <button on:click={() => $pageIndex++} disabled={!$hasNextPage} class="divbrowse-btn divbrowse-btn-light">Next page</button>
</div>


<style lang="less">

table {
    width: 100%;
    border: 0px solid black;
    border-collapse: collapse;
    /*font-size: 100%;*/
}

table thead tr th {
    padding: 0 5px 10px 0;
    border-bottom: 1px solid rgb(170,170,170);
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

</style>