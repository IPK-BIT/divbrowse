<script>

import { onMount, getContext, afterUpdate } from 'svelte';
const context = getContext('app');
let { appId, eventbus, controller } = context.app();

import getStores from '@/utils/store';
const { settings, variantWidth, groups } = getStores();

import Modal from 'svelte-simple-modal';



let selectedChromosome;
let position;
let chromosomes = [];
let statusBlastButton = false;


eventbus.on('metadata:loaded', metadata => {
    chromosomes = metadata.chromosomes;
    statusBlastButton = metadata.features.blast;
});

function handleGoToPosition(position) {
    if (position && position > 0) {
        controller.goToPosition(position);
    }
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

let btnBackwardDisabled = true;
let btnForwardDisabled = true;

function handleBackward(steps) {
    btnBackwardDisabled = true;
    controller.goBackward(steps);
}

function handleForward(steps) {
    btnForwardDisabled = true;
    controller.goForward(steps);
}

let showLoadingAnimation = false;
eventbus.on('loading:animation', msg => {
    showLoadingAnimation = msg.status;
});

function handleClickZoom(which) {
    $settings[which] = !$settings[which];
    if (which === 'zoomX') {
        if ($settings[which]) {
            $variantWidth = 2;
            controller.setSnpWidth(2);
        } else {
            $variantWidth = 20;
            controller.setSnpWidth(20);
        }
    }
    if (which === 'zoomY') {
        $settings.statusShowMinimap = !$settings.statusShowMinimap;
    }
}

let data = false;
let dataGenesLoaded = false;

eventbus.on('data:display:changed', _data => {
    data = _data;

    btnBackwardDisabled = false;
    btnForwardDisabled = false;

    if (data.coordinate_first <= controller.metadata.chromosomesById[data.coordinate_first_chromosome].start) {
        btnBackwardDisabled = true;
    }

    if (data.coordinate_last >= controller.metadata.chromosomesById[data.coordinate_first_chromosome].end) {
        btnForwardDisabled = true;
    }

    selectedChromosome = controller.chromosome;
});

eventbus.on('data:genes:loaded', _data => {
    dataGenesLoaded = true;
});


function openModal(component) {
    eventbus.emit('modal:open', {
        component: component
    });
}

let btnDisabledByData = true;
$: btnDisabledByData = data !== false ? false : true;

</script>



<nav class="navigation clearfix" style="position: relative;">

    <div class="navigation-row" style="display: flow-root;">

        <div style="">
            <label class="form-label" for="chromosome-selector">Chromosome: </label>
            <select class="divbrowse-form-control" bind:value={selectedChromosome} on:change|preventDefault="{handleChangeChromosome(selectedChromosome)}">
                {#each chromosomes as chromosome}
                <option value="{chromosome.id}">{chromosome.label}</option>
                {/each}
            </select>
        </div>
        

        <div style="margin-left:30px;">
            <!--<label class="form-label" for="position-input">Position: </label>-->
            <input bind:value={position} type="number" id="position-input" class="divbrowse-form-control" placeholder="Position">
            <button on:click|preventDefault={() => handleGoToPosition(position)} type="button" class="divbrowse-btn divbrowse-btn-light">Go</button>
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



        <div style="margin-left: 30px; margin-top: 0px;">
            <!--<label class="form-label" for="position-input">Variant width: </label>
            <input value={$variantWidth} on:change|preventDefault="{handleVariantWidthChange}" type="number" min="1" max="20" id="width-input" class="divbrowse-form-control">-->

            <button class="divbrowse-btn divbrowse-btn-light" style="position: relative; padding-left: 26px;" on:click={() => handleClickZoom('zoomX')}>
                <input style="position: absolute; top: 4px; left: 4px; " id="minimap-mode-xaxis" type="checkbox" bind:checked={$settings.zoomX}>
                Zoom X-axis
            </button>
        </div>

        <div style="margin-left: 7px; margin-top: 0px;">
            <!--<label class="form-label" for="minimap-mode" style="vertical-align: middle;">Show compressed view: </label>
            <input style="vertical-align: middle;" id="minimap-mode" type="checkbox" bind:checked={$settings.statusShowMinimap}>-->

            <button class="divbrowse-btn divbrowse-btn-light" style="position: relative; padding-left: 26px;" on:click={() => handleClickZoom('zoomY')}>
                <input style="position: absolute; top: 4px; left: 4px; " id="minimap-mode-xaxis" type="checkbox" bind:checked={$settings.statusShowMinimap}>
                Zoom Y-axis
            </button>
        </div>

    </div>

    <div class="navigation-row" style="margin-top:12px; display: flow-root;">

        <div style="float:left;">
            <button on:click|preventDefault={() => openModal('GeneSearch')} disabled={dataGenesLoaded !== false ? false : true} type="button" class="divbrowse-btn divbrowse-btn-light">Genes</button>
        </div>

        {#if statusBlastButton === true}
        <div style="float:left; margin-left:10px;">
            <button on:click|preventDefault={() => openModal('Blast')} disabled={btnDisabledByData} type="button" class="divbrowse-btn divbrowse-btn-light" style="font-size:0.8rem;">BLAST</button>
        </div>
        {/if}

        <div style="float:left; margin-left:30px;">
            <button on:click|preventDefault={() => openModal('VariantFilter')} disabled={btnDisabledByData} type="button" class="divbrowse-btn divbrowse-btn-light">Filter Variants</button>
        </div>

        <div style="float:left; margin-left:10px;">
            <button on:click|preventDefault={() => openModal('SortSamples')} disabled={btnDisabledByData} type="button" class="divbrowse-btn divbrowse-btn-light">Sort Samples</button>
        </div>

        <div style="float:left; margin-left:10px;">
            <button on:click|preventDefault={() => openModal('DataAnalysisAndExport')} disabled={btnDisabledByData} type="button" class="divbrowse-btn divbrowse-btn-light">Data Analysis / Export</button>
        </div>

        <div style="float:left; margin-left: 30px;">
            <button on:click|preventDefault={() => openModal('DataSummary')} type="button" class="divbrowse-btn divbrowse-btn-light">Data Summary</button>
        </div>

        <div style="float:left; margin-left:10px;">
            <button on:click|preventDefault={() => openModal('Settings')} type="button" class="divbrowse-btn divbrowse-btn-light">Settings</button>
        </div>

    </div>

</nav>

<style>
* {
  box-sizing: border-box;
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
input[type="number"] {
    -moz-appearance: textfield;
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
    margin-right: 0;
}
#width-input {
    width: 60px;
}
</style>