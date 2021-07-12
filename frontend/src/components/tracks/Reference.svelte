<script>
export let data;

import getStores from '/utils/store';
const { variantWidth } = getStores();

function isFiltered(pos) {
    if (data.filtered_variants_coordinates.includes( pos ) === false) {
        return 'background-color: rgb(240,240,240);';
    } else {
        return '';
    }
}

</script>

<div class="track reference"><div class="label">Reference genome</div>
    {#each data.reference as nucleotide, i}
    <span class="snp reference ref-{nucleotide}" data-position="{data.variants_coordinates[i]}" style="width: {$variantWidth}px; {isFiltered(data.variants_coordinates[i])}"></span>
    {/each}
</div>


<style lang="less">

</style>