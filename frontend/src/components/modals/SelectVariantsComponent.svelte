<script>
export let onCallToAction = null;
export let openClustermapModal = null;
export let callbackExportVcf = null;
export let callbackExportCsv = null;
export let callbackExportGff = null;
export let settings;

let errorMsg;
export function setErrorMsg(_errorMsg) {
    errorMsg = _errorMsg;
}

import { getContext } from 'svelte';
const context = getContext('app');
let { appId, controller, eventbus } = context.app();

import { fade } from 'svelte/transition';

import getStores from '@/utils/store';
const { variantFilterSettings } = getStores();

import LoadingAnimation from '@/components/utils/LoadingAnimation.svelte';
let showLoadingAnimation = false;


export const loadingAnimation = {
    show: () => showLoadingAnimation = true,
    hide: () => showLoadingAnimation = false
}


let showLoadingAnimationSnpWindow = false;


let mode = 'current_viewport';
let useVariantFilter = false;

let startpos, endpos, snpcount;
let genomicRange = '';
let customRangeInputDisabled = true;

let selectedFeature = null;
let selectedFeatureDisabled = false;
let featuresById = {};
let showSnpWindowInfobox = true;

let doCalcBtnDisabled = true;
let btnExportDisabled = true;

let customStartpos = '';
let customEndpos = '';

let variant_positions_textarea = '';
let variant_positions = [];
let variant_positions_found = [];
let variant_positions_not_found = [];


let data = controller.data;

$: {
    data = controller.data;
    featuresById = {};
    data.features.forEach((feature) => {
        featuresById[feature.ID] = feature;
    });
}

eventbus.on('data:display:changed', _data => {
    data = _data;
    featuresById = {};
    data.features.forEach((feature) => {
        featuresById[feature.ID] = feature;
    });
});



function validateGenomicRegion(_startpos, _endpos) {

    let params;

    if (_startpos === undefined && _endpos === undefined) {
        params = {
            positions: variant_positions
        }
    } else {
        params = {
            startpos: parseInt(_startpos),
            endpos: parseInt(_endpos),
        }
    }

    if (useVariantFilter) {
        params['variantFilterSettings'] = $variantFilterSettings;
    }

    showLoadingAnimationSnpWindow = true;
    variant_positions_not_found = [];

    controller.genomic_window_summary(params, result => {
        errorMsg = false;
        showLoadingAnimationSnpWindow = false;

        if (result.positions_not_found) {
            variant_positions_not_found = result.positions_not_found;
            btnExportDisabled = true;
        } else {

            if (result.positions) {
                variant_positions_found = result.positions;
            }

            //snpcount = result.number_of_variants_in_window;
            snpcount = result.number_of_variants_in_window_filtered;
            if (snpcount > 0) {
                startpos = result.startpos;
                endpos = result.endpos;
                btnExportDisabled = false;
            }
            if (snpcount > 4) {
                startpos = result.startpos;
                endpos = result.endpos;
                if (mode === 'current_gene') {
                    if (selectedFeature !== null && selectedFeature !== '') {
                        doCalcBtnDisabled = false;
                    }
                } else {
                    doCalcBtnDisabled = false;
                }
            } else {
                doCalcBtnDisabled = true;
                errorMsg = 'Too few variants for data analysis. Please provide a genomic region that has at least 5 variants.'
            }
        }
    });
}

function onChangeMode(mode) {
    switch (mode) {
        case 'current_viewport':
            startpos = data.coordinate_first;
            endpos = data.coordinate_last;
            snpcount = data.variants_coordinates.length;
            validateGenomicRegion(startpos, endpos);
            showSnpWindowInfobox = true;
            doCalcBtnDisabled = false;
            customRangeInputDisabled = true;
            break;

        case 'current_gene':
            doCalcBtnDisabled = true;
            btnExportDisabled = true;
            selectedFeature = '';
            customRangeInputDisabled = true;
            startpos = 0;
            endpos = 0;
            snpcount = '<i>undefined</i>';
            break;

        case 'custom_range':
            snpcount = '<i>undefined</i>';
            doCalcBtnDisabled = true;
            btnExportDisabled = true;
            customRangeInputDisabled = false;
            startpos = 0;
            endpos = 0;
            break;

        case 'variant_positions':
            snpcount = '<i>undefined</i>';
            doCalcBtnDisabled = true;
            btnExportDisabled = true;
            customRangeInputDisabled = false;
            startpos = 0;
            endpos = 0;
            break;
    }
}

