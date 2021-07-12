<script>
export let data;
export let variants;

import { onMount, getContext } from 'svelte';

const context = getContext('app');
let { eventbus, controller } = context.app();

let canvas;
let widthAllVariants;
let framesPerSecond = 10;
let timeoutHandle;
let frame;
let countVariants = variants.length;
let canvasHeight = countVariants;
let countSamples = 0;
let trackHeight = 0;


function drawVariants(variants) {

    if (canvas === undefined) {
        console.log('drawVariants() EARLY EXIT no canvas available');
        return false;
    }
    //window.requestAnimationFrame();

    let ctx = canvas.getContext('2d');

    ctx.clearRect(0, 0, widthAllVariants, canvasHeight);

    clearTimeout(timeoutHandle);
    cancelAnimationFrame(frame);

    let counter = 0;

    (function loop() {
    //function loop() {
    	
            frame = requestAnimationFrame(loop);

            // ==================================================================
            let row = 0;
            //for (let [sampleId, sampleVariants] of Object.entries(variants)) {
            for (let sample of variants) {
                let sampleId = sample[0];
                let sampleVariants = sample[1].variants;

                let col = 0;
                let xPos = 0;

                for (let sampleVariant of sampleVariants) {
                    xPos = col * 20;
                    col += 1;

                    if (sampleVariant == -1) {
                        ctx.fillStyle = "rgb(255,255,255)";
                    }

                    if (sampleVariant == 0) {
                        ctx.fillStyle = "rgb(219, 240, 216)";
                        //ctx.fillStyle = "rgb(255,255,255)";
                    }

                    if (sampleVariant == 1) {
                        ctx.fillStyle = "rgb(255, 136, 71)";
                    }

                    if (sampleVariant == 2) {
                        //ctx.fillStyle = "rgb(153, 191, 222)";
                        ctx.fillStyle = "rgb(133, 171, 222)";
                    }

                    ctx.fillRect(xPos, row, 20, 1);
                }
                row += 1;
            }
            //ctx.fillStyle = "rgb(0, 0, 0)";
            //ctx.fillRect(20, 20, 100, 50);

            counter += 1;
            if (counter > 60) {
                cancelAnimationFrame(frame);
            }

            // ==================================================================


    }());
    //}
    //loop();

}


let _data, _variants;
$: {
    _data = data;
    _variants = variants;
    countSamples = _variants.length;
    trackHeight = countSamples;
    if (trackHeight > 400) {
        trackHeight = 400;
    }
    widthAllVariants = controller.getCurrentWidthOfVariants();
    drawVariants(_variants);
}

function getMousePos(canvas, evt) {
    let rect = canvas.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}

onMount(() => {
    drawVariants(_variants);

    canvas.addEventListener('click', function(evt) { // mousemove
        let mousePos = getMousePos(canvas, evt);
        //let message = 'Mouse position: ' + mousePos.x + ',' + mousePos.y;
        eventbus.emit('minimap:click', {y: mousePos.y});
    }, false);
});

</script>

<div class="track minimap" style="position: absolute; top: 0px; left: 0px; z-index: 900; height: {trackHeight}px; width: 100%;">
    <div class="label">Compressed view</div>
    <div style="max-height: 399px; overflow-y: scroll; flex-grow: 1; margin-top: 1px;">
        <canvas bind:this={canvas} width={widthAllVariants} height={canvasHeight} ></canvas>
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