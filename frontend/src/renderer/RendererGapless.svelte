<script>
export let data;
export let statusShowMinimap;

import { onMount, getContext, afterUpdate } from 'svelte';
const context = getContext('app');
let { appId, eventbus, controller } = context.app();

import getStores from '/utils/store';
const { groups, sortSettings, variantFilterSettings, filteredVariantsCoordinates } = getStores();

import DataFrame from 'dataframe-js';
import tippy from "sveltejs-tippy";
import { delegate } from 'tippy.js';
import Modal from 'svelte-simple-modal';
import VirtualList from '@sveltejs/svelte-virtual-list';

// Import all tracks
import ChromosomeMinimap from '/components/tracks/ChromosomeMinimap.svelte';
import GenomicRegion from '/components/tracks/GenomicRegion.svelte';
import Positions from '/components/tracks/Positions.svelte';
import SnpEff from '/components/tracks/SnpEff.svelte';
import MinorAlleleFrequencyHeatmap from '/components/tracks/MinorAlleleFrequencyHeatmap.svelte';
import Reference from '/components/tracks/Reference.svelte';
import SampleVariantsMinimap from '/components/tracks/SampleVariantsMinimap.svelte';
import SampleVariants from '/components/tracks/SampleVariants.svelte';

import LoadingAnimation from '/components/utils/LoadingAnimation.svelte';


let start;
let end;
let sampleTracksContainer;

const debounce = (callback, wait) => {
    let timeoutId = null;
    return (...args) => {
        window.clearTimeout(timeoutId);
        timeoutId = window.setTimeout(() => {
        callback.apply(null, args);
        }, wait);
    };
}


function sortSamples(params) {

    let groupColors = ['#F9ACAA', '#FCD9B6', '#FFF9C2', '#A2F5BF', '#A0F0ED', '#BCDEFA', '#B2B7FF', 
        '#FFBBCA', '#EF5753', '#FAAD63', '#FFF382', '#51D88A', '#64D5CA', '#6CB2EB', '#7886D7', '#FA7EA8'];

    let allIds = Object.keys(params.variants);
    let allIdsOut = allIds.slice();
    let sorted = [];
    let allIdsInGroup = [];
    let allIdsGroupRoot = [];

    // handle sort settings
    if (params.sortSettings.sortmode === 'alphabetical') {
        
        let allIdsUnsorted = allIds.slice();

        // displayName is provided; if an <a> tag/link is provided the displayName is derived automatically by SnpbrowserController::setSamples()
        if (controller.config.samplesMetadata !== false && Object.values(controller.config.samplesMetadata)[0].displayName !== undefined) {

            // create array of arrays of corresponding pairs of sampleID and displayName
            let pairsIdDisplayName = [];
            allIdsUnsorted.forEach(sampleId => {
                pairsIdDisplayName.push([sampleId, controller.config.samplesMetadata[sampleId].displayName ])
            });

            // sort the pairs based on the displayName (2nd element => array index is 1)
            pairsIdDisplayName.sort( (a, b) => a[1].localeCompare(b[1]) );

            // extract only the sampleIDs
            allIdsOut = pairsIdDisplayName.map(item => item[0]);
            
            if (params.sortSettings.sortorder === 'DESC') {
                allIdsOut.reverse();
            }
        
        } else {
            // only sample IDs provided => simply sort by the IDs
            if (params.sortSettings.sortorder !== undefined) {
                allIdsUnsorted.sort( (a, b) => a.localeCompare(b) );
                allIdsOut = allIdsUnsorted.slice();

                if (params.sortSettings.sortorder === 'DESC') {
                    allIdsOut.reverse();
                }
            }
        }
    }

    if (params.sortSettings.sortmode === 'genetic_distance' && params.sortSettings.sortorder !== undefined) {
        let distances = params.distances.slice();
        distances.sort( (a, b) => { return a[1] - b[1] } );

        if (params.sortSettings.sortorder === 'DESC') {
            distances.reverse();
        }
        allIdsOut = distances.map((elem) => { return elem[0] });
    }

    // remove all samples that are in a group
    if (params.groups !== undefined && Object.keys(params.groups).length > 0 ) {
        allIdsInGroup = Object.values(params.groups).flat();
        allIdsGroupRoot = Object.keys(params.groups);
        for (let id of allIdsInGroup) {
            allIdsOut = allIdsOut.filter(item => item !== id);
        }

        // insert group root sample IDs
        allIdsOut = [...Object.keys(params.groups), ...allIdsOut];
    }

    // sort the sample ID list
    //allIdsOut.sort();

    for (let id of allIdsOut) {
        let sampleData = {};

        let _variants = (params.variants[id] !== undefined) ? params.variants[id] : [];
        let color;
        let groupColorMap = {};

        //////let _status = (allIdsGroupRoot.includes(id)) ? 'group-root' : 'single';

        if (allIdsGroupRoot.includes(id)) {
            groupColorMap[id] = groupColors.shift();
            sampleData = {
                status: 'group-root',
                color: groupColorMap[id],
                variants: []
            }
        } else {
            sampleData = {
                status: 'single',
                color: '#FFFFFF',
                //variants: _variants
            }

            if (controller.config.samplesMetadata !== undefined) {
                if (controller.config.samplesMetadata[id] !== undefined) {
                    sampleData.metadata = controller.config.samplesMetadata[id];
                }
            }
        }

        sorted.push([id, sampleData]);

        if (allIdsGroupRoot.includes(id)) {
            
            let groupMembers = params.groups[id].sort();
            let groupSize = groupMembers.length;
            let i = 1;

            for (let idNode of groupMembers) {
                _variants = (params.variants[idNode] !== undefined) ? params.variants[idNode] : [];

                let isLastNode = false;
                if (i == groupSize) {
                    isLastNode = true;
                }

                sampleData = {
                    status: 'group-node',
                    color: groupColorMap[id],
                    //variants: _variants,
                    isLastNode: isLastNode
                }
                sorted.push([idNode, sampleData]);
                i += 1;
            }
        }
    }

    return sorted;
}

