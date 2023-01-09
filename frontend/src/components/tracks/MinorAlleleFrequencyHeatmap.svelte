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

let scale = scaleLinear().domain([0, 0.5]).range([1, 0]);


const tippyProps = {
    delay: 0,
    appendTo: rootElem,
    target: 'div#'+appId+' span.maf-indicator',
    animation: false,
    placement: "bottom",
    allowHTML: true
};


let mafs;
let tippyInstance;

$: {
    mafs = data.per_variant_stats.maf;
    
    if (tippyInstance !== undefined && typeof tippyInstance.destroy === "function") {
        tippyInstance.destroy();
    }

    tippyInstance = delegate(rootElem.querySelector('#tracks-container'), tippyProps);
}

</script>


<div class="track mafvis" style="height: 20px; margin-top: 1px;"><div class="label">MAF indicator</div>
    {#each mafs as maf, i}
    <span class="variant-hover maf-indicator" data-tippy-content="MAF = {(maf).toFixed(3)}" data-position="{data.variants_coordinates[i]}" style="background-color: rgba(220,0,0, { scale(maf) }); width: {$variantWidth}px;">&nbsp;</span>
    {/each}
</div>


<style>

</style>