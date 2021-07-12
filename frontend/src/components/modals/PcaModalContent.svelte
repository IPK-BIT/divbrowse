<script>
import { getContext } from 'svelte';
const context = getContext('app');
let { controller, eventbus } = context.app();

import getStores from '/utils/store';
const { variantFilterSettings, filteredVariantsCoordinates } = getStores();

import SelectSnpsDialogue from '/components/modals/SelectSnpsDialogue.svelte';

let showPcaResultPlot = 'none';
let selectedAccessions = [];

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

    let traces = [{
        x: params.x,
        y: params.y,
        text: params.labels,
        mode: 'markers',
        type: 'scatter',
        marker: { size: 2, color: '#000000' },
    }];

    Plotly.newPlot('plotDivModal', traces, layout, buttons);
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


function onCallToAction(startpos, endpos, useVariantFilter, callbackSuccess) {

    let params = {
        startpos: startpos,
        endpos: endpos,
    }
    if (useVariantFilter) {
        params['variantFilterSettings'] = $variantFilterSettings;
    }

    controller.pca(params, result => {
        callbackSuccess();

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
}

let settingsSelectSnpsDialogue = {
    modeSelectLabel: 'Calculate PCA for:',
    ctaBtnLabel: 'Perform calculation now'
}

</script> 
 

<div>
    <div class="divbrowse-modal-dialogue-headline">Principle Component Analysis</div>

    <SelectSnpsDialogue onCallToAction={onCallToAction} settings={settingsSelectSnpsDialogue} />

    {#if selectedAccessions.length > 0}
    <div>You have selected {selectedAccessions.length} samples.</div>
    {/if}

    <div id="plotDivModal" style="display: {showPcaResultPlot}; height: 520px; margin-top:20px; padding: 5px; border: 1px solid black;"></div>

</div>

<style>

</style>