let showLoadingAnimation = false;
eventbus.on('loading:animation', msg => {
    showLoadingAnimation = msg.status;
});

function setupVariantFilterDataframe(data) {
    if (data === false) return false;
    let df_columns = ['variants_coordinates', 'maf', 'missing_freq', 'heterozygosity_freq', 'vcf_qual'];
    let df_data = {
        variants_coordinates: data.variants_coordinates,
        maf: data.per_snp_stats.maf,
        missing_freq: data.per_snp_stats.missing_freq,
        heterozygosity_freq: data.per_snp_stats.heterozygosity_freq,
        vcf_qual: data.per_snp_stats.vcf_qual,
    };
    let df = new DataFrame(df_data, df_columns);
    return df;
}

function getFilteredVariants(df) {
    if ($variantFilterSettings.filterByMaf === true) {
        df = df.filter(row => row.get('maf') >= ($variantFilterSettings.maf[0]) && row.get('maf') <= ($variantFilterSettings.maf[1]) );
    }
    if ($variantFilterSettings.filterByMissingFreq === true) {
        df = df.filter(row => row.get('missing_freq') >= ($variantFilterSettings.missingFreq[0]) && row.get('missing_freq') <= ($variantFilterSettings.missingFreq[1]) );
    }
    if ($variantFilterSettings.filterByHeteroFreq === true) {
        df = df.filter(row => row.get('heterozygosity_freq') >= ($variantFilterSettings.heteroFreq[0]) && row.get('heterozygosity_freq') <= ($variantFilterSettings.heteroFreq[1]) );
    }
    if ($variantFilterSettings.filterByVcfQual === true) {
        df = df.filter(row => row.get('vcf_qual') >= ($variantFilterSettings.vcfQual[0]) && row.get('vcf_qual') <= ($variantFilterSettings.vcfQual[1]) );
    }
    let filteredVariantsCoordinatesArray = df.toArray('variants_coordinates');
    filteredVariantsCoordinates.set(filteredVariantsCoordinatesArray);
    //return df.toArray('variants_coordinates');
    return filteredVariantsCoordinatesArray;
}

