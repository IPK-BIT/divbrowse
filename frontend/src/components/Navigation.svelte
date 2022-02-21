<script>
export let settings;

import { onMount, getContext, afterUpdate } from 'svelte';
const context = getContext('app');
let { appId, eventbus, controller } = context.app();

import getStores from '/utils/store';
const { variantWidth, groups } = getStores();

import Modal from 'svelte-simple-modal';

import SettingsModal from '/components/modals/SettingsModal.svelte';
import SortSamplesModal from '/components/modals/SortSamplesModal.svelte';
import VariantFilterModal from '/components/modals/VariantFilterModal.svelte';
import DataAnalysisAndExportModal from '/components/modals/DataAnalysisAndExportModal.svelte';
import BlastModal from '/components/modals/BlastModal.svelte';
import VcfExportModal from '/components/modals/VcfExportModal.svelte';
import GffExportModal from '/components/modals/GffExportModal.svelte';
import DataSummaryModal from '/components/modals/DataSummaryModal.svelte';
import GeneSearchModal from '/components/modals/GeneSearchModal.svelte';

import LoadingAnimation from '/components/utils/LoadingAnimation.svelte';

let selectedChromosome;
let position;
let chromosomes = [];
let statusBlastButton = false;


eventbus.on('metadata:loaded', metadata => {
    chromosomes = metadata.chromosomes;
    statusBlastButton = metadata.features.blast;
});

function handleGoToPosition(position) {
    controller.goToPosition(position);
}

function handleChangeChromosome(chromosome) {
    controller.setChromosome(chromosome);
}

function handleVariantWidthChange(event) {
    let width = parseInt(event.target.value);
    if (width > 0 && width <= 20) {
        variantWidth.set(width);
        controller.setSnpWidth(width);
    }
}

function handleBackward(steps) {
    controller.goBackward(steps);
}

function handleForward(steps) {
    controller.goForward(steps);
}

let showLoadingAnimation = false;
eventbus.on('loading:animation', msg => {
    showLoadingAnimation = msg.status;
});

let btnBackwardDisabled = true;
let btnForwardDisabled = true;

let data = false;
let dataGenesLoaded = false;
let variants = false;

eventbus.on('data:display:changed', _data => {
    data = _data;

    btnBackwardDisabled = false;
    btnForwardDisabled = false;

    if (data.coordinate_last_prev > data.coordinate_first) {
        btnBackwardDisabled = true;
    }

    if (data.coordinate_last > data.coordinate_first_next) {
        btnForwardDisabled = true;
    }

    selectedChromosome = controller.chromosome;
});

eventbus.on('data:genes:loaded', _data => {
    dataGenesLoaded = true;
});
</script>



