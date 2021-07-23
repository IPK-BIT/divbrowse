<script>
export let onCallToAction = null;
export let settings;

import { getContext } from 'svelte';
const context = getContext('app');
let { controller, eventbus } = context.app();

import getStores from '/utils/store';
const { variantFilterSettings, filteredVariantsCoordinates } = getStores();


import LoadingAnimation from '/components/utils/LoadingAnimation.svelte';
let showLoadingAnimation = false;
eventbus.on('loading:animation:pca', msg => {
    showLoadingAnimation = msg.status;
});
let showLoadingAnimationSnpWindow = false;


let mode = 'current_snp_window';
let useVariantFilter = false;

let startpos, endpos, snpcount, snpcountFiltered;
let customSnpWindowSnpCount = false;

let selectedFeature = null;
let featuresById = {};
let showSnpWindowInfobox = true;

let doCalcBtnDisabled = true;

let customStartpos = '';
let customEndpos = '';

let showPcaResultPlot = 'none';
let selectedAccessions = [];


let data = controller.data;
$: {
    data = controller.data;
    featuresById = {};
    data.features.forEach((feature) => {
        featuresById[feature.ID] = feature;
    });
}



function validateSnpWindow(_startpos, _endpos) {

    snpcountFiltered = '';
    let params = {
        startpos: parseInt(_startpos),
        endpos: parseInt(_endpos),
    }
    if (useVariantFilter) {
        params['variantFilterSettings'] = $variantFilterSettings;
    }

    showLoadingAnimationSnpWindow = true;

    controller.snp_window_summary(params, result => {
        showLoadingAnimationSnpWindow = false;
        snpcount = result.count_snps_in_window;
        snpcountFiltered = result.count_snps_in_window_filtered;
        if (snpcount > 0) {
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
        }
    });
}

function onChangePcaMode(mode) {
    switch (mode) {
        case 'current_snp_window':
            startpos = data.coordinate_first;
            endpos = data.coordinate_last;
            snpcount = data.variants_coordinates.length;
            validateSnpWindow(startpos, endpos);
            showSnpWindowInfobox = true;
            doCalcBtnDisabled = false;
            showPcaResultPlot = 'none';
            break;

        case 'current_gene':
            showSnpWindowInfobox = false;
            doCalcBtnDisabled = true;
            selectedFeature = '';
            showPcaResultPlot = 'none';
            break;

        case 'custom_snp_window':
            snpcount = false;
            showSnpWindowInfobox = false;
            doCalcBtnDisabled = true;
            showPcaResultPlot = 'none';
            break;
    }
}

function onChangeSelectedFeature(selectedFeatureID) {
    if (mode === 'current_gene') {
        showSnpWindowInfobox = false;
        snpcount = '';
        snpcountFiltered = '';
        if (selectedFeatureID !== null && selectedFeatureID !== '') {
            let selectedFeature = featuresById[selectedFeatureID];
            startpos = selectedFeature.start;
            endpos = selectedFeature.end;
            validateSnpWindow(startpos, endpos);
            showSnpWindowInfobox = true;
        }
    }
}

function onChangeUseVariantFilter() {
    if (mode === 'custom_snp_window' && customStartpos === '' && customEndpos === '') {
        return false;
    }
    validateSnpWindow(startpos, endpos);
}

$: onChangePcaMode(mode);
$: onChangeSelectedFeature(selectedFeature);
$: onChangeUseVariantFilter(useVariantFilter);




const doCalculation = () => {
    doCalcBtnDisabled = false;
    const callbackSuccess = () => { doCalcBtnDisabled = true; }
    onCallToAction(startpos, endpos, useVariantFilter, callbackSuccess);
};

</script> 
 

<div>

    <div class="clearfix">
        <div class="form-inline" style="float: left;">
            <label class="form-label" for="snp-coloring-selector">{settings.modeSelectLabel} </label>
            <select id="pca-mode" bind:value={mode} class="divbrowse-form-control">
                <option value="current_snp_window">Current SNP window</option>
                <option value="current_gene">Current gene</option>
                <option value="custom_snp_window">Custom SNP window</option>
            </select>
        </div>

        <div style="float: left; margin-left: 20px; margin-top: 6px;">
            <input id="useVariantFilter" type="checkbox" style="vertical-align: -1px;" bind:checked={useVariantFilter}>
            <label for="useVariantFilter" style="color: {useVariantFilter==true ? 'black' : 'rgb(140,140,140)'};">Apply SNP filter settings</label>
        </div>

    </div>

    {#if mode === 'custom_snp_window'}
    <div style="margin-top: 25px;">
        <div>
            <label class="form-label" style="display: inline-block; width: 120px;">Start position:</label>
            <input type="text" bind:value={customStartpos} class="divbrowse-form-control" style="padding: 0 8px 0 8px;" />
        </div>
        <div style="margin-top:5px;">
            <label class="form-label" style="display: inline-block; width: 120px;">End position:</label>
            <input type="text" bind:value={customEndpos} class="divbrowse-form-control" style="padding: 0 8px 0 8px;" />
            <input type="button" on:click|preventDefault={() => validateSnpWindow(customStartpos, customEndpos)} value="Validate positions" class="divbrowse-btn divbrowse-btn-light" />
        </div>
        {#if snpcount !== false}
        <div style="font-size:0.85rem; margin-top: 15px;">There are {snpcount} SNPs in the given window.</div>
            {#if useVariantFilter}
                <div style="margin-top: 10px; font-size:0.85rem;">
                {#if showLoadingAnimationSnpWindow}
                    <LoadingAnimation size="small" />
                {:else}
                    There are {snpcountFiltered} SNPs in the given window matching your filter criteria.
                {/if}
                </div>
            {/if}
        {/if}
    </div>
    {/if}
    
    {#if mode !== 'custom_snp_window'}
    <div style="margin-top: 25px;">
        <table style="margin-bottom: 15px;">
        {#if mode === 'current_gene'}
            {#if data.features.length > 0}
            <tr>
                <td>Select gene or feature:</td>
                <td>
                    <select class="divbrowse-form-control" bind:value={selectedFeature} >
                        <option value="">Please select...</option>
                        {#each data.features as feature}
                        <option value="{feature.ID}">{feature.ID}</option>
                        {/each}
                    </select>
                </td>
            </tr>
            {:else}
            <tr>
                <td colspan="2">There are currently no genes in the viewspace!</td>
            </tr>
            {/if}
        {/if}

        {#if showSnpWindowInfobox}
            <tr>
                <td>Start position:</td>
                <td>{startpos}</td>
            </tr>
            <tr>
                <td>End position:</td>
                <td>{endpos}</td>
            </tr>
            <tr>
                <td>Number of SNPs:</td>
                <td>{snpcount}</td>
            </tr>

            {#if useVariantFilter}
            <tr>
                <td>Number of filtered SNPs:</td>
                <td>
                    {#if showLoadingAnimationSnpWindow}
                        <LoadingAnimation size="small" />
                    {:else}
                        {snpcountFiltered}
                    {/if}
                </td>
            </tr>
            {/if}

        {/if}
        </table>
    </div>
    {/if}
    
    <div style="margin-top: 25px;" class="clearfix">
        <button on:click|preventDefault={doCalculation} disabled="{doCalcBtnDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light" style="float:left;">{settings.ctaBtnLabel}</button>

        {#if showLoadingAnimation}
        <div style="float:left;margin-left:20px;">
            <LoadingAnimation size="small" />
        </div>
        {/if}

    </div>

</div>

<style>
table tr td {
    font-size: 0.85rem;
}
</style>