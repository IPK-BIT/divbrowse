<script>
export let data;

import { afterUpdate } from 'svelte'
import getStores from '/utils/store';
const { variantWidth, snpPosHighlights } = getStores();

let el;

afterUpdate(async () => {
    // layout update hack for the vertical rotated SNP position number labels
    el = document.getElementById('track-positions');
    el.style.display='none';
    el.offsetHeight;
    el.style.display='inline-flex';
});

function checkHighlight(position) {
    if ($snpPosHighlights.startpos !== undefined) {
        if (position >= $snpPosHighlights.startpos && position <= $snpPosHighlights.endpos) {
            return true
        }
    }
    return false;
}

</script>


<div class="track positions" id="track-positions"><div class="label">Variant positions</div>
    {#each data.variants_coordinates as position}
    <span class="positions" data-position="{position}" style="width: {$variantWidth}px;" class:highlighted="{checkHighlight(position)}">{position}</span>
    {/each}
</div>


<style lang="less">
span.positions.highlighted {
    background: rgb(230,230,230);
}
</style>