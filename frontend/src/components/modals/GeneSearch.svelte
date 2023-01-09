<script>
    export let close;
    
    import { getContext, onMount, afterUpdate } from 'svelte';
    
    const context = getContext('app');
    let { controller } = context.app();
    
    import getStores from '@/utils/store';
    const { snpPosHighlights } = getStores();
    
    import { debounce } from '@/utils/helpers';
    
    import LoadingAnimation from '@/components/utils/LoadingAnimation.svelte';
    let showLoadingAnimation = false;

    import GeneSearchModalTable from '@/components/modals/GeneSearchModalTable.svelte';
    
    //import Fuse from 'fuse.js'


    const flip = obj => Object.assign({}, ...Object.entries(obj).map(([a,b]) => ({[b]: a })));
    const chromMap = flip(controller.metadata.gff3.gff3_to_vcf_chromosome_mapping);



    let query = '';
    let result = null;
    let resultRowCount = null;


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
    //let data = null;
    let showGenesFoundText = false;

    import { writable } from "svelte/store";

    const data = writable([]);



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
        let df_result = df.filter(row => clean(row.get('description')).includes( queryCleaned ) === true || clean(row.get('ID')).includes( queryCleaned ) === true);
        result = df_result.toCollection();
        $data = result;

        resultRowCount = result.length;
        showLoadingAnimation = false;
        showGenesFoundText = true;
    }

    const debouncedDoSearch = debounce(doSearch, 750);
    const debouncedSetupSearchInInterval = debounce(setupSearchInInterval, 500);

    $: debouncedDoSearch(query);


    onMount(async () => {
        df = controller.metadata.gff3._dataframe;
        //data = df.toCollection();
        //result = df.toCollection();
        result = controller.metadata.gff3._collection;
        $data = result;//.slice(0,5000);
    });

    let showTable = false;
    let domUpdates = 0;

	afterUpdate(async () => {
        domUpdates++;
        if (domUpdates > 1) {
            showTable = true;
        }
	});

</script>

<div id="container" style="min-height: 600px; width: 70vw;">

    <div class="divbrowse-modal-dialogue-headline">Gene Search</div>

    <div style="display: flow-root; font-size: 90%;">
   
        <div style="position: relative; float:left;">
            <input type="text" bind:value={query} placeholder="The ID and the description can be searched..." style="font-size: 1rem; padding-left: 35px; width: 25rem; height: 36px;" class="divbrowse-form-control">
            <div style="position: absolute; top: 7px; left: 6px;">
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
            <input id="search-in-genomic-region" type="checkbox" style="vertical-align: -2px;" bind:checked={searchInInterval} on:change={() => setupSearchInInterval()}>
            <label for="search-in-genomic-region">Search within genomic region</label>
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

        <div style="float:left; margin: 4px 0 0 10px;">
            <input bind:value={startpos} placeholder="start position" on:keyup|preventDefault="{() => debouncedSetupSearchInInterval()}" type="number" id="startpos" class="divbrowse-form-control pos" style="width:7rem;">
        </div>

        <div style="float:left; margin: 4px 0 0 10px;">
            <input bind:value={endpos} placeholder="end position" on:keyup|preventDefault="{() => debouncedSetupSearchInInterval()}" type="number" id="endpos" class="divbrowse-form-control pos" style="width:7rem;">
        </div>
        {/if}

    </div>

    <p>
        {#if query.length > 0 && resultRowCount !== null && showGenesFoundText}
        {resultRowCount} genes were found that match your search query.
        {/if} &nbsp;
    </p>


    {#if result !== null}

    <div id="results">

        {#if showTable}
        <GeneSearchModalTable data={data} {close} />
        {:else}
        <div style="border: 0px solid black; display: flex; justify-content: center;">
            <LoadingAnimation size="small" />
        </div>
        {/if}

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
    font-size: 80%;
}

</style>