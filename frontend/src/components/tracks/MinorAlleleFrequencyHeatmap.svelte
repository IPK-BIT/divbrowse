<script>
export let data;

import getStores from '/utils/store';
const { variantWidth } = getStores();

import { getContext } from 'svelte';

const context = getContext('app');
let { appId } = context.app();

import { scaleLinear } from "d3-scale";

import { delegate } from 'tippy.js';

let scale = scaleLinear().domain([0, 0.5]).range([1, 0]);


const tippyProps = {
    delay: 0,
    target: 'div#'+appId+' span.maf-indicator',
    animation: false,
    placement: "bottom",
    allowHTML: true
};


let mafs;
let tippyInstancesMaf;

$: {
    mafs = data.per_snp_stats.maf;
    
    if (tippyInstancesMaf !== undefined && typeof tippyInstancesMaf[0].destroy === "function") { tippyInstancesMaf[0].destroy(); }
    tippyInstancesMaf = delegate('body', tippyProps);
}

</script>


<div class="track mafvis" style="height: 23px;"><div class="label">MAF indicator</div>
    {#each mafs as maf, i}
    <span class="variant-hover maf-indicator" data-tippy-content="MAF = {(maf).toFixed(3)}" data-position="{data.variants_coordinates[i]}" style="background-color: rgba(220,0,0, { scale(maf) }); width: {$variantWidth}px;">&nbsp;</span>
    {/each}
</div>


<style>

:global(.tippy-box) {
    font-family: sans-serif;
}

:global(.tippy-content) {
    font-size: 0.85rem;
    font-family: sans-serif;
}

:global(.tippy-tooltip[data-out-of-boundaries]) {
  opacity: 0;
}

</style>