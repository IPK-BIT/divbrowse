<script>
export let data;

import { onMount, getContext } from 'svelte';
const context = getContext('app');
let { appId } = context.app();

import getStores from '/utils/store';
const { variantWidth } = getStores();

import { delegate } from 'tippy.js';
//let tippyInstancesReference;

let tippyInstances;
let tippyInstancesInitialized = false;

function isFiltered(pos) {
    if (data.filtered_variants_coordinates.includes( pos ) === false) {
        return 'background-color: rgb(240,240,240);';
    } else {
        return '';
    }
}

const tippyProps = {
    delay: 0,
    target: 'div#'+appId+' span.reference',
    animation: false,
    placement: "bottom",
    allowHTML: true
};

//tippyInstancesReference = delegate('body', tippyProps);

/*onMount(async () => {
    //if (sampleTracksContainer !== undefined) {
        //sampleTracksContainerClassname = sampleTracksContainer.getAttribute('class');
        if (tippyInstancesInitialized === false) {
            tippyInstances = delegate('body', tippyProps);
            tippyInstancesInitialized = true;
        }
    //}
});*/

let reference;

$: {
    reference = data.reference;
    
    if (tippyInstances !== undefined && typeof tippyInstances[0].destroy === "function") { tippyInstances[0].destroy(); }
    tippyInstances = delegate('body', tippyProps);
}

</script>

<div class="track reference"><div class="label">Reference allele</div>
    {#each reference as nucleotide, i}
    {#if nucleotide.length == 1}
    <span class="variant-hover snp reference ref-{nucleotide}" class:noletter={$variantWidth < 10} data-tippy-content="Variant type: SNP<br />Position: {data.variants_coordinates[i]}" data-position="{data.variants_coordinates[i]}" style="width: {$variantWidth}px; {isFiltered(data.variants_coordinates[i])}"></span>
    {:else}
    <span class="variant-hover snp reference ref-indel" class:noletter={$variantWidth < 10} data-tippy-content="Variant type: INDEL<br />Position: {data.variants_coordinates[i]}" data-position="{data.variants_coordinates[i]}" style="width: {$variantWidth}px; {isFiltered(data.variants_coordinates[i])}"></span>
    {/if}
    {/each}
</div>


<style lang="less">

</style>