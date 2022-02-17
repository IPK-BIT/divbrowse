<script>
export let params;

import { getContext } from 'svelte';
const context = getContext('app');
let { controller, eventbus } = context.app();

import getStores from '/utils/store';
const { variantFilterSettings, filteredVariantsCoordinates } = getStores();

import keyBy from 'lodash/keyBy';

import SelectVariantsComponent from '/components/modals/SelectVariantsComponent.svelte';

import LoadingAnimation from '/components/utils/LoadingAnimation.svelte';

import VariantFilterModalContent from '/components/modals/VariantFilterModalContent.svelte';
const { open } = getContext('2nd-modal');

let showPcaResultPlot = 'block';
let showUmapResultPlot = 'block';
let selectedSamples = [];
let showLoadingAnimation = false;

let result = {};

let rightPlotMethod = 'umap';


let _pcs = Array.from(Array(10).keys()).map(x => x+1);
let _pcsLabels = _pcs.map(x => 'PC '+x);
let pcs = Object.fromEntries(_pcs.map((key, index)=> [key, _pcsLabels[index]]));

let pcaPlotAxisX = '1';
let pcaPlotAxisY = '2';


let pcaPlotAxis = {
    left: {x: '1', y: '2'},
    right: {x: '3', y: '4'},
}

let listenersAdded = {
    'plotDivLeft': false,
    'plotDivRight': false
}


function createTrace(x, y, text, mode) {

    let marker = { size: 4, color: '#000000', opacity: 0.2 };
    if (mode === 'highlighted') {
        marker = { size: 4, color: '#0000FF', opacity: 0.8 };
    }

    let trace = {
        x: x,
        y: y,
        text: text,
        mode: 'markers',
        type: 'scattergl',
        marker: marker,
    }
    return trace;
}


function createTraces() {

    if (selectedSamples.length > 0) {

    }

    //let test = keyBy(samples , '0')

    let onlySelectedSamplesPca = result.pca_result.filter(item => selectedSamples.includes(item[0]) );
    let onlySelectedSamplesUmap = result.umap_result.filter(item => selectedSamples.includes(item[0]) );
    
    let otherSamplesPca = result.pca_result.filter(item => selectedSamples.includes(item[0]) === false );
    let otherSamplesUmap = result.umap_result.filter(item => selectedSamples.includes(item[0]) === false );

    let umapLabels;

    /*if (controller.config.sampleDisplayNameTransformer !== undefined && typeof controller.config.sampleDisplayNameTransformer === "function") {
        umapLabels = result.umap_result.map(item => controller.config.sampleDisplayNameTransformer(item[0]));
    } else {
        umapLabels = result.umap_result.map(item => item[0]);
    }*/

    let x, y, text;
    let tracesLeft = [];
    let tracesRight = [];


    if (onlySelectedSamplesPca.length > 0) {
        x = onlySelectedSamplesPca.map(item => item[pcaPlotAxis.left.x]);
        y = onlySelectedSamplesPca.map(item => item[pcaPlotAxis.left.y]);
        text = onlySelectedSamplesPca.map(item => item[0]);
        tracesLeft.push(createTrace(x, y, text, 'highlighted'));
    }

    x = otherSamplesPca.map(item => item[pcaPlotAxis.left.x]);
    y = otherSamplesPca.map(item => item[pcaPlotAxis.left.y]);
    text = otherSamplesPca.map(item => item[0]);
    tracesLeft.push(createTrace(x, y, text, 'others'));



    if (rightPlotMethod === 'umap') {
        if (onlySelectedSamplesUmap.length > 0) {
            x = onlySelectedSamplesUmap.map(item => item[1]);
            y = onlySelectedSamplesUmap.map(item => item[2]);
            text = onlySelectedSamplesUmap.map(item => item[0]);
            tracesRight.push(createTrace(x, y, text, 'highlighted'));
        }

        x = otherSamplesUmap.map(item => item[1]);
        y = otherSamplesUmap.map(item => item[2]);
        text = otherSamplesUmap.map(item => item[0]);
        tracesRight.push(createTrace(x, y, text, 'others'));
    }

    if (rightPlotMethod === 'pca') {
        if (onlySelectedSamplesPca.length > 0) {
            x = onlySelectedSamplesPca.map(item => item[pcaPlotAxis.right.x]);
            y = onlySelectedSamplesPca.map(item => item[pcaPlotAxis.right.y]);
            text = onlySelectedSamplesPca.map(item => item[0]);
            tracesRight.push(createTrace(x, y, text, 'highlighted'));
        }

        x = otherSamplesPca.map(item => item[pcaPlotAxis.right.x]);
        y = otherSamplesPca.map(item => item[pcaPlotAxis.right.y]);
        text = otherSamplesPca.map(item => item[0]);
        tracesRight.push(createTrace(x, y, text, 'others'));
    }

    return {
        left: tracesLeft,
        right: tracesRight
    };
}



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
        uirevision: 'true',
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

    Plotly.react(params.containerId, params.traces, layout, buttons);
    let plotDiv = document.getElementById(params.containerId);

    if (listenersAdded[params.containerId] === false) {
        listenersAdded[params.containerId] = true;
        addSelectedListener(params.containerId);
    }

}


