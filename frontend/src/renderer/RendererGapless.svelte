<script>

import { onMount, getContext, afterUpdate } from 'svelte';
const context = getContext('app');
let { appId, eventbus, controller } = context.app();

const rootElem = getContext('rootElem');

import getStores from '@/utils/store';
const { settings, groups, sortSettings, variantFilterSettings, filteredVariantsCoordinates } = getStores();

import { debounce } from '@/utils/helpers';

import DataFrame from 'dataframe-js';
//import tippy from "sveltejs-tippy";
import { delegate } from 'tippy.js';
import Modal from 'svelte-simple-modal';
import VirtualList from '@sveltejs/svelte-virtual-list';

// Import all tracks
import ChromosomeMinimap from '@/components/tracks/ChromosomeMinimap.svelte';
import GenomicRegion from '@/components/tracks/GenomicRegion.svelte';
import Positions from '@/components/tracks/Positions.svelte';
import SnpEff from '@/components/tracks/SnpEff.svelte';
import MinorAlleleFrequencyHeatmap from '@/components/tracks/MinorAlleleFrequencyHeatmap.svelte';
import HeterozygousCallsFrequencyHeatmap from '@/components/tracks/HeterozygousCallsFrequencyHeatmap.svelte';

import Reference from '@/components/tracks/Reference.svelte';
import SampleVariantsMinimap from '@/components/tracks/SampleVariantsMinimap.svelte';
import SampleVariants from '@/components/tracks/SampleVariants.svelte';

import LoadingAnimation from '@/components/utils/LoadingAnimation.svelte';

let data = false;
let samples;
let start;
let end;
let sampleTracksContainer;


function sortSamples(params) {

    let groupColors = ['#F9ACAA', '#FCD9B6', '#FFF9C2', '#A2F5BF', '#A0F0ED', '#BCDEFA', '#B2B7FF', 
        '#FFBBCA', '#EF5753', '#FAAD63', '#FFF382', '#51D88A', '#64D5CA', '#6CB2EB', '#7886D7', '#FA7EA8'];

    let allIds = params.sampleIds;
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
        
        } else {
            // only sample IDs provided => simply sort by the IDs
            if (params.sortSettings.sortorder !== undefined) {
                allIdsUnsorted.sort( (a, b) => a.localeCompare(b) );
                allIdsOut = allIdsUnsorted.slice();
            }
        }

        if (params.sortSettings.sortorder === 'DESC') {
            allIdsOut.reverse();
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

        let color;
        let groupColorMap = {};

        //////let _status = (allIdsGroupRoot.includes(id)) ? 'group-root' : 'single';

        if (allIdsGroupRoot.includes(id)) {
            groupColorMap[id] = groupColors.shift();
            sampleData = {
                status: 'group-root',
                color: groupColorMap[id],
            }
        } else {
            sampleData = {
                status: 'single',
                color: '#FFFFFF',
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

                let isLastNode = false;
                if (i == groupSize) {
                    isLastNode = true;
                }

                sampleData = {
                    status: 'group-node',
                    color: groupColorMap[id],
                    isLastNode: isLastNode
                }
                sorted.push([idNode, sampleData]);
                i += 1;
            }
        }
    }

    return sorted;
}



