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

let currChromEnd = metadata.chromosomesById[ controller.chromosome ].end;

let currChromCentromerePos = metadata.chromosomesById[ controller.chromosome ].centromere_position;
let centromerePosFrac = currChromCentromerePos / currChromEnd;
let widthLeftFragment = Math.floor(200 * centromerePosFrac);
let widthRightFragment = 400 - widthLeftFragment;


$: {
    widthAllVariants = controller.getCurrentWidthOfVariants();
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

</script>

<div class="track chromosome-minimap" style="width:100%;">

    <div class="label">Position on chromosome</div>

    <div style="width: {widthAllVariants}px;">
    
        <div style="position: relative; height: 18px;">

            {#if currChromCentromerePos > 0}
            <div class="chromosome-fragment" style="width: {widthLeftFragment}px; left: 0px:"></div>
            <div class="chromosome-fragment" style="width: {widthRightFragment}px; left: {widthLeftFragment+2}px;"></div>
            {:else}
            <div class="chromosome-fragment" style="width: 400px; left: 0px:"></div>
            {/if}

            <div id="pos-indicator" style="left: {posIndicatorLeft}px;"></div>

            <div id="pos-coordinates" style="position: absolute; left: 420px;font-size:13px;width: 300px;">  {prettyPos(data.coordinate_first)}  - {prettyPos(data.coordinate_last)} of {prettyPos(currChromEnd)}</div>

        </div>

        <div id="svg-container" style=" width: {widthAllVariants}px;">
            <svg width="{widthAllVariants}" height="30" bind:this={svg}>
                <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style="stop-color:rgb(234,234,234);stop-opacity:1" />
                        <stop offset="100%" style="stop-color:rgb(250,250,250);stop-opacity:1" />
                    </linearGradient>
                </defs>
                <!--<polygon points="{posIndicatorTrapezLeft},0 0,30 {widthAllVariants-1},30" fill="url(#grad)" />-->
                <line x1="{posIndicatorTrapezLeft-1}" y1="0" x2="0" y2="{height}" style="stroke:rgb(30,30,30);stroke-width:1.0" />
                <line x1="{posIndicatorTrapezLeft}" y1="0" x2="{widthAllVariants+80}" y2="{height}" style="stroke:rgb(30,30,30);stroke-width:1.0" />
            </svg>
        </div>

        <!--<div id="trapez" style="border-left: {posIndicatorTrapezLeft}px solid transparent; border-right: {posIndicatorTrapezRight}px solid transparent;"></div>-->

    </div>

</div>

<style>

div.track.chromosome-minimap {
    margin-top: 8px;
    height: 46px;
}

.chromosome-fragment {
    width: 400px;
    height: 14px;
    background: rgb(240,240,240);
    border: 1px solid rgb(150,150,150);
    border-radius: 7px;
    position: absolute;
    top: 0px;
}

#pos-indicator {
    position: absolute;
    top: 0px;
    height: 18px;
    width: 3px;
    background: black;
}

#svg-container {
    height: 30px;
    display: block;
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