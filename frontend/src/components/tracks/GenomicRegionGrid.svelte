<script>
export let data;

import { getContext } from 'svelte';
let { controller } = getContext('app').app();


let widthAllVariants;
let maxmin;
let gridPositionsY = [];

const takeElementsEvenlySpaced = (a, n) => {
    let p = Math.ceil(a.length / n);
    return a.slice(0, p * n).filter((_, i) => 0 == i % p);
}

$: {
    widthAllVariants = controller.getCurrentWidthOfVariants();
    maxmin = data.coordinate_last - data.coordinate_first;

    let regionLength = Math.ceil(Math.log10(maxmin + 1));

    let gridInterval = 10 ** (regionLength - 2);

    if (maxmin < 1000) {
        gridInterval = 100;
    }

    let regionGridMin = Math.ceil(data.coordinate_first / gridInterval ) * gridInterval;
    let regionGridMax = Math.floor(data.coordinate_last / gridInterval ) * gridInterval;

    gridPositionsY = [...Array((regionGridMax - regionGridMin) / gridInterval + 1)].map((_, i) => regionGridMin + gridInterval * i);

    if (gridPositionsY.length > 15) {
        gridPositionsY = takeElementsEvenlySpaced(gridPositionsY, 15);
    }
}


</script>


<g>
    {#each gridPositionsY as position}
    <text text-anchor="middle" x="{ ((position - data.coordinate_first) / maxmin) * (widthAllVariants-5) }" y="10" class="small">{position.toLocaleString('en-US')}</text>
    <line class="gridline" stroke-dasharray="1, 4" x1="{ ((position - data.coordinate_first) / maxmin) * (widthAllVariants-5) }" y1="12" x2="{ ((position - data.coordinate_first) / maxmin) * (widthAllVariants-5) }" y2="45" stroke-linecap="butt" />
    {/each}
</g>

<style>
    .gridline {
        stroke: rgb(100,100,100);
        stroke-width: 1;
    }
    .small {
      font-family: sans-serif;
      font-size: 10px;
    }
</style>