<nav class="navigation clearfix" style="position: relative;">

    {#if showLoadingAnimation}
    <div style="position: absolute; top: 0px; right: 0px;">
        <LoadingAnimation size="small" />
    </div>
    {/if}

    <div class="navigation-row clearfix">

        <div style="">
            <label class="form-label" for="chromosome-selector">Chromosome: </label>
            <select class="divbrowse-form-control" bind:value={selectedChromosome} on:change|preventDefault="{handleChangeChromosome(selectedChromosome)}">
                {#each chromosomes as chromosome}
                <option value="{chromosome.id}">{chromosome.label}</option>
                {/each}
            </select>
        </div>
        

        <div style="margin-left:30px;">
            <label class="form-label" for="position-input">Position: </label>
            <input bind:value={position} type="number" id="position-input" class="divbrowse-form-control">
            <button on:click|preventDefault={handleGoToPosition(position)} type="button" class="divbrowse-btn divbrowse-btn-light">Go</button>
        </div>

        <div style="float:left; margin-left:30px;">
            <!--<button on:click|preventDefault={ () => handleBackward() } disabled="{btnBackwardDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light">&laquo; prev. window</button>-->
            <button on:click|preventDefault={ () => handleBackward(20) } disabled="{btnBackwardDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light"><span style="font-size:20px;">&#8678;&#8678;</span></button>
            <button on:click|preventDefault={ () => handleBackward(10) } disabled="{btnBackwardDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light" style="margin-left:2px;"><span style="font-size:20px;">&#8678;</span></button>
            <!--<span style="border-left:2px solid rgb(150,150,150); margin-left: 10px; margin-right:12px;"></span>-->
            <button on:click|preventDefault={ () => handleForward(10) } disabled="{btnForwardDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light" style=""><span style="font-size:20px;">&#8680;</span></button>
            <button on:click|preventDefault={ () => handleForward(20) } disabled="{btnForwardDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light" style="margin-left:2px;"><span style="font-size:20px;">&#8680;&#8680;</span></button>
            <!--<button on:click|preventDefault={ () => handleForward() } disabled="{btnForwardDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light" style="margin-left:2px;">next window &raquo;</button>-->
        </div>



        <div style="margin-left:30px;display:none;">
            <label class="form-label" for="position-input">SNP width: </label>
            <input value={$variantWidth} on:change|preventDefault="{handleVariantWidthChange}" type="number" min="1" max="20" id="width-input" class="divbrowse-form-control">
        </div>

        <div style="margin-left:30px;margin-top:5px;">
            <label class="form-label" for="minimap-mode" style="vertical-align: middle;">Show compressed view: </label>
            <input style="vertical-align: middle;" id="minimap-mode" type=checkbox bind:checked={settings.statusShowMinimap}>
        </div>

        <div class="clearfix"></div>

    </div>

    <div class="navigation-row clearfix" style="margin-top:12px;">
        <Modal key="2nd-modal" styleBg={{'z-index': '2000', 'top': '0px', 'left': '0px'}} closeOnOuterClick={false}>
        
        <!--<div style="float:left; width: 1px; height: 20px; border-left:2px solid rgb(150,150,150); margin-left: 20px; margin-right:0px; margin-top:6px;"></div>-->

        <div style="float:left;">
        <Modal closeOnOuterClick={false}>
            <GeneSearchModal disabled={dataGenesLoaded !== false ? false : true} />
        </Modal>
        </div>

        {#if statusBlastButton === true}
        <div style="float:left; margin-left:10px;">
        <Modal>
            <BlastModal disabled={data !== false ? false : true} />
        </Modal>
        </div>
        {/if}

        <div style="float:left; margin-left:30px;">
        <Modal closeOnOuterClick={false}>
            <VariantFilterModal disabled={data !== false ? false : true} />
        </Modal>
        </div>

        <div style="float:left; margin-left:10px;">
        <Modal closeOnOuterClick={false}>
            <SortSamplesModal disabled={data !== false ? false : true} />
        </Modal>
        </div>

        <div style="float:left; margin-left:10px;">
        <Modal>
            <DataAnalysisAndExportModal disabled={data !== false ? false : true} />
        </Modal>
        </div>

        <div style="float:left; margin-left: 30px;">
            <Modal>
                <DataSummaryModal />
            </Modal>
        </div>

        <div style="float:left; margin-left:10px;">
        <Modal closeOnOuterClick={false}>
            <SettingsModal />
        </Modal>
        </div>

        <div class="clearfix"></div>
        </Modal>
    </div>

</nav>

<style>
* {
  box-sizing: border-box;
}


.navigation label {
    font-size: 14px;
    line-height: 0.8 !important;
}

.navigation input {
    font-size: 14px;
    line-height: 0.8 !important;
}

.navigation select {
    font-size: 14px;
    line-height: 0.8 !important;
}

.navigation button {
    font-size: 13px;
    line-height: 0.8 !important;
}



.navigation {
    margin-bottom: 10px;
    /*background:rgb(190,190,190);
    padding: 10px 15px;
    border: 1px solid rgb(120, 120, 120);*/
}

.navigation-row {
    width: 100%;
    border: 0px solid black;
}

.navigation-row > div {
    float: left;
    border: 0px solid black;
}

#chromosome-selector {
    width: 150px;
}
#position-input {
    width: 150px;
}
#width-input {
    width: 60px;
}
</style>