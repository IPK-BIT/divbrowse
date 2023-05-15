<script>

import getStores from '@/utils/store';
const { variantFilterSettings } = getStores();

import RangeSlider from "svelte-range-slider-pips";
</script> 
 

<div style="min-height: 500px; min-width: 700px;">
    <div class="divbrowse-modal-dialogue-headline">Filter Variants</div>

    <div class="sortmode" style="margin-top: 30px;">
        <div class="sortmode-option">
            <input id="filterByMaf" type="checkbox" style="vertical-align: -1px;" bind:checked={$variantFilterSettings.filterByMaf}>
            <label for="filterByMaf">Filter by minor allele frequency</label>
        </div>
        {#if $variantFilterSettings.filterByMaf}
        <div style="margin-top: 25px; --range-slider: #d7dada; --range-handle-inactive: rgb(140,140,140); --range-range: rgb(150,150,255);">
            <RangeSlider id="variant-filter-slider" range pushy step={0.01} min={0} max={0.5} bind:values={$variantFilterSettings.maf} />
        </div>
        <div style="margin-top: 25px;">
            Minor allele frequency (MAF) must be between {Math.round($variantFilterSettings.maf[0] * 100)}% and {Math.round($variantFilterSettings.maf[1] * 100)}%
        </div>
        {/if}
    </div>

    <div class="sortmode" style="margin-top: 20px;">
        <div class="sortmode-option">
            <input id="filterByMissingFreq" type="checkbox" style="vertical-align: -1px;" bind:checked={$variantFilterSettings.filterByMissingFreq}>
            <label for="filterByMissingFreq">Filter by missing rate</label>
        </div>
        {#if $variantFilterSettings.filterByMissingFreq}
        <div style="margin-top: 25px; --range-slider: #d7dada; --range-handle-inactive: rgb(140,140,140); --range-range: rgb(150,150,255);">
            <RangeSlider id="variant-filter-slider" range pushy step={0.01} min={0} max={1} bind:values={$variantFilterSettings.missingFreq} />
        </div>
        <div style="margin-top: 25px;">
            Missing rate must be between {Math.round($variantFilterSettings.missingFreq[0] * 100)}% and {Math.round($variantFilterSettings.missingFreq[1] * 100)}%
        </div>
        {/if}
    </div>


    <div class="sortmode" style="margin-top: 20px;">
        <div class="sortmode-option">
            <input id="filterByHeteroFreq" type="checkbox" style="vertical-align: -1px;" bind:checked={$variantFilterSettings.filterByHeteroFreq}>
            <label for="filterByHeteroFreq">Filter by heterozygosity frequency</label>
        </div>
        {#if $variantFilterSettings.filterByHeteroFreq}
        <div style="margin-top: 25px;">
            <RangeSlider id="variant-filter-slider" range pushy step={0.01} min={0} max={1} bind:values={$variantFilterSettings.heteroFreq} />
        </div>
        <div style="margin-top: 25px;">
            Heterozygosity frequency must be between {Math.round($variantFilterSettings.heteroFreq[0] * 100)}% and {Math.round($variantFilterSettings.heteroFreq[1] * 100)}%
        </div>
        {/if}
    </div>


    <div class="sortmode" style="margin-top: 20px;">
        <div class="sortmode-option">
            <input id="filterByVcfQual" type="checkbox" style="vertical-align: -1px;" bind:checked={$variantFilterSettings.filterByVcfQual}>
            <label for="filterByVcfQual">Filter by QUAL value of VCF file</label>
        </div>
        {#if $variantFilterSettings.filterByVcfQual}
        <div style="margin-top: 25px;">
            <RangeSlider id="variant-filter-slider" range pushy step={25} min={0} max={1000} bind:values={$variantFilterSettings.vcfQual} />
        </div>
        <div style="margin-top: 25px;">
            QUAL value must be between {$variantFilterSettings.vcfQual[0]} and {$variantFilterSettings.vcfQual[1]}
        </div>
        {/if}
    </div>


    <div style="clear:left"></div>

</div>

<style>

.sortmode {
    border: 1px solid rgb(180,180,180);
    padding: 15px;
    margin-bottom: 10px;
    background-color: rgb(248,248,248);
    border-radius: 4px;
}

.sortmode .headline {
    font-weight: 500;
    margin-bottom: 15px;
}

.sortmode-option {
    
}

.centered {
    text-align: center;
}



:global(#variant-filter-slider) {
  height: 6px;
}
:global(#variant-filter-slider .rangeBar) {
  height: 6px;
}
:global(#variant-filter-slider .rangeHandle) {
  top: 2px;
  height: 16px;
  width: 16px;
}
:global(#variant-filter-slider .rangeHandle .rangeNub) {
  border: 1px solid rgb(255, 255, 255);
}


</style>