function handleVariantFilterSettings(variantFilterSettings) {
    if (data !== false) {
        data = data;
    }
}

const debouncedHandleVariantFilterSettings = debounce(handleVariantFilterSettings, 500);
$: debouncedHandleVariantFilterSettings($variantFilterSettings);

let variants;

$: {
    if (data !== false && data.error === undefined) {

        // Apply/add variant filter data
        data.filtered_variants_coordinates = getFilteredVariants(setupVariantFilterDataframe(data));

        variants = sortSamples({
            variants: data.variants,
            distances: data.hamming_distances_to_reference,
            groups: $groups,
            sortSettings: $sortSettings
        });

        data.ref_and_alt = data.alternates.map((variant, idx) => {
            let tmp = variant.slice();
            tmp.unshift(data.reference[idx]);
            return tmp;
        });
    }
}


let _data;
$: {
    _data = data;
}


let tippyProps = {
    delay: 0,
    appendTo: 'parent',
    target: '.'+appId+' span.snp',
    animation: false,
    content: "<span class='tooltip'></span>",
    placement: "bottom",
    allowHTML: true,

    onShow(instance) {
        let currentSampleId = instance.reference.dataset.sampleId;
        let currentPos = instance.reference.dataset.position;
        let currentPosIdx = instance.reference.dataset.positionIndex;

        let content = [];
        content.push('Position: '+currentPos);
        content.push('Reference Allele: '+_data.reference[currentPosIdx]);

        if (_data.dp !== undefined) {
            content.push('DP: '+_data.dp[currentSampleId][currentPosIdx]);
        }
        if (_data.dv !== undefined) {
            content.push('DV: '+_data.dv[currentSampleId][currentPosIdx]);
        }
        instance.setContent(content.join("<br />"));
    }
};

let tippyInstances;
let tippyInstancesInitialized = false;

onMount(async () => {
    //if (sampleTracksContainer !== undefined) {
        //sampleTracksContainerClassname = sampleTracksContainer.getAttribute('class');
        if (tippyInstancesInitialized === false) {
            tippyInstances = delegate('body', tippyProps);
            tippyInstancesInitialized = true;
        }
    //}

});

let viewport;

eventbus.on('minimap:click', payload => {
    console.log('EVENT: minimap:click');
    viewport.scrollTo(0, payload.y * 23);
});


</script>


<div>
    {#if data !== false}

        <ChromosomeMinimap data={data} />

        {#if data.features !== undefined}
        <GenomicRegion data={data} />
        {/if}

        <Positions data={data} />

        {#if data.snpeff_variants !== undefined}
        <Modal>
            <SnpEff data={data} />
        </Modal>
        {/if}

        <MinorAlleleFrequencyHeatmap data={data} />

        <Reference data={data} />

        <div id="sample-tracks-container" class={appId} bind:this={sampleTracksContainer}>

            {#if statusShowMinimap}
            <SampleVariantsMinimap data={data} variants={variants} />
            {/if}

            <VirtualList bind:viewport={viewport} itemHeight={20} items={variants} bind:start bind:end let:item>
                <SampleVariants data={data} item={item} sampleId={item[0]} />
            </VirtualList>
        </div>

    {:else}

        {#if showLoadingAnimation}
        <div style="margin: 20px;">
            <LoadingAnimation />
        </div>
        {:else}
        <p style="width: 90%; padding:30px;">Before SNPs can be displayed, a collection must first be selected.</p>
        {/if}
        
    {/if}

    
</div>


<style lang="less">
#sample-tracks-container {
    /*height:50vh;
    min-height:50vh;*/

    height: 400px;
    min-height: 400px;

    position: relative;
}
</style>