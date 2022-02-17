<!--
<svelte:head>
  <script src="https://cdn.plot.ly/plotly-latest.min.js" type="text/javascript"></script>
</svelte:head>
-->
<script>
export let config;
export let appId;

import { onMount, setContext, getContext } from 'svelte';
import jquery from 'jquery';
import DataFrame from "dataframe-js";
//import Plotly from 'plotly.js-dist';

import EventEmitter from '/utils/eventbus';
import SnpbrowserController from '/lib/SnpbrowserController';

const eventbus = new EventEmitter();
const controller = new SnpbrowserController(eventbus);

const app = {
    appId: appId,
    eventbus: eventbus,
    controller: controller
}

setContext('app', {
    app: () => app
});

import getStores from '/utils/store';
const { settings, variantWidth, groups } = getStores();

import Navigation from '/components/Navigation.svelte';

import LoadingAnimation from '/components/utils/LoadingAnimation.svelte';
import RendererGapless from './renderer/RendererGapless.svelte';

import Modal from 'svelte-simple-modal';


let maxSamplesDisplayable = 5000;
let errorTooManySamples = false;

export function setSamples(_samples) {
    if (_samples.length < maxSamplesDisplayable) {
        errorTooManySamples = false;
        controller.setSamples(_samples);
    } else {
        errorTooManySamples = true;
    }
}

export function setGroups(_groups) {
    groups.set(_groups);
}

let snpbrowserMatrixContainer;

/*let settings = {
    statusShowMinimap: false,
    statusColorblindMode: false,
    variantDisplayMode: 'reference_mismatch'
};*/

onMount(async () => {
    console.log('Svelte App mounted!');
    let availableWidth = jquery(snpbrowserMatrixContainer).width(); // jquery('#snpbrowser-matrix-container').width();

    controller.setup({
        container: jquery(snpbrowserMatrixContainer), // jquery('#snpbrowser-matrix-container')
        config: config
    });

    /*let elt = document.body.querySelector("#snpbrowser-matrix-container");
    let rect = elt.getBoundingClientRect();
    //console.log(elt);
    //console.log(rect);
    //console.log(elt.clientWidth);*/

    let _debounce = function(ms, fn) {
        let timer;
        return function() {
            clearTimeout(timer);
            let args = Array.prototype.slice.call(arguments);
            args.unshift(this);
            timer = setTimeout(fn.bind.apply(fn, args), ms);
        };
    };

    /*let ro = new ResizeObserver(_debounce(500, function(muts) {
        console.log(muts);
    }));*/
    
    let resizeObserverStarted = false;
    let initResizeObserver = () => {
        console.log('ResizeObserver INITIATED ('+appId+')');
        const containerResizeObserver = new ResizeObserver(_debounce(500, function(entries) {
            if (resizeObserverStarted === false) {
                resizeObserverStarted = true;
                console.log('ResizeObserver OMITTED FIRST CALL ('+appId+')');
                console.log(entries);
            } else {
                console.log('ResizeObserver INVOKED ('+appId+')');
                console.log(entries);
                
                let containerWidth = entries[0].contentBoxSize[0].inlineSize;
                if (containerWidth > 0) {
                    console.log('ResizeObserver controller.draw() INVOKED ('+appId+')');
                    controller.draw();
                }
            }
        }));
        containerResizeObserver.observe(snpbrowserMatrixContainer);
    }
    setTimeout( () => initResizeObserver(), 1000);

    
   let script = document.createElement('script');
   script.src = "https://cdn.plot.ly/plotly-latest.min.js"
   document.head.append(script);

   /*script.onload = function() {
       //drawPlot();
   };*/

});

let data = false;
let variants = false;

eventbus.on('data:display:changed', _data => {
    data = _data;
});


let showLoadingAnimation = false;
eventbus.on('loading:animation', msg => {
    showLoadingAnimation = msg.status;
});


