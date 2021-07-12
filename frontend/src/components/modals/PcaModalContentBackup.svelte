<script>
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


let pcaMode = 'current_snp_window';
let useVariantFilter = false;

let startpos, endpos, snpcount, snpcountFiltered;
let customSnpWindowSnpCount = false;

let selectedFeature = null;
let featuresById = {};
let showSnpWindowInfobox = true;

let doCalcBtnDisabled = true;

let customSnpWindowStartPos = '';
let customSnpWindowEndPos = '';

let showPcaResultPlot = 'none';
let selectedAccessions = [];


let data = controller.data;
$: {
    data = controller.data;
    console.log(data);
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

    controller.snp_window_summary(params, result => {
        snpcount = result.count_snps_in_window;
        snpcountFiltered = result.count_snps_in_window_filtered;
        if (snpcount > 0) {
            startpos = result.startpos;
            endpos = result.endpos;
            doCalcBtnDisabled = false;
        } else {
            doCalcBtnDisabled = true;
        }
    });
}

function onChangePcaMode(pcaMode) {
    switch (pcaMode) {
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
    if (pcaMode === 'current_gene') {
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
    validateSnpWindow(startpos, endpos);
}

$: onChangePcaMode(pcaMode);
$: onChangeSelectedFeature(selectedFeature);
$: onChangeUseVariantFilter(useVariantFilter);



function drawPlot(params) {

    let axesOpts = {
        zeroline: false,
        ticks: '',
        showticklabels: true,
        showline: true,
        zeroline: false,
        mirror: false,
        showgrid: false
    }

    let layout = {
        width: 500, // 800
        height: 500, // 800
        autosize: false,
        title: '',
        hovermode: 'closest',
        showlegend: false,
        margin: {
            t: 25, r: 10, b: 20, l: 45
        },
        xaxis: {
            ...axesOpts
        },
        yaxis: {
            scaleanchor: "x",
            ...axesOpts
        },
    };

    let buttons = {
        modeBarButtonsToRemove: ['sendDataToCloud', 'hoverCompareCartesian', 'hoverClosestCartesian', 'hoverClosestGl2d'],
        displaylogo: false
    }

    let trace = {
        x: params.x,
        y: params.y,
        text: params.labels,
        mode: 'markers',
        type: 'scatter',
        marker: { size: 2, color: '#000000' },
    };

    let data = [trace];

    Plotly.newPlot('plotDivModal', data, layout, buttons);

    let plotDiv = document.getElementById('plotDivModal');

    plotDiv.on('plotly_selected', function(eventData) {
        if (eventData !== undefined) {
            eventData.points.forEach(function(pt) {
                selectedAccessions = [...selectedAccessions, pt.text];
            });
            if (selectedAccessions.length > 0) {
                if (controller.config.samplesSelectedCallback !== undefined && typeof controller.config.samplesSelectedCallback === "function") {
                    controller.config.samplesSelectedCallback(selectedAccessions);
                }
            }
        } else {
            //handler(false);
        }
    });
}



const doCalculation = () => {
    doCalcBtnDisabled = false;

    let params = {
        startpos: startpos,
        endpos: endpos,
    }
    if (useVariantFilter) {
        params['variantFilterSettings'] = $variantFilterSettings;
    }

    controller.pca(params, result => {
        doCalcBtnDisabled = true;

        let pcaLabels;

        if (controller.config.sampleDisplayNameTransformer !== undefined && typeof controller.config.sampleDisplayNameTransformer === "function") {
            pcaLabels = result.pca_result.map(item => controller.config.sampleDisplayNameTransformer(item[0]));
        } else {
            pcaLabels = result.pca_result.map(item => item[0]);
        }

        let pcaXvals = result.pca_result.map(item => item[1]);
        let pcaYvals = result.pca_result.map(item => item[2]);
        showPcaResultPlot = 'block';
        drawPlot({x: pcaXvals, y: pcaYvals, labels: pcaLabels});
    });
    
};

</script> 
 

<div>
    <div class="divbrowse-modal-dialogue-headline">Principle Component Analysis</div>

    <div class="clearfix">
        <div class="form-inline" style="float: left;">
            <label class="form-label" for="snp-coloring-selector">Calculate PCA for: </label>
            <select id="pca-mode" bind:value={pcaMode} class="divbrowse-form-control">
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

    {#if pcaMode === 'custom_snp_window'}
    <div style="margin-top: 25px;">
        <div>
            <label class="form-label" style="display: inline-block; width: 160px;">Position of first SNP:</label>
            <input type="text" bind:value={customSnpWindowStartPos} class="form-control" />
        </div>
        <div style="margin-top:5px;">
            <label class="form-label" style="display: inline-block; width: 160px;">Position of last SNP:</label>
            <input type="text" bind:value={customSnpWindowEndPos} class="form-control" />
            <input type="button"  on:click|preventDefault={() => validateSnpWindow(customSnpWindowStartPos, customSnpWindowEndPos)} value="Validate positions" class="divbrowse-btn divbrowse-btn-light" />
        </div>
        {#if snpcount !== false}
        <div style="font-size:0.85rem;">There are {snpcount} SNPs in the given window.</div>
            {#if useVariantFilter}
            <div style="font-size:0.85rem;">There are {snpcountFiltered} SNPs in the given window matching your filter criteria.</div>
            {/if}
        {/if}
    </div>
    {/if}
    
    {#if pcaMode !== 'custom_snp_window'}
    <div style="margin-top: 25px;">
        <table>
        {#if pcaMode === 'current_gene'}
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
                <td>Position of first SNP:</td>
                <td>{startpos}</td>
            </tr>
            <tr>
                <td>Position of last SNP:</td>
                <td>{endpos}</td>
            </tr>
            <tr>
                <td>Number of SNPs:</td>
                <td>{snpcount}</td>
            </tr>

            {#if useVariantFilter}
            <tr>
                <td>Number of filtered SNPs:</td>
                <td>{snpcountFiltered}</td>
            </tr>
            {/if}

        {/if}
        </table>
    </div>
    {/if}
    
    <div style="margin-top: 25px;" class="clearfix">
        <button on:click|preventDefault={doCalculation} disabled="{doCalcBtnDisabled}" type="button" class="divbrowse-btn divbrowse-btn-light" style="float:left;">Perform calculation now</button>

        {#if showLoadingAnimation}
        <div style="float:left;margin-left:20px;">
            <LoadingAnimation size="small" />
        </div>
        {/if}

    </div>

    {#if selectedAccessions.length > 0}
    <div>You have selected {selectedAccessions.length} samples.</div>
    {/if}

    <div id="plotDivModal" style="display: {showPcaResultPlot}; height: 520px; margin-top:20px; padding: 5px; border: 1px solid black;"></div>

</div>

<style>
table tr td {
    font-size: 0.85rem;
}
</style>