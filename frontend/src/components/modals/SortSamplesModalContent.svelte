<script>
export let close;

import getStores from '/utils/store';
const { sortSettings } = getStores();

let sortmode = $sortSettings.sortmode;
let sortorder = $sortSettings.sortorder;

function setSortSettings(_sortmode, _sortorder) {
    if (_sortmode === 'none') {
        sortorder = undefined;
    }

    if (_sortmode !== 'none' && _sortorder === undefined) {
        sortorder = 'ASC';
    }

    let settings = {
        sortmode: sortmode,
        sortorder: sortorder
    }
    sortSettings.set(settings);
}

$: setSortSettings(sortmode, sortorder);

</script> 
 

<div style="min-height: 400px;">
    <div class="divbrowse-modal-dialogue-headline">Sort Samples</div>

    <div class="sortmode" style="margin-top: 30px;">
        <div class="headline">Sort mode</div>
        <div class="sortmode-option">
            <input type="radio" style="vertical-align: -1px;" bind:group={sortmode} value="{'none'}">
            <label>No sorting</label>
        </div>
        <div class="sortmode-option">
            <input type="radio" style="vertical-align: -1px;" bind:group={sortmode} value="{'alphabetical'}">
            <label>Sort sample list alphabetical</label>
        </div>
        <div class="sortmode-option">
            <input type="radio" style="vertical-align: -1px;" bind:group={sortmode} value="{'genetic_distance'}">
            <label>Sort sample list by genetic distance to the reference genome</label>
        </div>
    </div>

    {#if $sortSettings.sortmode !== 'none'}
    <div class="sortmode">
        <div class="headline">Sort order</div>
        <div class="sortmode-option">
            <input type="radio" style="vertical-align: -1px;" bind:group={sortorder} value="{'ASC'}">
            <label>Sort ascending</label>
        </div>
        <div class="sortmode-option">
            <input type="radio" style="vertical-align: -1px;" bind:group={sortorder} value="{'DESC'}">
            <label>Sort descending</label>
        </div>
    </div>
    {/if}

    <div style="clear:left"></div>

</div>

<style>
.sortmode {
    border: 1px solid rgb(180,180,180);
    padding: 15px;
    margin-bottom: 20px;
    background-color: rgb(248,248,248);
    border-radius: 4px;
}

.sortmode .headline {
    font-weight: 500;
    margin-bottom: 15px;
}

.sortmode-option {
    margin-bottom: 10px;
}
</style>