function onChangeSelectedFeature(selectedFeatureID) {
    if (mode === 'current_gene') {
        snpcount = '<i>undefined</i>';
        selectedFeatureDisabled = true;
        if (selectedFeatureID !== null && selectedFeatureID !== '') {
            let selectedFeature = featuresById[selectedFeatureID];
            startpos = selectedFeature.start;
            endpos = selectedFeature.end;
            validateGenomicRegion(startpos, endpos);
            showSnpWindowInfobox = true;
            selectedFeatureDisabled = false;
        }
    }
}

function onChangeUseVariantFilter() {
    if (mode === 'custom_range' && customStartpos === '' && customEndpos === '') {
        return false;
    }
    validateGenomicRegion(startpos, endpos);
}

$: onChangeMode(mode);
$: onChangeSelectedFeature(selectedFeature);
$: onChangeUseVariantFilter(useVariantFilter);

function onChangeStartEndPos(startpos, endpos) {
    if (startpos > 0 && endpos > 0) {
        genomicRange = startpos+' &#8211; '+endpos;
    } else {
        genomicRange = '<i>undefined</i>';
    }
}

$: onChangeStartEndPos(startpos, endpos);


const doCalculation = () => {
    doCalcBtnDisabled = false;
    const callbackSuccess = () => { doCalcBtnDisabled = true; }
    onCallToAction(startpos, endpos, useVariantFilter, callbackSuccess);
};



function parsePositions(input) {
    if (input.includes(',')) {
        variant_positions = input.split(',');
    } else if (input.includes(';')) {
        variant_positions = input.split(';');
    } else if (input.includes('\n')) {
        variant_positions = input.split('\n');
    } else if (input.includes(' ')) {
        variant_positions = input.split(' ');
    } else {
        variant_positions = [input];
    }
    
    variant_positions = variant_positions.filter(id => id.length > 0);
    onChangeMode('variant_positions');
}

$: parsePositions(variant_positions_textarea);



const showVariantFilterModal = () => {
    eventbus.emit('modal:open', {
        component: 'VariantFilter',
        onClose: () => {
            onChangeUseVariantFilter()
        }
    });
};


$: if (errorMsg) {
    setTimeout(function(){
        errorMsg = false;
    }, 8000);
}


</script>

<svelte:options accessors={true}/>
 

