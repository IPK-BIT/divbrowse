<script>
export let data;
export let variants;

console.log(variants);

import { onMount, getContext } from 'svelte';

const context = getContext('app');
let { eventbus, controller } = context.app();

import { numberOfAltAllelesFactory } from '/utils/helpers';

let canvas;
let widthAllVariants;
let framesPerSecond = 10;
let timeoutHandle;
let frame;
let canvasHeight = variants.length;


const ploidy = controller.metadata.ploidy;

const numberOfAlternateAlleles = numberOfAltAllelesFactory.getFunction(ploidy);


function drawVariants(variants) {

    if (canvas === undefined) {
        console.log('drawVariants() EARLY EXIT no canvas available');
        return false;
    }

    let ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, widthAllVariants, canvasHeight);

    clearTimeout(timeoutHandle);
    cancelAnimationFrame(frame);

    let frameCounter = 0;

    (function loop() {
    	
            frame = requestAnimationFrame(loop);

            let row = 0;
            for (let sample of variants) {
                let sampleId = sample[0];
                let col = 0;
                let xPos = 0;

                for (let col = 0; col < data.filtered_variants_coordinates.length; col++) {
                    xPos = col * 20;
                    //col += 1;

                    //let call = data.variants_gt[sampleId][col]

                    let numAltAlleles = numberOfAlternateAlleles(data.variants_gt[sampleId][col])

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

                    ctx.fillRect(xPos, row, 20, 1);
                }
                row += 1;
            }
            //ctx.fillStyle = "rgb(0, 0, 0)";
            //ctx.fillRect(20, 20, 100, 50);

            frameCounter += 1;
            if (frameCounter > 60) {
                cancelAnimationFrame(frame);
            }

    }());

}


let _data, _variants;
$: {
    _data = data;
    _variants = variants;
    if (canvasHeight > 400) {
        canvasHeight = 400;
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

<div class="track minimap" style="position: absolute; top: 0px; left: 0px; z-index: 900; height: {canvasHeight}px; width: 100%;">
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