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

    let color = 'rgb(165,165,165)';
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

let size = "20px";
let width = size;
let height = size;
let color = "red";
let viewBox = "0 0 24 24";

</script>


<div class="track snpeff" style="height: 23px;"><div class="label">SnpEff annotations</div>
    {#if data.snpeff_variants !== undefined}
    {#each data.variants_coordinates as position}
    <span on:click|preventDefault={showModal(position)} class="snpeff-indicator-test" data-tippy-content="SnpEff annotation" data-position="{position}" style="width: {$variantWidth}px;">
    <svg width="{width}" height="{height}" viewBox="{viewBox}">
    <path fill="{iconColor(position)}" d="M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z" />
    </svg>
    </span>
    {/each}
    {/if}
</div>


<style>

span.snpeff-indicator-img {
    width: 20px;
    height: 20px;
    background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAQAAAD9CzEMAAABnUlEQVRYw+2XQcrCMBCFP8WN0CLoUroTryC46in0DvYC3XWnJ2hP0Z0uxGPoDRRU0APoyn+ThErbNFoa+MHJcl7mJTN5kwR+9h+sxYSQlD1nXrw4syclZEKrfvAhK068SsaJFcPvg/eJeZQGl+NBTP+b8DPulcHluDP7LHiH5C3Akx0BPiMcHEb4BOx4vmESOqbhu6wzE68EuIU4l4BrBrmma7b6TSa/EY4W7RBl6rQx2UWSWfvUaMfTzD6SKvBcQQ94xjXzOKh5cx1wwE2t3vvoWHhqFzcG5bBY5b44OXKVxYmStYjLVSshUQlCRwCRWl6JupcCcCk9OXoCh4vwL4vcbY7CvShNoZ4AFsJ/pJ13TpRqe193r55S9yTvDIVrW6v7bkWUMO9KhSuoRRCIKGneJaXi1yLwlUxzJiU21kyvKjKMldxyJjXg1iJwlRbsEzSeIpMiVxNoimxyTKsJNMfURGjVBBqhmbSKKgJtq2i82TXeri1cOI1fmRYu/cafLRYeXhaejo0/fi083y18QKx8oSx8Aq18Y3/WvP0BRWMFw2a7DC4AAAAASUVORK5CYII=);
    background-repeat: no-repeat;
    background-size: 20px 20px;
    /*filter: opacity(35%);*/
    filter: sepia(100%) saturate(300%) brightness(70%) hue-rotate(180deg);

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

span.snpeff-indicator-test {
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