function drawPlots() {
    let _traces = createTraces();
    drawPlot({containerId: 'plotDivLeft', traces: _traces.left});
    drawPlot({containerId: 'plotDivRight', traces: _traces.right});
}


function addSelectedListener(containerId) {
    let plotDiv = document.getElementById(containerId);
    plotDiv.on('plotly_selected', function(eventData) {
        if (eventData !== undefined) {
            selectedSamples = [];
            eventData.points.forEach(function(pt) {
                selectedSamples = [...selectedSamples, pt.text];
            });
            if (selectedSamples.length > 0) {
                if (controller.config.samplesSelectedCallback !== undefined && typeof controller.config.samplesSelectedCallback === "function") {
                    controller.config.samplesSelectedCallback(selectedSamples);
                }
                drawPlots();
            }
        } else {
            //handler(false);
        }
    });
}


let showPcaComponentSelects = false;

let umap_n_neighbors = 25;

function calc() {

    showLoadingAnimation = true;

    params['umap_n_neighbors'] = umap_n_neighbors;

    controller.pca(params, _result => {
        //callbackSuccess();
        showLoadingAnimation = false;
        result = _result;

        let numberOfCalculatedComponents = _result.pca_result[0].length - 1;
        _pcs = Array.from(Array(numberOfCalculatedComponents).keys()).map(x => x+1);
        _pcsLabels = _pcs.map(x => 'PC '+x);
        pcs = Object.fromEntries(_pcs.map((key, index)=> [key, _pcsLabels[index]]));
        
    
        //let pcaLabels;
        /*if (controller.config.sampleDisplayNameTransformer !== undefined && typeof controller.config.sampleDisplayNameTransformer === "function") {
            pcaLabels = result.umap_result.map(item => controller.config.sampleDisplayNameTransformer(item[0]));
        } else {
            pcaLabels = result.umap_result.map(item => item[0]);
        }*/

        showPcaResultPlot = 'block';
        showUmapResultPlot = 'block';


        drawPlots();

        showPcaComponentSelects = true;

        //addSelectedListener('plotDivLeft');
        //addSelectedListener('plotDivRight');
    });

}


function updatePlot(plot) {
    let _traces = createTraces();

    if (plot === 'left') {
        drawPlot({containerId: 'plotDivLeft', traces: _traces.left});
    }

    if (plot === 'right') {
        drawPlot({containerId: 'plotDivRight', traces: _traces.right});
    }
}

function onChangeRightPlotMethod() {
    let _traces = createTraces();
    drawPlot({containerId: 'plotDivRight', traces: _traces.right});
}


</script> 
 