<section style="width: 50vw;">

    

    <div id="grid-parent">

        <div class="col1 grid-mode-box">
            <p style="margin: 0 0 15px 0; font-size: 90%;">Select the genomic region for analysis or export:</p>

            <div class="select-option">
                <input type="radio" name="mode" bind:group={mode} value="current_viewport" id="mode-current_viewport"> 
                <label for="mode-current_viewport">
                    <h5>Current viewport</h5>
                </label>
                <p>Data analysis and export are based on the variants that are displayed in the current viewport.</p>
            </div>

            <div class="select-option" class:disabled={ data.features.length == 0 ? true : false } style="margin-top: 20px;">
                <input disabled={ data.features.length == 0 ? true : false } type="radio" name="mode" bind:group={mode} value="current_gene" id="mode-current_gene">
                <label for="mode-current_gene">
                    <h5>Currently visible gene</h5>
                </label>
                <p>Data analysis and export are based on the variants that are within a currently visible gene or feature.</p>
            </div>

            <div class="select-option" style="margin-top: 20px;">
                <input type="radio" name="mode" bind:group={mode} value="custom_range" id="mode-custom_range">
                <label for="mode-custom_range">
                    <h5>Custom genomic region</h5>
                </label>
                <p>Data analysis and export are based on a custom defined genomic region.</p>
            </div>

            <div class="select-option" style="margin-top: 20px;">
                <input type="radio" name="mode" bind:group={mode} value="variant_positions" id="mode-variant_positions"> 
                <label for="mode-variant_positions">
                    <h5>Variant positions</h5>
                </label>
                <p>Data analysis and export are based on the variants that are provided by a delimiter separated list of positions.</p>
            </div>
        </div>

        <div class="col2 grid-mode-box parameters" class:inactive={mode === 'current_viewport' ? true : false}>

            <div>
            {#if mode === 'current_gene'}
                {#if data.features.length == 0}
                    <p style="line-height: 1 !important; font-size: 90%; font-weight: 500; padding-top: 0px;">There are currently no genes in the viewport!</p>
                {:else}
                    <select class="divbrowse-form-control" style="width:100%;" bind:value={selectedFeature} disabled={ (data.features.length == 0 || mode !== 'current_gene') ? true : false }>
                        <option value="">Please select a gene or feature ...</option>
                        {#each data.features as feature}
                        {#if feature.ID !== "."}
                        <option style="font-size: 90%;" value="{feature.ID}">{feature.ID}</option>
                        {/if}
                        {/each}
                    </select>
                {/if}
            {/if}
            </div>

            {#if mode === 'custom_range'}
            <div>
                <p>Provide a start and an end position for the genomic range:</p>
                <input disabled="{customRangeInputDisabled}" type="text" bind:value={customStartpos} placeholder="Start position" class="divbrowse-form-control" style="padding: 0 8px 0 8px; width: 120px;" />
                <input disabled="{customRangeInputDisabled}" type="text" bind:value={customEndpos} placeholder="End position" class="divbrowse-form-control" style="padding: 0 8px 0 8px; width: 120px;" /><br>
                <input disabled="{customRangeInputDisabled}" type="button" on:click|preventDefault={() => validateGenomicRegion(customStartpos, customEndpos)} value="Validate" class="divbrowse-btn divbrowse-btn-light" style="margin-top: 9px;" />
            </div>
            {/if}

            {#if mode === 'variant_positions'}
            <div>
                <p>Provide a list with variant positions in the textarea below. Positions can be separated either by comma, semicolon, space or newline.</p>
                <textarea bind:value={variant_positions_textarea} style="width: 100%; height: 70px; padding: 6px;"></textarea>

                <div style="margin-top: 6px; display: flow-root;">
                    <input disabled="{variant_positions.length > 0 && !showLoadingAnimationSnpWindow ? false : true}" type="button" on:click|preventDefault={() => validateGenomicRegion()} value="Validate" class="divbrowse-btn divbrowse-btn-light" style="float: left;" />
                    {#if showLoadingAnimationSnpWindow}
                    <div style="float: left; margin: 4px 0 0 10px;"><LoadingAnimation size="small" /></div>
                    {/if}
                </div>

                {#if variant_positions_not_found.length > 0}
                <div style="margin-top: 20px;">
                    <p style="color: red; margin-bottom: 0px;">The following positions couldn't be mapped to any variant:</p>
                    <textarea style="width: 100%; height: 60px; padding: 6px;">{variant_positions_not_found.join(', ')}</textarea>
                </div>
                {/if}
            </div>
            {/if}

        </div>

        <!--
        <div class="col3 grid-mode-box">

        </div>

        <div class="col4 grid-mode-box">

        </div>
        -->
    </div>






        {#if showSnpWindowInfobox}
        <p style="margin-bottom: 5px; margin-top:25px; font-size: 90%;">Current parameters for analysis or export:</p>
        <div class="genomic-range-info clearfix" style="">
            <div class="clearfix" style="">
                <table style="border-collapse: collapse; float: left; width: 450px;">
                    <tr>
                        <td>Chromosome:</td>
                        <td>{controller.metadata.chromosomesById[controller.chromosome].label}</td>
                    </tr>
                    <tr>
                        <td style="width: 140px;">Genomic range:</td>
                        <td>{@html genomicRange}</td>
                    </tr>

                    {#if settings.showSnpCount === undefined || settings.showSnpCount === true}
                    <tr>
                        <td>Number of variants:</td>
                        <td>
                            {#if showLoadingAnimationSnpWindow}
                                <LoadingAnimation size="tiny" />
                            {:else}
                                {@html snpcount}
                            {/if}
                        </td>
                    </tr>
                    {/if}

                </table>

                {#if settings.allowSnpFiltering === undefined || settings.allowSnpFiltering === true}
                <div style="float: left; margin-left: 20px; margin-top: 15px; font-size: 90%;">
                    <input id="useVariantFilter" type="checkbox" style="vertical-align: -1px;" bind:checked={useVariantFilter}>
                    <label for="useVariantFilter" style="color: {useVariantFilter==true ? 'black' : 'rgb(140,140,140)'};">Apply variant filter settings (<a on:click|preventDefault={showVariantFilterModal} href="#">change</a>)</label>
                </div>
                {/if}
            </div>
        </div>
        {/if}
    




    <div style="margin-top: 25px;" class="clearfix">
        <button on:click|preventDefault={doCalculation} disabled={doCalcBtnDisabled} type="button" class="divbrowse-btn divbrowse-btn-light btn-cta" style="float:left;">Start data analysis</button>
        <button on:click|preventDefault={() => openClustermapModal(startpos, endpos, useVariantFilter)} disabled={doCalcBtnDisabled} type="button" class="divbrowse-btn divbrowse-btn-light btn-cta" style="float:left;">Clustermap</button>
        <button on:click|preventDefault={() => callbackExportVcf(startpos, endpos, useVariantFilter, variant_positions_found, () => {})} disabled={btnExportDisabled} type="button" class="divbrowse-btn divbrowse-btn-light btn-cta" style="float:left;">Export VCF</button>
        <button on:click|preventDefault={() => callbackExportCsv(startpos, endpos, useVariantFilter, variant_positions_found, () => {})} disabled={btnExportDisabled} type="button" class="divbrowse-btn divbrowse-btn-light btn-cta" style="float:left;">Export variants as CSV</button>
        <button on:click|preventDefault={() => callbackExportGff(startpos, endpos, useVariantFilter, () => {})} disabled={btnExportDisabled} type="button" class="divbrowse-btn divbrowse-btn-light btn-cta" style="float:left;">Export GFF3</button>

        {#if showLoadingAnimation}
        <div style="float:left;margin-left:20px;">
            <LoadingAnimation size="small" />
        </div>
        {/if}
    </div>

    <div style="margin-top: 20px; height: 40px;" class="clearfix">
        {#if errorMsg}
        <div in:fade out:fade style="font-size: 90%; color: red;">
            <span style="font-weight: 500;">Warning:</span> {errorMsg}
        </div>
        {/if}
    </div>


</section>

<style lang="less">

button.btn-cta {
    margin-right: 25px;
}

#grid-parent {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: 1fr;
    grid-column-gap: 20px;
    grid-row-gap: 0px;
}

.col1 { grid-area: 1 / 1 / 2 / 2; }
.col2 { grid-area: 1 / 2 / 2 / 3; }
.col3 { grid-area: 1 / 3 / 2 / 4; }
.col4 { grid-area: 1 / 4 / 2 / 5; }

.grid-mode-box {
    border: 1px solid rgb(200,200,200);
    background: rgb(248,248,248);
    border-radius: 8px;
    padding: 15px;
    box-sizing: border-box;

    > div.select-option {
        border: 0px solid red;
        position: relative;

        input {
            position: absolute;
            top: 1px;
            left: 0px;
            margin:0;
        }

        label {
            margin-left: 23px;
            display: block;

            h5 {
                font-size: 95%;
                margin: 0;
                padding: 0;
                font-weight: 700;
            }
        }

        p {
            font-size: 86%;
            margin: 5px 0 0 23px;
            padding: 0;
            line-height: 1.2 !important;
            color: rgb(90,90,90);
        }

        &.disabled {
            color: rgb(130,130,130);
            p {
                color: rgb(130,130,130);
            }
        }
    }

    &.parameters {
        p {
            margin: 0 0 10px 0;
            font-size: 90%;
            line-height: 1.3;
        }
    }

    &.inactive {

    }
}

div.mode-option-box {

    border: 1px solid rgb(200,200,200);
    background: rgb(248,248,248);
    border-radius: 8px;
    margin-bottom: 14px;
    padding: 15px 10px;
    /*width: 300px;*/
    box-sizing: border-box;
    float: left;

    > div.select-option {
        float: left;
        width: 250px;
        border: 0px solid red;
        position: relative;

        input {
            position: absolute;
            top: 0px;
            left: 0px;
        }

        label {
            margin-left: 28px;
            display: block;

            h5 {
                font-size: 95%;
                margin: 0;
                padding: 2px 0 0 0;
                font-weight: 700;
            }

            p {
                font-size: 90%;
                margin: 5px 0 0 0;
                padding: 0;
                line-height: 1 !important;
                color: rgb(90,90,90);
            }
        }
    }
}


div.genomic-range-info {
    /*margin-top: 40px;*/
    border: 1px solid rgb(200,200,200);
    background: rgb(242,242,242);
    border-radius: 8px;
    padding: 10px 7px;
}


table tr td {
    font-size: 90%;
    border: 0px solid rgb(200,200,200);
    padding: 1px 5px;
}

</style>