<script>
export let data;

import getStores from '@/utils/store';
const { variantWidth } = getStores();

import { getContext } from 'svelte';

const context = getContext('app');
let { appId } = context.app();

const rootElem = getContext('rootElem');

import { scaleLinear } from "d3-scale";

import { delegate } from 'tippy.js';

let scale = scaleLinear().domain([0, 0.1]).range([0, 1]);

const tippyProps = {
    delay: 0,
    appendTo: rootElem,
    target: 'div#'+appId+' span.het-indicator',
    animation: false,
    placement: "bottom",
    allowHTML: true
};


let hets;
let tippyInstance;

$: {
    hets = data.per_variant_stats.heterozygosity_freq;

    scale = scaleLinear().domain([0, Math.max(...hets) ]).range([0, 1]);
    
    if (tippyInstance !== undefined && typeof tippyInstance.destroy === "function") { 
        tippyInstance.destroy();
    }

    tippyInstance = delegate(rootElem.querySelector('#tracks-container'), tippyProps);
}

</script>


<div class="track heterozygous-calls-freq" style="height: 20px;"><div class="label">Heterozygosity indicator</div>
    {#each hets as het, i}
    <span class="variant-hover het-indicator" data-tippy-content="HET = {(het).toFixed(3)}" data-position="{data.variants_coordinates[i]}" style="background-color: rgba(255, 136, 71, { scale(het) }); width: {$variantWidth}px;">&nbsp;</span>
    {/each}
</div>


<style>

</style>