<div>
    <div class="divbrowse-modal-dialogue-headline">Data Analysis</div>

    <div class="clearfix" style="margin-bottom: 10px;">
        <button on:click|preventDefault={calc} type="button" class="divbrowse-btn divbrowse-btn-light" style="float: left;">Calculate</button>
        {#if showLoadingAnimation}
        <div style="float:left;margin-left:20px;">
            <LoadingAnimation size="small" />
        </div>
        {/if}
    </div>

    <div class="clearfix">
        <div style="float:left; height: 600px; padding: 10px 20px; border: 1px solid rgb(100,100,100); background:rgb(240,240,240);">
            
            <div style="float: left; margin-top: 5px; font-weight: 400;">PCA</div>

            {#if showPcaComponentSelects}
            <div class="clearfix" style="float: left; margin-left: 20px;">
                <label class="form-label" for="pcaPlotAxisX">X axis: </label>
                <select class="divbrowse-form-control" id="pcaPlotAxisX" bind:value={pcaPlotAxis.left.x} on:change="{(event) => { updatePlot('left'); event.currentTarget.blur(); } }">
                    {#each Object.entries(pcs) as [pc, label]}
                    <option value="{pc}">{label}</option>
                    {/each}
                </select>

                <label class="form-label" for="pcaPlotAxisY">Y axis: </label>
                <select class="divbrowse-form-control" id="pcaPlotAxisY" bind:value={pcaPlotAxis.left.y} on:change="{(event) => { updatePlot('left'); event.currentTarget.blur(); } }">
                    {#each Object.entries(pcs) as [pc, label]}
                    <option value="{pc}">{label}</option>
                    {/each}
                </select>
            </div>
            {/if}

            <div style="clear:both;"></div>

            <div id="plotDivLeft" style="margin-top:20px; float: left; display: {showPcaResultPlot}; width: 520px; height: 520px; padding: 5px; border: 1px solid rgb(200,200,200); background: white;"></div>

        </div>
        <div style="float:left; height: 600px; padding: 10px 20px; border: 1px solid rgb(100,100,100);  background:rgb(240,240,240); margin-left:20px;">

            <select class="divbrowse-form-control" style="float:left;" id="rightPlotMethod" bind:value={rightPlotMethod} on:change="{(event) => { onChangeRightPlotMethod(); event.currentTarget.blur(); } }">
                <option value="umap">UMAP</option>
                <option value="pca">PCA</option>
            </select>

            {#if rightPlotMethod === 'umap'}
            <div style="float: left;">
                <label style="margin-left: 30px;">UMAP Neighbors: </label>
                <input bind:value={umap_n_neighbors} type="number" id="umap_n_neighbors" class="divbrowse-form-control" style="width: 40px;height: 30px; padding: 0 8px;">
            </div>
            {/if}

            {#if rightPlotMethod === 'pca' && showPcaComponentSelects}
            <div class="clearfix" style="float: left; margin-left: 20px;">
                <label class="form-label" for="pcaPlot2AxisX">X axis: </label>
                <select class="divbrowse-form-control" id="pcaPlot2AxisX" bind:value={pcaPlotAxis.right.x} on:change="{(event) => { updatePlot('right'); event.currentTarget.blur(); } }">
                    {#each Object.entries(pcs) as [pc, label]}
                    <option value="{pc}">{label}</option>
                    {/each}
                </select>

                <label class="form-label" for="pcaPlot2AxisY">Y axis: </label>
                <select class="divbrowse-form-control" id="pcaPlot2AxisY" bind:value={pcaPlotAxis.right.y} on:change="{(event) => { updatePlot('right'); event.currentTarget.blur(); } }">
                    {#each Object.entries(pcs) as [pc, label]}
                    <option value="{pc}">{label}</option>
                    {/each}
                </select>
            </div>
            {/if}

            <div style="clear:both;"></div>

            <div id="plotDivRight" style="margin-top: 20px; float: left; display: {showUmapResultPlot}; width: 520px; height: 520px; padding: 5px; border: 1px solid rgb(200,200,200); background: white;"></div>

        </div>

        {#if selectedSamples.length > 0}
        <div style="float:left; width: 300px; font-size: 0.85rem; margin-left: 25px; height: 600px; border: 1px solid rgb(100,100,100); padding: 10px; overflow-y: scroll;">
            <strong>You have selected {selectedSamples.length} genotypes:</strong><br />
            {#each selectedSamples as sample}
                {sample}<br />
            {/each}
        </div>
        {/if}

    </div>

    <!--

    <div class="clearfix">
        <button on:click|preventDefault={calc} type="button" class="divbrowse-btn divbrowse-btn-light" style="float:left;">Calculate PCA</button>




    </div>


    <div class="clearfix" style="margin-top: 15px;">


    </div>
    -->



</div>

<style lang="less">



</style>