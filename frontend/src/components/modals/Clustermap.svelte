<script>
export let params;

import { onMount, getContext } from 'svelte';
const context = getContext('app');
let { controller } = context.app();

const rootElem = getContext('rootElem');

import LoadingAnimation from '@/components/utils/LoadingAnimation.svelte';
    import App from '@/App.svelte';
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

let fontscale = 2.5;

let base64imageStr = undefined;
let zoomlvl = 0.0;

let widthOrig = 1948;

let max = widthOrig;
let min = 600;

let widthScaled;
let zoomfactor;

$: widthScaled = zoomlvl * (max - min) + min;
$: zoomfactor = (widthScaled / widthOrig) * 100;


// function to calculate the mean of an array of integers




function calc() {

    showLoadingAnimation = true;

    params['fontscale'] = fontscale;

    controller.clustermap(params, _result => {
        showLoadingAnimation = false;
        result = _result;
        base64imageStr = result.clustermap;
    });

}

</script> 
 

<div style="width: 70vw;">
    <div class="divbrowse-modal-dialogue-headline">Clustermap</div>

    <div class="clearfix" style="margin-bottom: 10px;">
        <button on:click|preventDefault={calc} type="button" class="divbrowse-btn divbrowse-btn-light" style="float: left;">Calculate</button>
        {#if showLoadingAnimation}
        <div style="float:left;margin-left:20px;">
            <LoadingAnimation size="small" />
        </div>
        {/if}

        <div style="border: 1px solid rgb(150,150,150); display: inline-block; margin-left: 25px; padding: 5px 9px; position: relative; width: 260px;">
            <label for="zoom">Zoom: {parseInt(zoomfactor)}%</label> <input id="zoom" bind:value={zoomlvl} type="range" min="0" max="1" step="any" style="position: absolute; top:3px; left:110px;" />
        </div>

        <div style="border: 1px solid rgb(150,150,150); display: inline-block; margin-left: 25px; padding: 5px 9px; position: relative;">
            <label for="fontscale">Font size:</label> <input bind:value={fontscale} id="fontscale" type="number" step="0.1" min="1" max="3" />
        </div>

        
    </div>

    <div style="border: 1px solid black; padding: 0; width: 610px; height: 610px; overflow: auto; box-sizing:content-box;">
        {#if base64imageStr}
        <img src="data:image/png;base64,{base64imageStr}" alt="clustermap" style="width: {widthScaled}px;" />
        {/if}
    </div>

</div>

<style lang="less" global>

</style>