<script>
export let data;
export let samples;

import { onMount, getContext } from 'svelte';

const context = getContext('app');
let { appId, eventbus, controller } = context.app();

import getStores from '/utils/store';
const { sortSettings, variantWidth, variantFilterSettings, filteredVariantsCoordinates } = getStores();

import { debounce, numberOfAltAllelesFactory } from '/utils/helpers';
import { delegate } from 'tippy.js';
import tippy, { followCursor } from 'tippy.js';

let canvas;
let widthAllVariants;
let framesPerSecond = 10;
let timeoutHandle;
let frame;
let canvasHeight = samples.length;
let canvasScrollTop = 0;

let ctx = false;



const ploidy = controller.metadata.ploidy;

const numberOfAlternateAlleles = numberOfAltAllelesFactory.getFunction(ploidy);


function isFiltered(pos, gt) {
    if ( gt.every(el => el < 0) ) {
        return false;
    }
    if (data.filtered_variants_coordinates.includes( pos ) === false) {
        return true;
    } else {
        return false;
    }
}





function drawSampleVariants(samples, calledFrom = '') {

    //console.warn('Minimap::drawSampleVariants() called from: ', calledFrom);

    if (canvas === undefined) {
        console.log('drawSampleVariants() EARLY EXIT no canvas available');
        return false;
    }

    //console.info('drawSampleVariants() CALLED');

    //ctx.clearRect(0, 0, widthAllVariants, canvasHeight);

    ////clearTimeout(timeoutHandle);
    //cancelAnimationFrame(frame);

    let frameCounter = 0;

    samples = samples.slice(canvasScrollTop, canvasScrollTop + 500);

    let _sampleIds = samples.map(elem => elem[0]);
    controller.DataLoader.lazyLoadVariantCalls(_sampleIds, () => { return false; });

    //console.log(canvasScrollTop);

    (function loop() {

        //let row = 0;
        let row = canvasScrollTop;
        //console.warn(row);
        //console.warn(data.variants_coordinates.length);

        for (let sample of samples) {
            let sampleId = sample[0];
            //console.log(sampleId);
            let xPos = 0;

            for (let col = 0; col < data.variants_coordinates.length; col++) {
                
                xPos = col * $variantWidth;

                //console.log(data.calls.get(sampleId));
                if (data.calls.get(sampleId) === null) {
                    continue;
                }

                let numAltAlleles = numberOfAlternateAlleles(data.calls.get(sampleId)[col]);

                if (numAltAlleles == -1) {
                    ctx.fillStyle = "rgb(255,255,255)";
                }

                if (numAltAlleles == 0) {
                    ctx.fillStyle = "rgb(219, 240, 216)";
                    //ctx.fillStyle = "rgb(255,255,255)";
                }

                if (numAltAlleles == 1) {
                    ctx.fillStyle = "rgb(255, 136, 71)";
                }

                if (numAltAlleles == 2) {
                    //ctx.fillStyle = "rgb(153, 191, 222)";
                    ctx.fillStyle = "rgb(133, 171, 222)";
                }

                if (isFiltered(data.variants_coordinates[col], data.calls.get(sampleId)[col])) {
                    ctx.fillStyle = "rgb(255,255,255)";
                }

                ctx.fillRect(xPos, row, $variantWidth, 1);
            }
            row += 1;
        }

        frame = requestAnimationFrame(loop);

        frameCounter += 1;
        if (frameCounter > 5) {
            cancelAnimationFrame(frame);
        }

    }());
}



sortSettings.subscribe(value => {
    if (ctx !== false) {
        //ctx.clearRect(0, 0, widthAllVariants, canvasHeight);
    }
});


$: {
    samples;

    canvasHeight = samples.length;
    widthAllVariants = controller.getCurrentWidthOfVariants();
    drawSampleVariants(samples, 'reactive block');
}

/*variantWidth.subscribe(value => {
    console.log('variantWidth: ', value);
    //drawSampleVariants(samples);
    let _start = canvasScrollTop;
    let _end = _start + 500;
    let sampleIds = samples.slice(_start, _end).map(elem => elem[0]);
    controller.DataLoader.lazyLoadVariantCalls(sampleIds, () => {
        drawSampleVariants(samples, 'variantWidth.subscribe');
    });
});*/

function getMousePos(canvas, evt) {
    let rect = canvas.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}

onMount(() => {
    ctx = canvas.getContext('2d');

    let sampleIds = samples.slice(0, 500).map(elem => elem[0]);
    controller.DataLoader.lazyLoadVariantCalls(sampleIds);

    drawSampleVariants(samples, 'onMount');

    canvas.addEventListener('click', function(evt) { // mousemove
        let mousePos = getMousePos(canvas, evt);
        eventbus.emit('minimap:click', {y: mousePos.y});
    }, false);
});



const canvasOnScrollDebounced = debounce((event) => {
    let _start = parseInt(event.target.scrollTop);
    canvasScrollTop = _start;
    let _end = _start + 500;
    let sampleIds = samples.slice(_start, _end).map(elem => elem[0]);
    controller.DataLoader.lazyLoadVariantCalls(sampleIds, () => {
        drawSampleVariants(samples, 'canvasOnScrollDebounced');
    });
}, 500);





/*************************************
 * Tippy related code following
 *************************************/

 let tippyProps = {
    delay: 0,
    //appendTo: 'parent',
    target: '.'+appId+' #canvas-minimap',
    animation: false,
    content: "<span class='tooltip'></span>",
    //placement: "bottom",
    allowHTML: true,
    followCursor: true,

    onShow(instance) {
        let content = [];
        content.push('test');
        instance.setContent(content.join("<br />"));
    }
};

let tippyInstances;
let tippyInstancesInitialized = false;

/*onMount(async () => {
    if (tippyInstancesInitialized === false) {
        tippyInstances = delegate('body', tippyProps);
        tippyInstancesInitialized = true;
    }
});*/

onMount(async () => {

    /*tippy('#test', {
        content: 'My tooltip!',
        plugins: [followCursor],
        followCursor: true,
    });*/

});



</script>

<div class="track minimap" style="position: absolute; top: 0px; left: 0px; z-index: 900; height: 400px; width: 100%;">
    <div class="label">Compressed view</div>
    <div id="test" on:scroll={ (event) => canvasOnScrollDebounced(event) } style="max-height: 399px; overflow-y: scroll; flex-grow: 1; margin-top: 1px;">
        <canvas id="canvas-minimap" bind:this={canvas} width={widthAllVariants} height={canvasHeight}></canvas>
    </div>
</div>

<style lang="less">
.track.minimap {
    background: white;
    border-bottom: 1px solid rgb(100,100,100);
    box-sizing: border-box;
}
.label {
    background: white;
}
</style>