jquery(document).on({
    mouseenter: function (event) {
        let elem = jquery(this);
        let position = elem.data('position');
        jquery("div#"+appId+" span.positions[data-position="+position+"]").addClass('highlight');
        jquery("#snp-"+position).addClass('highlight-snp');
    },
    mouseleave: function () {
        let elem = jquery(this);
        let position = elem.data('position');
        jquery("div#"+appId+" span.positions[data-position="+position+"]").removeClass('highlight');
        jquery("#snp-"+position).removeClass('highlight-snp');
    }
}, "div#"+appId+" span.snp,div#"+appId+" span.snpeff-indicator,div#"+appId+" span.maf-indicator");


let timer;
function handleWindowResize(event) {
    clearTimeout(timer);
    timer = setTimeout(() => {
        //console.log('handleWindowResize() was triggered');
        //controller.draw();
    }, 200);
}

</script>

<svelte:window on:resize={handleWindowResize}/>

<div>

    <div id="{appId}" class="divbrowse-container">

        <Navigation config={config} bind:settings={$settings} />

        <div id="snpbrowser-matrix-container" bind:this={snpbrowserMatrixContainer} ref="matrix-pane-container" class:colorblind={$settings.statusColorblindMode} class:nucleotides={$settings.variantDisplayMode === 'nucleotides'}>
            {#if errorTooManySamples === true}
            <div><p style="padding:30px;">The size of your collection exceeds the maximum of {maxSamplesDisplayable} samples to be displayed simultaneously.
            Please decrease the size of your collection below the value of {maxSamplesDisplayable} samples.</p></div>
            {:else if data.error !== undefined}
            <div><p style="padding:30px;">Error: {data.error}</p></div>
            {:else}
            <Modal>
                <RendererGapless data={data} statusShowMinimap={$settings.statusShowMinimap} />
            </Modal>
            {/if}
        </div>

    </div>

</div>


<style lang="less">

@trackHeight: 20px;
@trackHeightReference: 39px;

@fontsizeNucleotideLetter: 13px;
@fontsizeSnpPosition: 12px;
@snpBorderRadius: 1px;

main {
    /*text-align: center;*/
    /*padding: 1em;*/
    /*max-width: 240px;*/
    margin: 0 auto;
}

h1 {
    color: #ff3e00;
    text-transform: uppercase;
    font-size: 4em;
    font-weight: 100;
}



* {
  box-sizing: border-box;
}

.divbrowse-container {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;

    border: 1px solid rgb(0,0,0);
    padding: 10px;
    font-family: 'Roboto', sans-serif;
    background: rgb(220,220,220);
}

#snpbrowser-matrix-container {
    /*border: 1px dashed rgb(150,150,150);*/
    border: 1px solid rgb(70, 70, 70);
    background: rgb(255,255,255);
    min-height: 300px;
}


:global(.snpbrowser-nav label) {
    font-size: 14px;
    line-height: 0.8 !important;
}

:global(.snpbrowser-nav input) {
    font-size: 14px;
    line-height: 0.8 !important;
}

:global(.snpbrowser-nav select) {
    font-size: 14px;
    line-height: 0.8 !important;
}

:global(.snpbrowser-nav button) {
    font-size: 13px;
    line-height: 0.8 !important;
}


:global(.divbrowse-modal-dialogue-headline) {
    margin-bottom: 15px;
    font-weight: bold;
    font-size: 1.2rem;
}


:global(.divbrowse-form-control) {
    /*height: 25px;*/
    /*font-size: 14px;*/
    padding: 4px 8px;
    margin: 0px;
    border: 1px solid rgb(120,120,120);
    border-radius: 5px;
    margin-right: 5px;
}

:global(select.divbrowse-form-control) {
    padding: 2px 8px;
    height: 30px;
}

:global(input.divbrowse-form-control) {
    padding: 2px 8px;
    height: 30px;
}

:global(.divbrowse-btn) {
    height: 30px;
    padding: 1px 8px;
    border-radius: 4px;
    
}

