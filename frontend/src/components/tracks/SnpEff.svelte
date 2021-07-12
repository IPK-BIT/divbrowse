<script>
export let data;

import { onMount, getContext } from 'svelte';
const context = getContext('app');
let { appId } = context.app();

import getStores from '/utils/store';
const { variantWidth } = getStores();

import { delegate } from 'tippy.js';

import SnpEffAnnotationModalContent from '/components/modals/SnpEffAnnotationModalContent.svelte';
const { open, close } = getContext('simple-modal');


const showModal = (position) => {
    let snpeff_data = data.snpeff_variants[position];
    open(SnpEffAnnotationModalContent, {snpeff_data: snpeff_data, position: position, close: close}, {styleWindow: { width: '99vw' }});
};


const tippyProps = {
    delay: 0,
    target: 'div#'+appId+' span.snpeff-indicator',
    animation: false,
    placement: "right-start",
    allowHTML: true,
    onShow(instance) {
        let currentPos = instance.reference.dataset.position;
        instance.setContent('Please click to display the SnpEff annotation.');
    }
};


function iconColor(position) {
    let snpeff_data = data.snpeff_variants[position];

    if (!Array.isArray(snpeff_data)) {
        snpeff_data = [snpeff_data];
    }

    let hasNonsynonymousSubstitutions = false;
    snpeff_data.forEach(ann => {
        if (ann.includes('missense_variant') || ann.includes('splice_region_variant') || ann.includes('intron_variant') ) {
            hasNonsynonymousSubstitutions = true;
        }
    });

    let color = 'rgb(150,150,150)';
    if (hasNonsynonymousSubstitutions) {
        color = 'rgb(255,35,25)';
    }

    return color;
}


let tippyInstancesSnpeff;

/*$: {
    if (tippyInstancesSnpeff !== undefined && typeof tippyInstancesSnpeff[0].destroy === "function") { tippyInstancesSnpeff[0].destroy(); }
    tippyInstancesSnpeff = delegate('body', tippyProps);
}*/

onMount(async () => {
    if (tippyInstancesSnpeff !== undefined && typeof tippyInstancesSnpeff[0].destroy === "function") { tippyInstancesSnpeff[0].destroy(); }
    tippyInstancesSnpeff = delegate('body', tippyProps);
});

</script>


<div class="track snpeff" style="height: 23px;"><div class="label">SnpEff annotations</div>
    {#if data.snpeff_variants !== undefined}
    {#each data.variants_coordinates as position}
    <span on:click|preventDefault={showModal(position)} class="snpeff-indicator" data-tippy-content="SnpEff annotation" data-position="{position}" style="width: {$variantWidth}px;"><i style="color: {iconColor(position)};" class="material-icons">add_circle_outline</i></span>
    {/each}
    {/if}
</div>


<style>

span.snpeff-indicator i {
    font-size: 16px;
    color:rgb(120,120,120);
    cursor: pointer;
}


span.snpeff-indicator {
    display: inline-block;
    text-align: center;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    min-height: 20px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}


:global(.snpeff-tooltip) {
    font-size: 12px;
    line-height: 1.0em !important;
}

</style>