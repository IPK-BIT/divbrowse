<script>
    export let close;
    
    import { getContext, onMount, afterUpdate } from 'svelte';
    
    const context = getContext('app');
    let { controller } = context.app();

    import { debounce } from '@/utils/helpers';
    
    import getStores from '@/utils/store';
    const stores = getStores();
    let store = stores.geneSearch;

    if (!$store.selectedChromosome) {
        $store.selectedChromosome = controller.chromosome;
    }

    import { writable } from 'svelte/store';
    const data = writable([]);
   
    
    import LoadingAnimation from '@/components/utils/LoadingAnimation.svelte';
    let showLoadingAnimation = false;

    import GeneSearchModalTableFast from '@/components/modals/GeneSearchModalTableFast.svelte';
    
    //import Fuse from 'fuse.js'


    const flip = obj => Object.assign({}, ...Object.entries(obj).map(([a,b]) => ({[b]: a })));
    const chromMap = flip(controller.metadata.gff3.gff3_to_vcf_chromosome_mapping);


    let result = null;
    let resultRowCount = null;


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
    let showGenesFoundText = false;


    const clean = (query) => query.replace('-', ' ').toLowerCase();

    function doSearch(_query) {

        df = controller.metadata.gff3._dataframe;
        if ($store.searchInInterval === true) {
            let _chrom = chromMap[$store.selectedChromosome];
            df = df.filter(row => row.get('seqid') === _chrom);
            if ($store.startpos !== undefined && $store.startpos > 0) {
                df = df.filter(row => row.get('start') >= $store.startpos);
            }
            if ($store.endpos !== undefined && $store.endpos > 0) {
                df = df.filter(row => row.get('end') <= $store.endpos);
            }

            //fuse = new Fuse(df.toCollection(), fuseOptions);
        }

        let query = $store.query;

        if (query === '') {
            result = df.toCollection();
            $data = result;
            resultRowCount = result.length;
            showLoadingAnimation = false;
            showGenesFoundText = false;
            return false;
        }
        showLoadingAnimation = true;
        //let resultFuzzy = fuse.search(query);
        //result = resultFuzzy.map(x => x.item);

        let queryCleaned = clean(query);
        df = df.filter(row => clean(row.get('description')).includes( queryCleaned ) === true || clean(row.get('ID')).includes( queryCleaned ) === true);
        result = df.toCollection();
        $data = result;

        resultRowCount = result.length;
        showLoadingAnimation = false;
        showGenesFoundText = true;
    }

    const debouncedDoSearch = debounce(doSearch, 750);

    function saveResultAsCsv() {
        let strCSV = df.toCSV(true);
        const a = document.createElement('a');
        a.href = URL.createObjectURL(new Blob([strCSV], {
            type: 'text/csv'
        }));
        a.setAttribute('download', 'genes.csv');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    onMount(async () => {
        df = controller.metadata.gff3._dataframe;
        //data = df.toCollection();
        //result = df.toCollection();
        result = controller.metadata.gff3._collection;
        $data = result;//.slice(0,5000);

        doSearch();
    });

    /*let showTable = false;
    let domUpdates = 0;

	afterUpdate(async () => {
        domUpdates++;
        if (domUpdates > 1) {
            showTable = true;
        }
	});*/

</script>

<div id="container" style="min-height: 600px; width: 70vw;">

    <div class="divbrowse-modal-dialogue-headline">Gene Search</div>

    <div style="display: flow-root;">
   
        <div style="position: relative; float:left;">
            <input type="text" bind:value={$store.query} on:keyup|preventDefault="{() => debouncedDoSearch()}" placeholder="The ID and the description can be searched..." style="font-size: 110%; padding-left: 35px; width: 420px; height: 36px;" class="divbrowse-form-control">
            <div style="position: absolute; top: 7px; left: 6px;">
                <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
                </svg>
            </div>

            {#if showLoadingAnimation}
                <div style="position: absolute; top: 6px; left: 400px;">
                    <LoadingAnimation size="small" />
                </div>
            {/if}
        </div>

        <div style="float:left; margin: 10px 0 0 10px;">
            <input id="search-in-genomic-region" type="checkbox" style="vertical-align: -1.5px;" bind:checked={$store.searchInInterval} on:change={() => doSearch()}>
            <label for="search-in-genomic-region">Search within genomic region</label>
        </div>

        {#if $store.searchInInterval}
        <div style="float:right; margin: 4px 0 0 25px;">
            <label class="form-label" for="chromosome-selector">Chromosome: </label>
            <select class="divbrowse-form-control" bind:value={$store.selectedChromosome} on:change|preventDefault="{() => doSearch()}">
                {#each controller.metadata.chromosomes as chromosome}
                <option value="{chromosome.id}">{chromosome.label}</option>
                {/each}
            </select>

            <input bind:value={$store.startpos} placeholder="start position" on:keyup|preventDefault="{() => debouncedDoSearch()}" type="number" id="startpos" class="divbrowse-form-control pos" style="width:120px;">

            <input bind:value={$store.endpos} placeholder="end position" on:keyup|preventDefault="{() => debouncedDoSearch()}" type="number" id="endpos" class="divbrowse-form-control pos" style="width:120px;">
        </div>
        {/if}

    </div>

    <p>
        {#if $store.query.length > 0 && resultRowCount !== null && showGenesFoundText}
        {resultRowCount} genes were found that match your search query.
        {/if} &nbsp;
    </p>


    {#if result !== null}

    <div id="results">

        
        <!--{#if showTable}
        <GeneSearchModalTable data={data} {close} />
        {:else}
        <div style="border: 0px solid black; display: flex; justify-content: center;">
            <LoadingAnimation size="small" />
        </div>
        {/if}
        -->

        <GeneSearchModalTableFast data={data} {close}>
            <button slot="buttons" disabled={result.length == 0} on:click|preventDefault={saveResultAsCsv} class="divbrowse-btn divbrowse-btn-light">Save result as CSV</button>
        </GeneSearchModalTableFast>

        

        <!--
        {#await import("./GeneSearchModalTable.svelte")}
        <div style="border: 0px solid black; display: flex; justify-content: center;">
            <LoadingAnimation size="small" />
        </div>
        {:then GeneSearchModalTable}
	        <GeneSearchModalTable.default data={data} {close} />
        {/await}
        -->
    </div>

    {/if}

</div>

<style lang="less">

#results {
    background: rgb(242,242,242);
    padding: 20px;
    border-radius: 6px;
}

</style>