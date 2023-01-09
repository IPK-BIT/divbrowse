<script>
export let onCallToAction = null;
export let callbackExportVcf = null;
export let callbackExportGff = null;
export let settings;

let errorMsg;
export function setErrorMsg(_errorMsg) {
    errorMsg = _errorMsg;
}

import { getContext } from 'svelte';
const context = getContext('app');
let { controller, eventbus } = context.app();

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

let customStartpos = '';
let customEndpos = '';


let data = controller.data;
$: {
    data = controller.data;
    featuresById = {};
    data.features.forEach((feature) => {
        featuresById[feature.ID] = feature;
    });
}



function validateGenomicRegion(_startpos, _endpos) {

    let params = {
        startpos: parseInt(_startpos),
        endpos: parseInt(_endpos),
    }
    if (useVariantFilter) {
        params['variantFilterSettings'] = $variantFilterSettings;
    }

    showLoadingAnimationSnpWindow = true;

    controller.genomic_window_summary(params, result => {
        errorMsg = false;
        showLoadingAnimationSnpWindow = false;
        snpcount = result.number_of_variants_in_window;
        snpcount = result.number_of_variants_in_window_filtered;
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
            selectedFeature = '';
            customRangeInputDisabled = true;
            startpos = 0;
            endpos = 0;
            snpcount = '<i>undefined</i>';
            break;

        case 'custom_range':
            snpcount = '<i>undefined</i>';
            doCalcBtnDisabled = true;
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
 

<div>

    <div class="clearfix" style="margin-bottom: 25px;">

        <p style="margin-bottom: 10px; font-size: 0.85rem;">Select the genomic region for analysis or export:</p>
        
        <div style="" class="mode-option-box clearfix">
            <div class="select-option">
                <input type="radio" name="mode" bind:group={mode} value={"current_viewport"} id="mode-current_viewport"> 
                <label for="mode-current_viewport">
                    <h5>Current viewport</h5>
                    <p>Data analysis and export are based on the variants that are displayed in the current viewport.</p>
                </label>
            </div>
        </div>

        <div style="" class="mode-option-box clearfix">
            <div class="select-option">
                <input disabled={ data.features.length == 0 ? true : false } type="radio" name="mode" bind:group={mode} value={"current_gene"} id="mode-current_gene">
                <label for="mode-current_gene">
                    <h5>Currently visible gene</h5>
                    <p>Data analysis and export are based on the variants that are within a currently visible gene or feature.</p>
                </label>
            </div>

            <div class="form-inline" style="float: left; margin-left: 50px; margin-top: 20px;">
            {#if data.features.length == 0}
                <p style="line-height: 0.8 !important; font-size: 0.85rem; font-weight: 500; padding-top: 0px;">There are currently no genes in the viewport!</p>
            {:else}
                <select class="divbrowse-form-control" bind:value={selectedFeature} disabled={ (data.features.length == 0 || mode !== 'current_gene') ? true : false }>
                    <option value="">Please select a gene or feature ...</option>
                    {#each data.features as feature}
                    {#if feature.ID !== "."}
                    <option value="{feature.ID}">{feature.ID}</option>
                    {/if}
                    {/each}
                </select>
            {/if}
            </div>

        </div>

        <div style="" class="mode-option-box clearfix">
            <div class="select-option">
                <input type="radio" name="mode" bind:group={mode} value={"custom_range"} id="mode-custom_range">
                <label for="mode-custom_range">
                    <h5>Custom genomic region</h5>
                    <p>Data analysis and export are based on a custom defined genomic region.</p>
                </label>
            </div>

            
            <div class="form-inline" style="float: left; margin-left: 50px; margin-top: 0px;">
                <div style="float: left;">
                    <input disabled="{customRangeInputDisabled}" type="text" bind:value={customStartpos} placeholder="Start position" class="divbrowse-form-control" style="padding: 0 8px 0 8px; margin-bottom: 6px;" /><br />
                    <input disabled="{customRangeInputDisabled}" type="text" bind:value={customEndpos} placeholder="End position" class="divbrowse-form-control" style="padding: 0 8px 0 8px;" />
                    <input disabled="{customRangeInputDisabled}" type="button" on:click|preventDefault={() => validateGenomicRegion(customStartpos, customEndpos)} value="Validate" class="divbrowse-btn divbrowse-btn-light" />
                </div>


            </div>
            

        </div>







        {#if showSnpWindowInfobox}
        <p style="margin-bottom: 10px; margin-top:25px; font-size: 0.85rem;">Current parameters for analysis or export:</p>
        <div class="genomic-range-info clearfix" style="">
            <div class="clearfix" style="">
                <table style="border-collapse: collapse; float: left; width: 450px;">
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
                <div style="float: left; margin-left: 20px; margin-top: 6px; font-size: 0.85rem;">
                    <input id="useVariantFilter" type="checkbox" style="vertical-align: -1px;" bind:checked={useVariantFilter}>
                    <label for="useVariantFilter" style="color: {useVariantFilter==true ? 'black' : 'rgb(140,140,140)'};">Apply SNP filter settings (<a on:click|preventDefault={showVariantFilterModal} href="#">change</a>)</label>
                </div>
                {/if}
            </div>
        </div>
        {/if}



    </div>




    <div style="margin-top: 25px;" class="clearfix">

        <button on:click|preventDefault={doCalculation} disabled="{doCalcBtnDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light btn-cta" style="float:left;">Start data analysis</button>
        <button on:click|preventDefault={() => callbackExportVcf(startpos, endpos, useVariantFilter, () => {})} disabled="{doCalcBtnDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light btn-cta" style="float:left;">Export VCF</button>
        <button on:click|preventDefault={() => callbackExportGff(startpos, endpos, useVariantFilter, () => {})} disabled="{doCalcBtnDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light btn-cta" style="float:left;">Export GFF3</button>

        {#if showLoadingAnimation}
        <div style="float:left;margin-left:20px;">
            <LoadingAnimation size="small" />
        </div>
        {/if}



    </div>

    <div style="margin-top: 20px; height: 40px;" class="clearfix">
        {#if errorMsg}
        <div in:fade out:fade style="font-size: 0.85rem; color: red;">
            <span style="font-weight: 500;">ERROR:</span> {errorMsg}
        </div>
        {/if}
    </div>

</div>

<style lang="less">

button.btn-cta {
    margin-right: 25px;
}

div.mode-option-box {

    border: 1px solid rgb(200,200,200);
    background: rgb(248,248,248);
    border-radius: 8px;
    margin-bottom: 14px;
    padding: 15px 10px;
    
    box-sizing: border-box;

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
                font-size: 0.9rem;
                margin: 0;
                padding: 2px 0 0 0;
                font-weight: 700;
            }

            p {
                font-size: 0.85rem;
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
    padding: 13px 15px;
}


table tr td {
    font-size: 0.85rem;
    border: 0px solid rgb(200,200,200);
    padding: 1px 5px;
}

</style>