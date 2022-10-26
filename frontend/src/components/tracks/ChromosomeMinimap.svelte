<script>
export let data;

import { getContext } from 'svelte';

const context = getContext('app');
let { controller } = context.app();


let posIndicatorLeft = 0;
let posIndicatorTrapezLeft = 5;
let posIndicatorTrapezRight = 1695;


let metadata = controller.getMetadata();

let widthAllVariants = controller.getCurrentWidthOfVariants();

let currChromStart = metadata.chromosomesById[ controller.chromosome ].start;
let currChromEnd = metadata.chromosomesById[ controller.chromosome ].end;

let currChromCentromerePos = metadata.chromosomesById[ controller.chromosome ].centromere_position;
let centromerePosFrac = currChromCentromerePos / currChromEnd;
let widthLeftFragment = Math.floor(200 * centromerePosFrac);
let widthRightFragment = 400 - widthLeftFragment;


$: {
    widthAllVariants = controller.getCurrentWidthOfVariants();

    currChromStart = metadata.chromosomesById[ controller.chromosome ].start;
    currChromEnd = metadata.chromosomesById[ controller.chromosome ].end;

    currChromCentromerePos = metadata.chromosomesById[ controller.chromosome ].centromere_position;
    centromerePosFrac = currChromCentromerePos / currChromEnd;
    widthLeftFragment = Math.floor(400 * centromerePosFrac);
    widthRightFragment = 400 - widthLeftFragment;

    let positionRelative = data.coordinate_first / currChromEnd;
    posIndicatorLeft = Math.floor(positionRelative * 390) + 5;

    posIndicatorTrapezLeft = posIndicatorLeft + 2;
    posIndicatorTrapezRight = widthAllVariants - posIndicatorTrapezLeft;
}

let svg;
let height = 30;

function prettyPos(pos) {
    return parseInt(pos).toLocaleString();
}

function onClickMinimap(event) {
    let rect = event.currentTarget.getBoundingClientRect();
    let clickX = event.clientX - rect.left;
    if (clickX >= 0 && clickX <= 400) {
        let in_min = 0;
        let in_max = 400;
        let out_min = currChromStart;
        let out_max = currChromEnd;
        let desiredPosition = Math.floor((clickX - in_min) * (out_max - out_min) / (in_max - in_min) + out_min);
        controller.goToPosition(desiredPosition);
    }
}

</script>

<div class="track chromosome-minimap" style="width:100%;">

    <div class="label">Position on chromosome</div>

    <div style="width: {widthAllVariants}px;">
    
        <div style="position: relative; height: 18px;" on:click={onClickMinimap}>

            {#if currChromCentromerePos > 0}
            <div class="chromosome-fragment" style="width: {widthLeftFragment}px; left: 0px:"></div>
            <div class="chromosome-fragment" style="width: {widthRightFragment}px; left: {widthLeftFragment+2}px;"></div>
            {:else}
            <div class="chromosome-fragment" style="width: 400px; left: 0px:"></div>
            {/if}

            <div id="pos-indicator" style="left: {posIndicatorLeft}px;"></div>

            <div id="pos-coordinates" style="position: absolute; left: 420px;font-size:13px;width: 300px;">  {prettyPos(data.coordinate_first)}  - {prettyPos(data.coordinate_last)} of {prettyPos(currChromEnd)}</div>

        </div>

        <!--
        <div id="svg-container" style=" width: {widthAllVariants}px;">
            <svg width="{widthAllVariants}" height="30" bind:this={svg}>
                <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style="stop-color:rgb(234,234,234);stop-opacity:1" />
                        <stop offset="100%" style="stop-color:rgb(250,250,250);stop-opacity:1" />
                    </linearGradient>
                </defs>
                
                <line class="trapez" x1="{posIndicatorTrapezLeft-1}" y1="0" x2="0" y2="{height}" />
                <line class="trapez" x1="{posIndicatorTrapezLeft}" y1="0" x2="{widthAllVariants+80}" y2="{height}" />
                
            </svg>
        </div>
        -->

        <!--<div id="trapez" style="border-left: {posIndicatorTrapezLeft}px solid transparent; border-right: {posIndicatorTrapezRight}px solid transparent;"></div>-->

    </div>

</div>

<style>

div.track.chromosome-minimap {

    height: 30px;
}

.chromosome-fragment {
    width: 400px;
    height: 14px;
    background: rgb(240,240,240);
    border: 1px solid rgb(150,150,150);
    border-radius: 7px;
    position: absolute;
    top: 0px;
    cursor: pointer;
}

#pos-indicator {
    position: absolute;
    top: 0px;
    height: 16px;
    width: 3px;
    background: black;
}

#svg-container {
    height: 30px;
    display: block;
}
.trapez {
    stroke:rgb(100,100,100);
    stroke-width: 1.0;
}

#trapez {
    display: block;
    border-bottom: 20px solid rgb(220,220,220);
    height: 0;
    /*width: 1500px;*/
    max-width: 1700px;
    box-sizing: border-box;
}

</style>