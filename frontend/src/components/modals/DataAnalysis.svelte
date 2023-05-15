<script>
export let params;

import { onMount, getContext } from 'svelte';
const context = getContext('app');
let { controller } = context.app();

const rootElem = getContext('rootElem');

import LoadingAnimation from '@/components/utils/LoadingAnimation.svelte';
//import Plotly from 'plotly.js-dist';
//import Plotly from 'plotly.js-gl2d-dist'


let showPcaResultPlot = 'block';
let showUmapResultPlot = 'block';
let selectedSamples = [];
let showLoadingAnimation = false;

let result = {};

let rightPlotMethod = 'umap';

if (!controller.metadata.features.umap) {
    rightPlotMethod = 'pca';
}


let _pcs = Array.from(Array(10).keys()).map(x => x+1);
let _pcsLabels = _pcs.map(x => 'PC '+x);
let pcs = Object.fromEntries(_pcs.map((key, index)=> [key, _pcsLabels[index]]));

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
        selected: {
		    marker: {
			    color: '#0000FF',
		    }
        }
    }
    return trace;
}


function createTraces() {

    if (selectedSamples.length > 0) {

    }

    let onlySelectedSamplesPca = result.pca_result.filter(item => selectedSamples.includes(item[0]) );
    let otherSamplesPca = result.pca_result.filter(item => selectedSamples.includes(item[0]) === false );

    let onlySelectedSamplesUmap, otherSamplesUmap;
    if (result.umap_result != null) {
        onlySelectedSamplesUmap = result.umap_result.filter(item => selectedSamples.includes(item[0]) );
        otherSamplesUmap = result.umap_result.filter(item => selectedSamples.includes(item[0]) === false );
    }

    /*
    let umapLabels;

    if (controller.config.sampleDisplayNameTransformer !== undefined && typeof controller.config.sampleDisplayNameTransformer === "function") {
        umapLabels = result.umap_result.map(item => controller.config.sampleDisplayNameTransformer(item[0]));
    } else {
        umapLabels = result.umap_result.map(item => item[0]);
    }
    */

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



    if (rightPlotMethod === 'umap' && result.umap_result != null) {
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

    let plotlyContainer = rootElem.querySelector('#'+params.containerId);

    //Plotly.react(params.containerId, params.traces, layout, buttons);
    //console.log(params.traces);
    Plotly.react(plotlyContainer, params.traces, layout, buttons);
    //let plotDiv = document.getElementById(params.containerId);

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

function unsetPointSelection() {
    var updatedData = {
        //'marker.color': 'red',
		//'selectedpoints': [selec],
        'selectedpoints': [[]],
        'selected': {
		    'marker': {
			    'color': '#0000FF',
		    }
        },
        'unselected': {
		    'marker': {
			    'color': '#000000',
		    }
        }
    };
    Plotly.update(rootElem.querySelector('#plotDivLeft'), updatedData);
    Plotly.update(rootElem.querySelector('#plotDivRight'), updatedData);
}

function addSelectedListener(containerId) {
    let plotDiv = rootElem.querySelector('#'+containerId);
    plotDiv.on('plotly_selected', function(eventData) {
        if (eventData !== undefined) {
            selectedSamples = [];

            for (let point of eventData.points) {
                selectedSamples = [...selectedSamples, point.text];
            }

            if (selectedSamples.length > 0) {
                if (controller.config.samplesSelectedCallback !== undefined && typeof controller.config.samplesSelectedCallback === "function") {
                    controller.config.samplesSelectedCallback(selectedSamples);
                }
                unsetPointSelection();
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

            {#if controller.metadata.features.umap}
            <select class="divbrowse-form-control" style="float:left;" id="rightPlotMethod" bind:value={rightPlotMethod} on:change="{(event) => { onChangeRightPlotMethod(); event.currentTarget.blur(); } }">
                <option value="umap">UMAP</option>
                <option value="pca">PCA</option>
            </select>
            {:else}
            <div style="float: left; margin-top: 5px; font-weight: 400;">PCA</div>
            {/if}

            {#if rightPlotMethod === 'umap'}
            <div style="float: left;">
                <label for="umap_n_neighbors" style="margin-left: 30px; font-size:90%;">UMAP Neighbors: </label>
                <input bind:value={umap_n_neighbors} type="number" id="umap_n_neighbors" class="divbrowse-form-control" style="width: 60px;height: 30px; padding: 0 8px;">
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
        <div style="float:left; width: 300px; font-size: 90%; margin-left: 25px; height: 500px; border: 1px solid rgb(100,100,100); padding: 10px; overflow-y: scroll;">
            <button style="margin-bottom: 8px;display: block;" on:click|preventDefault={() => { unsetPointSelection(); selectedSamples = []; } }>Unset selection</button>
            <strong>You have selected {selectedSamples.length} genotypes:</strong><br />
            {#each selectedSamples as sample}
                {sample}<br />
            {/each}
        </div>
        {/if}

    </div>

</div>

<style lang="less" global>

.js-plotly-plot .plotly,.js-plotly-plot .plotly div {
    direction:ltr;
    font-family:'Open Sans', verdana, arial, sans-serif;
    margin:0;
    padding:0;
}
.js-plotly-plot .plotly input,.js-plotly-plot .plotly button {
    font-family:'Open Sans', verdana, arial, sans-serif;
}
.js-plotly-plot .plotly input:focus,.js-plotly-plot .plotly button:focus {
    outline:none;
}
.js-plotly-plot .plotly a {
    text-decoration:none;
}
.js-plotly-plot .plotly a:hover {
    text-decoration:none;
}
.js-plotly-plot .plotly .crisp {
    shape-rendering:crispEdges;
}
.js-plotly-plot .plotly .user-select-none {
    -webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;-o-user-select:none;
    user-select:none;
}
.js-plotly-plot .plotly svg {
    overflow:hidden;
}
.js-plotly-plot .plotly svg a {
    fill:#447adb;
}
.js-plotly-plot .plotly svg a:hover {
    fill:#3c6dc5;
}
.js-plotly-plot .plotly .main-svg {
    position:absolute;
    top:0;
    left:0;
    pointer-events:none;
}
.js-plotly-plot .plotly .main-svg .draglayer {
    pointer-events:all;
}
.js-plotly-plot .plotly .cursor-default {
    cursor:default;
}
.js-plotly-plot .plotly .cursor-pointer {
    cursor:pointer;
}
.js-plotly-plot .plotly .cursor-crosshair {
    cursor:crosshair;
}
.js-plotly-plot .plotly .cursor-move {
    cursor:move;
}
.js-plotly-plot .plotly .cursor-col-resize {
    cursor:col-resize;
}
.js-plotly-plot .plotly .cursor-row-resize {
    cursor:row-resize;
}
.js-plotly-plot .plotly .cursor-ns-resize {
    cursor:ns-resize;
}
.js-plotly-plot .plotly .cursor-ew-resize {
    cursor:ew-resize;
}
.js-plotly-plot .plotly .cursor-sw-resize {
    cursor:sw-resize;
}
.js-plotly-plot .plotly .cursor-s-resize {
    cursor:s-resize;
}
.js-plotly-plot .plotly .cursor-se-resize {
    cursor:se-resize;
}
.js-plotly-plot .plotly .cursor-w-resize {
    cursor:w-resize;
}
.js-plotly-plot .plotly .cursor-e-resize {
    cursor:e-resize;
}
.js-plotly-plot .plotly .cursor-nw-resize {
    cursor:nw-resize;
}
.js-plotly-plot .plotly .cursor-n-resize {
    cursor:n-resize;
}
.js-plotly-plot .plotly .cursor-ne-resize {
    cursor:ne-resize;
}
.js-plotly-plot .plotly .cursor-grab {
    cursor:-webkit-grab;
    cursor:grab;
}
.js-plotly-plot .plotly .modebar {
    position:absolute;
    top:2px;
    right:2px;
}
.js-plotly-plot .plotly .ease-bg {
    -webkit-transition:background-color 0.3s ease 0s;-moz-transition:background-color 0.3s ease 0s;-ms-transition:background-color 0.3s ease 0s;-o-transition:background-color 0.3s ease 0s;
    transition:background-color 0.3s ease 0s;
}
.js-plotly-plot .plotly .modebar--hover>:not(.watermark) {
    opacity:0;-webkit-transition:opacity 0.3s ease 0s;-moz-transition:opacity 0.3s ease 0s;-ms-transition:opacity 0.3s ease 0s;-o-transition:opacity 0.3s ease 0s;
    transition:opacity 0.3s ease 0s;
}
.js-plotly-plot .plotly:hover .modebar--hover .modebar-group {
    opacity:1;
}
.js-plotly-plot .plotly .modebar-group {
    float:left;
    display:inline-block;
    box-sizing:border-box;
    padding-left:8px;
    position:relative;
    vertical-align:middle;
    white-space:nowrap;
}
.js-plotly-plot .plotly .modebar-btn {
    position:relative;
    font-size:16px;
    padding:3px 4px;
    height:22px;
    cursor:pointer;
    line-height:normal;
    box-sizing:border-box;
}
.js-plotly-plot .plotly .modebar-btn svg {
    position:relative;
    top:2px;
}
.js-plotly-plot .plotly .modebar.vertical {
    display:flex;
    flex-direction:column;
    flex-wrap:wrap;
    align-content:flex-end;
    max-height:100%;
}
.js-plotly-plot .plotly .modebar.vertical svg {
    top:-1px;
}
.js-plotly-plot .plotly .modebar.vertical .modebar-group {
    display:block;
    float:none;
    padding-left:0px;
    padding-bottom:8px;
}
.js-plotly-plot .plotly .modebar.vertical .modebar-group .modebar-btn {
    display:block;
    text-align:center;
}
.js-plotly-plot .plotly [data-title]:before,.js-plotly-plot .plotly [data-title]:after {
    position:absolute;-webkit-transform:translate3d(0, 0, 0);-moz-transform:translate3d(0, 0, 0);-ms-transform:translate3d(0, 0, 0);-o-transform:translate3d(0, 0, 0);transform:translate3d(0, 0, 0);display:none;
    opacity:0;
    z-index:1001;
    pointer-events:none;
    top:110%;right:50%;
}
.js-plotly-plot .plotly [data-title]:hover:before,.js-plotly-plot .plotly [data-title]:hover:after {
    display:block;
    opacity:1;
}
.js-plotly-plot .plotly [data-title]:before {
    content:'';position:absolute;
    background:transparent;
    border:6px solid transparent;
    z-index:1002;
    margin-top:-12px;
    border-bottom-color:#69738a;
    margin-right:-6px;
}
.js-plotly-plot .plotly [data-title]:after {
    content:attr(data-title);background:#69738a;
    color:white;
    padding:8px 10px;
    font-size:12px;
    line-height:12px;
    white-space:nowrap;
    margin-right:-18px;
    border-radius:2px;
}
.js-plotly-plot .plotly .vertical [data-title]:before,.js-plotly-plot .plotly .vertical [data-title]:after {
    top:0%;right:200%;
}
.js-plotly-plot .plotly .vertical [data-title]:before {
    border:6px solid transparent;
    border-left-color:#69738a;
    margin-top:8px;
    margin-right:-30px;
}
.js-plotly-plot .plotly .select-outline {
    fill:none;
    stroke-width:1;
    shape-rendering:crispEdges;
}
.js-plotly-plot .plotly .select-outline-1 {
    stroke:white;
}
.js-plotly-plot .plotly .select-outline-2 {
    stroke:black;
    stroke-dasharray:2px 2px;
}
.plotly-notifier {
    font-family:'Open Sans', verdana, arial, sans-serif;
    position:fixed;
    top:50px;
    right:20px;
    z-index:10000;
    font-size:10pt;
    max-width:180px;
}
.plotly-notifier p {
    margin:0;
}
.plotly-notifier .notifier-note {
    min-width:180px;
    max-width:250px;
    border:1px solid #fff;
    z-index:3000;
    margin:0;
    background-color:#8c97af;
    background-color:rgba(140,151,175,0.9);color:#fff;
    padding:10px;
    overflow-wrap:break-word;
    word-wrap:break-word;-ms-hyphens:auto;-webkit-hyphens:auto;
    hyphens:auto;
}
.plotly-notifier .notifier-close {
    color:#fff;
    opacity:0.8;
    float:right;
    padding:0 5px;
    background:none;
    border:none;
    font-size:20px;
    font-weight:bold;
    line-height:20px;
}
.plotly-notifier .notifier-close:hover {
    color:#444;
    text-decoration:none;
    cursor:pointer
}

</style>