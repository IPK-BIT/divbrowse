<script>
export let sampleId;
export let data;
export let item;

import { getContext } from 'svelte';
const context = getContext('app');
let { controller } = context.app();

// TODO: check if this can be removed
//import Inview from 'svelte-inview';
//let inview_ref;

import getStores from '/utils/store';
const { variantWidth } = getStores();

import { numberOfAltAllelesFactory } from '/utils/helpers';

let coords, ref, alt, sampleData, ref_and_alt;

const ploidy = controller.metadata.ploidy;

$: {
    coords = data.variants_coordinates;
    ref = data.reference;
    alt = data.alternates;
    ref_and_alt = data.ref_and_alt;
    sampleId = item[0];
    sampleData = item[1];
}

const snpClass = numberOfAltAllelesFactory.getFunction(ploidy);

function sampleDisplayName(sampleId, sampleData) {

    if (sampleData.metadata !== undefined) {  
        if (sampleData.metadata.link !== undefined) {
            sampleId = sampleData.metadata.link;
        } else {
            if (sampleData.metadata.displayName !== undefined) {
                sampleId = sampleData.metadata.displayName;
            }
        }
    }

    if (controller.config.sampleDisplayNameTransformer !== undefined && typeof controller.config.sampleDisplayNameTransformer === "function") {
        sampleId = controller.config.sampleDisplayNameTransformer(sampleId);
    }

    return sampleId;
}


function isFiltered(pos, gt) {
    if ( gt.every(el => el < 0) ) {
        return '';
    }
    if (data.filtered_variants_coordinates.includes( pos ) === false) {
        return 'background-color: rgb(255,255,255);';
    } else {
        return '';
    }
}

</script>

<div>
<div class="track">

    {#if sampleData.status == 'single'}
    <div class="label" style="padding-left: 4px;">{@html sampleDisplayName(sampleId, sampleData)}</div>
    {:else if sampleData.status == 'group-root'}
    <div class="label firstNode" style="padding-left: 4px;"><strong>{sampleId}</strong></div>
    {:else}
    <div class="label" class:lastNode={sampleData.isLastNode === true} style="padding-left: 15px;">
        <svg style="position: absolute; top: 0px; left: 0px;" width="15" height="20" xmlns="http://www.w3.org/2000/svg">
            {#if sampleData.isLastNode === true}
            <line x1="5" y1="0" x2="5" y2="11" stroke-width="1" stroke="black" />
            {:else}
            <line x1="5" y1="0" x2="5" y2="20" stroke-width="1" stroke="black" />
            {/if}
            <line x1="5" y1="10" x2="13" y2="10" stroke-width="1" stroke="black" />
        </svg>
        {sampleId}
    </div>
    {/if}
    
    {#if data.filtered_variants_coordinates.length > 0}
    {#each data.filtered_variants_coordinates as variant_coordinate, i}
    
    {#if ploidy === 1}
        <span data-tippy-content="Pos: {coords[i]}" class="snp snp-{snpClass(data.calls[sampleId][i])} ref-{ref_and_alt[i][ data.calls[sampleId][i] ]} alt-{ref_and_alt[i][ data.calls[sampleId][i] ]}" data-sample-id="{sampleId}" data-position="{coords[i]}" data-position-index="{i}" style="width: {$variantWidth}px;"></span>
    {:else if ploidy === 2}
        <span data-tippy-content="Pos: {coords[i]}" class="snp snp-{snpClass(data.calls[sampleId][i])} ref-{ref_and_alt[i][ data.calls[sampleId][i][0] ]} alt-{ref_and_alt[i][ data.calls[sampleId][i][1] ]}" data-sample-id="{sampleId}" data-position="{coords[i]}" data-position-index="{i}" style="width: {$variantWidth}px; {isFiltered(coords[i], data.calls[sampleId][i])}"></span>
    {/if}
    
    {/each}
    {/if}

</div>

<div class="track-separator"></div>



</div>


<style lang="less">

@fontsizeTrackLabel: 12px;

:global {
    div.track div.label {
        width: 170px;
        margin: 0;
        padding: 0;

        /*display: inline-block;
        vertical-align: top;*/
        box-sizing: border-box;
        padding-left: 4px;

        font-size: @fontsizeTrackLabel;
        line-height: @fontsizeTrackLabel;

        display:inline-flex;
        align-items: center;
        min-height: 20px;

        &.firstNode {
            /*box-shadow: inset 0 2px 1px -1px black;*/
        }

        &.lastNode {
            box-shadow: inset 0 -2px 1px -1px rgb(70,70,70);
        }
    }
}

div.label {
    position: relative;

}

/*
:global(div.track div.label.lastNode) {
    box-shadow: 0 4px 2px -2px gray;
}
*/

div.track {
    /*background: rgb(150,150,150);*/
}


div.track-separator {
    height: 1px;
    /*border-top: 1px solid white;
    border-bottom: 1px solid white;*/
    background: rgb(210,210,210);
}

</style>