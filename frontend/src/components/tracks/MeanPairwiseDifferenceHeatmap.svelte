<script>
export let data;

import getStores from '@/utils/store';
const { variantWidth } = getStores();

import { getContext } from 'svelte';

const context = getContext('app');
let { appId } = context.app();

import { scaleLinear } from "d3-scale";

import { delegate } from 'tippy.js';

let scale = scaleLinear().domain([0, 0.1]).range([1, 0]);

const tippyProps = {
    delay: 0,
    target: 'div#'+appId+' span.mpd-indicator',
    animation: false,
    placement: "bottom",
    allowHTML: true
};


let hets;
let tippyInstancesMaf;

$: {
    hets = data.per_variant_stats.mean_pairwise_difference;

    scale = scaleLinear().domain([0, Math.max(...hets) ]).range([1, 0]);
    
    if (tippyInstancesMaf !== undefined && typeof tippyInstancesMaf[0].destroy === "function") { tippyInstancesMaf[0].destroy(); }
    tippyInstancesMaf = delegate('body', tippyProps);
}

</script>


<div class="track mean-pairwise-difference" style="height: 20px;"><div class="label">Pairwise diff. indicator</div>
    {#each hets as het, i}
    <span class="variant-hover mpd-indicator" data-tippy-content="MPD = {(het).toFixed(3)}" data-position="{data.variants_coordinates[i]}" style="background-color: rgba(255, 136, 71, { scale(het) }); width: {$variantWidth}px;">&nbsp;</span>
    {/each}
</div>


<style>

</style>