function setupVariantFilterDataframe(data) {
    if (data === false) return false;
    let df_columns = ['variants_coordinates', 'maf', 'missing_freq', 'heterozygosity_freq', 'vcf_qual'];
    let df_data = {
        variants_coordinates: data.variants_coordinates,
        maf: data.per_variant_stats.maf,
        missing_freq: data.per_variant_stats.missing_freq,
        heterozygosity_freq: data.per_variant_stats.heterozygosity_freq,
        vcf_qual: data.per_variant_stats.vcf_qual,
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
    return filteredVariantsCoordinatesArray;
}



let preloaded = new Set();

function preloadVariantCalls(samples) {
    let key = data.coordinate_first+'-'+data.coordinate_last;
    if (!preloaded.has(key)) {
        let numberToLoad = 1000;
        if (numberToLoad > samples.length) {
            numberToLoad = samples.length;
        }
        let sampleIds = samples.slice(0, numberToLoad).map(elem => elem[0]);
        controller.DataLoader.lazyLoadVariantCalls(sampleIds);
        preloaded.add(key);
    }
}

function lazyLoadVariantCalls(samples) {
    if (start !== undefined && end !== undefined) {
        if ($settings.statusShowMinimap === false && samples !== undefined && samples.length > 0) {
            let sampleIds = samples.slice(start, end).map(elem => elem[0]);
            controller.DataLoader.lazyLoadVariantCalls(sampleIds);
        }
    }
}

let numberOfAlternateAlleles;

function dataChanged() {

    if (data !== false && data.error === undefined) {

        // Apply/add variant filter data
        data.filtered_variants_coordinates = getFilteredVariants(setupVariantFilterDataframe(data));

        samples = sortSamples({
            sampleIds: controller.config.samples, // Object.keys(data.variants)
            distances: data.hamming_distances_to_reference,
            groups: $groups,
            sortSettings: $sortSettings
        });

        lazyLoadVariantCalls(samples);

        preloadVariantCalls(samples);

        data.ref_and_alt = data.alternates.map((variant, idx) => {
            let tmp = variant.slice();
            tmp.unshift(data.reference[idx]);
            return tmp;
        });
    }
}


sortSettings.subscribe(value => {
    dataChanged();
});


const debouncedHandleVariantFilterSettings = debounce(() => dataChanged(), 500);
variantFilterSettings.subscribe(() => {
    debouncedHandleVariantFilterSettings();
});

eventbus.on('data:display:changed', _data => {
    data = _data;
    dataChanged();
});


const tracksScrolledDebounced = debounce((_start) => {
    lazyLoadVariantCalls(samples);
}, 200);


$: tracksScrolledDebounced(start);


let showLoadingAnimation = false;
eventbus.on('loading:animation', msg => {
    showLoadingAnimation = msg.status;
});



/*************************************
 * Tippy related code following
 *************************************/

let tippyProps = {
    delay: 0,
    //appendTo: 'parent',
    //appendTo: document.querySelector('#tracks-container'),
    appendTo: rootElem,
    target: '.'+appId+' span.snp',
    //target: 'span.snp', // tracks-container
    animation: false,
    content: "<span class='tooltip'></span>",
    placement: "bottom",
    allowHTML: true,

    onShow(instance) {
        let currentSampleId = instance.reference.dataset.sampleId;
        let currentPos = instance.reference.dataset.position;
        let currentPosIdx = instance.reference.dataset.positionIndex;

        let content = [];

        // Variant type: SNP
        if (data.reference[currentPosIdx].length > 1) {
            content.push('Variant type: INDEL');
        } else {
            content.push('Variant type: SNP');
        }

        content.push('Position: '+currentPos);
        content.push('Reference Allele: '+data.reference[currentPosIdx]);
        //content.push('Alternate Alleles: '+data.alternates[currentPosIdx][0]);

        let _alternateAlleles = [];
        for (let alternateAllele of data.alternates[currentPosIdx]) {
            if (alternateAllele.length > 0) {
                _alternateAlleles.push(alternateAllele);
            }
        }

        if (_alternateAlleles.length > 1) {
            content.push('Alternate Alleles: '+ _alternateAlleles.join(" / "));
        } else {
            content.push('Alternate Allele: '+ _alternateAlleles.join(" / "));
        }

        let variants = [data.reference[currentPosIdx], ...data.alternates[currentPosIdx]];
        let calls = data.calls.get(currentSampleId)[currentPosIdx];
        let calls_unique = [...new Set(calls)];

        if (calls_unique.length == 1 && calls_unique[0] === -1) {
            content.push('Variant called: none');
        } else {
            let calls_unique_mapped = calls_unique.map((call, index) => { return variants[call] });
            content.push('Variant called: '+ calls_unique_mapped.join(' or '));
        }
        

        if (data.calls_metadata !== undefined) {
            if (data.calls_metadata.DP !== undefined) {
                content.push('DP: '+data.calls_metadata.DP.get(currentSampleId)[currentPosIdx]);
            }
            if (data.calls_metadata.DV !== undefined) {
                content.push('DV: '+data.calls_metadata.DV.get(currentSampleId)[currentPosIdx]);
            }
        }

        instance.setContent(content.join("<br />"));
    }
};

let tippyInstances;
let tippyInstancesInitialized = false;

onMount(async () => {
    if (tippyInstancesInitialized === false) {
        //tippyInstances = delegate('#tracks-container', tippyProps); // 
        tippyInstances = delegate(rootElem.querySelector('#tracks-container'), tippyProps);
        tippyInstancesInitialized = true;
    }
});



let viewport;
eventbus.on('minimap:click', payload => {
    console.log('EVENT: minimap:click');
    viewport.scrollTo(0, payload.y * 23);
});

</script>


<div id="tracks-container" style="position: relative; box-sizing: border-box;">

    {#if showLoadingAnimation}
    <div id="loading-overlay">
        <LoadingAnimation size="large" />
    </div>
    {/if}

    {#if data !== false}
        <ChromosomeMinimap data={data} />

        {#if data.features !== undefined}
        <GenomicRegion data={data} />
        {/if}


        {#if data.snpeff_variants !== undefined}
        <Modal>
            <SnpEff data={data} />
        </Modal>
        {/if}

        <MinorAlleleFrequencyHeatmap data={data} />
        <HeterozygousCallsFrequencyHeatmap data={data} />
        

        <Reference data={data} />

        <div id="sample-tracks-container" class={appId} bind:this={sampleTracksContainer}>

            {#if $settings.statusShowMinimap}
            <SampleVariantsMinimap data={data} samples={samples} />
            {:else}
            <!-- TODO: make itemHeight configureable or dynamically -->
            <VirtualList bind:viewport={viewport} itemHeight={20} items={samples} bind:start bind:end let:item>
                <SampleVariants data={data} item={item} sampleId={item[0]} />
            </VirtualList>
            {/if}

        </div>

    {:else}

        <!--{#if showLoadingAnimation}
        <div style="margin: 20px;">
            <LoadingAnimation />
        </div>
        {:else}-->
        <p style="width: 90%; padding:30px;">Before variants can be displayed, a collection must first be selected.</p>
        <!--{/if}-->
        
    {/if}
</div>


<style lang="less">

#loading-overlay {
    box-sizing: border-box;
    position: absolute;
    z-index: 999;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255,255,255,0.55);
    /*backdrop-filter: saturate(60%);*/
    /*backdrop-filter: blur(2px);*/
    padding: 0;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

#sample-tracks-container {
    /*height:50vh;
    min-height:50vh;*/

    height: 400px;
    min-height: 400px;

    position: relative;
}
</style>