:global(.divbrowse-btn-light) {
    /*background: #f8f9fa;*/
    /*background-color: rgb(235,235,235);*/
    box-shadow: inset 1px 1px 1px 0px #FFF, inset -1px -1px 0px 0px rgba(0,0,0,0.4);
    /*border: 1px solid #dcdcdc;*/
    border-radius: 2px;

    background: #f8f9fa;
    background: linear-gradient(to bottom, #f0f0f0, #e0e0e0);
    border: 1px solid rgb(180,180,180);
    border-top: 1px solid rgb(150,150,150);
    border-left: 1px solid rgb(150,150,150);
}

:global(.divbrowse-btn-light:hover) {
    background: #f8f9fa;
    background: linear-gradient(to bottom, #f0f0f0, #e0e0e0);
    border: 1px solid rgb(150,150,150);
}

:global(.divbrowse-btn-light[disabled]) {
    opacity: 0.6;
}

:global(.divbrowse-btn-light[disabled]:hover) {
    background: #f8f9fa;
    background: linear-gradient(to bottom, #f8f9fa, #e9e9e9);
    border: 1px solid rgb(200,200,200);
}





:global(.clearfix::after) {
    content: "";
    clear: both;
    display: table;
}




:global {
    div.track {
        /*background: rgb(235,235,235);*/
        height: @trackHeight;
        box-sizing: border-box;
        /*border-bottom: 1px solid rgb(220,220,220);*/
        padding-top: 0px;

        display: inline-flex;
        align-items: center;
        justify-content: flex-start;

        &.reference {
            font-weight: 500;
            height: @trackHeightReference;
        }
    }
}


:global {
    div.track.positions {
        border-bottom: 1px solid rgb(220,220,220);
        height: 100px;
        box-sizing: border-box;

        > div.label {
            height: 100px;
        }
    }
}

:global {
    span.snp {
        font-family: 'Source Code Pro', monospace;

        display: inline-block;

        text-align: center;
        margin: 0;
        padding: 0;
        box-sizing: border-box;

        min-height: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;

        border-radius: @snpBorderRadius;
        margin-right: 0px;

        font-size: @fontsizeNucleotideLetter;
        line-height: @fontsizeNucleotideLetter;

        font-weight:500;
    }
}

:global {
    span.positions {

        &.highlight {
            background-color: rgb(200,200,200) !important;
        }

        writing-mode: vertical-rl;
        box-sizing: border-box;
        
        height: 100px;

        display: inline-flex;
        align-items: center;
        justify-content: flex-start;
        

        border: 0px solid black;
        border-left: 1px solid rgb(200,200,200);
        border-right: 1px solid white;
        padding-top: 10px;
        font-size: @fontsizeSnpPosition;
        line-height: @fontsizeSnpPosition;
        font-weight: 500;
        
        /*background: rgb(240,240,240);*/
    }
}


.nucl() {
    .A() {
        &:before { content: "A"; }
    }
    .G() {
        &:before { content: "G"; }
    }
    .T() {
        &:before { content: "T"; }
    }
    .C() {
        &:before { content: "C"; }
    }
}

.nucl-bg() {
    .A() {
        background-color: #2ecc71;
    }
    .G() {
        background-color: #f1c40f;
    }
    .T() {
        background-color: #e74c3c;
    }
    .C() {
        background-color: #3498db;
    }

    .colorblind() {
        .A() {
            background-color: #F0E442;
        }
        .G() {
            background-color: #a6cee3;
        }
        .T() {
            background-color: #E69F00;
        }
        .C() {
            background-color: #1f78b4;
        }
    }
}


.ref-mixin() {
    .letters() {
        &.ref-A {
            .nucl.A();
        }
        &.ref-G {
            .nucl.G();
        }
        &.ref-T {
            .nucl.T();
        }
        &.ref-C {
            .nucl.C();
        }
    }
    .backgrounds() {
        &.ref-A {
            .nucl-bg.A();
        }
        &.ref-G {
            .nucl-bg.G();
        }
        &.ref-T {
            .nucl-bg.T();
        }
        &.ref-C {
            .nucl-bg.C();
        }

        .colorblind() {
            &.ref-A {
                .nucl-bg.colorblind.A();
            }
            &.ref-G {
                .nucl-bg.colorblind.G();
            }
            &.ref-T {
                .nucl-bg.colorblind.T();
            }
            &.ref-C {
                .nucl-bg.colorblind.C();
            }
        }
    }
}


:global {
    span.reference {
        .ref-mixin.letters();
        .ref-mixin.backgrounds();
    }
}

:global {
    #snpbrowser-matrix-container.colorblind span.reference {
        .ref-mixin.backgrounds.colorblind();
    }
}


.alt-mixin() {
    .letters() {
        &.alt-A {
            .nucl.A();
        }
        &.alt-G {
            .nucl.G();
        }
        &.alt-T {
            .nucl.T();
        }
        &.alt-C {
            .nucl.C();
        }
    }
    .backgrounds() {
        &.alt-A {
            .nucl-bg.A();
        }
        &.alt-G {
            .nucl-bg.G();
        }
        &.alt-T {
            .nucl-bg.T();
        }
        &.alt-C {
            .nucl-bg.C();
        }

        .colorblind() {
            &.alt-A {
                .nucl-bg.colorblind.A();
            }
            &.alt-G {
                .nucl-bg.colorblind.G();
            }
            &.alt-T {
                .nucl-bg.colorblind.T();
            }
            &.alt-C {
                .nucl-bg.colorblind.C();
            }
        }
    }
}

.hetero-mixin() {
    .letters() {
        &.ref-T.alt-C, &.alt-T.ref-C {
            &:before { content: "Y"; }
        }
        &.ref-T.alt-G, &.ref-G.alt-T  {
            &:before { content: "K"; }
        }
        &.ref-C.alt-A, &.ref-A.alt-C  {
            &:before { content: "M"; }
        }
        &.ref-C.alt-G, &.ref-G.alt-C  {
            &:before { content: "S"; }
        }
        &.ref-T.alt-A, &.ref-A.alt-T  {
            &:before { content: "W"; }
        }
        &.ref-G.alt-A, &.ref-A.alt-G  {
            &:before { content: "R"; }
        }
    }
    .backgrounds() {
        background-color: #aa34ff;
    }
}

:global {
    span.snp {
        &.snp--1 {
            background-color: white;
            &:before { content: "\00a0"; }
        }
        &.snp-0 {
            background-color: rgb(219, 240, 216); /* 219, 240, 216 */
            .ref-mixin.letters();
            color: rgb(190,190,190);
        }
        &.snp-1 {
            background-color: rgb(255, 136, 71); /* red;  */
            .hetero-mixin.letters();
        }
        &.snp-2 {
            background-color: rgb(153, 191, 222); /*  #aa34ff;   160, 136, 227         136, 171, 227 */
            .alt-mixin.letters();
        }
    }
}

:global {
    #snpbrowser-matrix-container.nucleotides {
        span.snp {
            &.snp--1 {
                background-color: white;
                &:before { content: "\00a0"; }
            }
            &.snp-0 {
                .ref-mixin.letters();
                .ref-mixin.backgrounds();
                border:0px solid black;
                color: black;
            }
            &.snp-1 {
                .hetero-mixin.letters();
                .hetero-mixin.backgrounds();
            }
            &.snp-2 {
                .alt-mixin.letters();
                .alt-mixin.backgrounds();
            }
        }
    }
}

:global {
    #snpbrowser-matrix-container.colorblind.nucleotides {
        span.snp {
            &.snp--1 {
                background-color: white;
                &:before { content: "\00a0"; }
            }
            &.snp-0 {
                .ref-mixin.letters();
                .ref-mixin.backgrounds.colorblind();
                color: black;
            }
            &.snp-1 {
                .hetero-mixin.letters();
                .hetero-mixin.backgrounds();
            }
            &.snp-2 {
                .alt-mixin.letters();
                .alt-mixin.backgrounds.colorblind();
            }
        }
    }
}

</style>