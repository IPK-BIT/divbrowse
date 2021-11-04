<script>
import { getContext } from 'svelte';

const context = getContext('app');
let { controller } = context.app();

import getStores from '/utils/store';
const { settings } = getStores();

function sampleDisplayName(sampleId) {
    if (controller.config.sampleDisplayNameTransformer !== undefined && typeof controller.config.sampleDisplayNameTransformer === "function") {
        sampleId = controller.config.sampleDisplayNameTransformer(sampleId);
    }
    return sampleId;
}

</script>

<div>
    <div class="divbrowse-modal-dialogue-headline">Settings</div>

    <div style="">
        <label class="form-label" for="snp-coloring-selector" style="display: inline-block; width: 200px;">SNP coloring</label>
        <select id="snp-coloring-selector" bind:value={$settings.variantDisplayMode} class="divbrowse-form-control">
            <option value="reference_mismatch">Reference mismatch</option>
            <option value="nucleotides">Nucleotides</option>
        </select>
    </div>

    <div style="margin-top:20px; position: relative;">
        <label class="form-label" for="colorblind-mode" style="display: inline-block; width: 200px; vertical-align: middle;">Colour vision deficiency mode</label>
        <input style="vertical-align: middle; margin-left: 0;" id="colorblind-mode" type=checkbox bind:checked={$settings.statusColorblindMode}>
    </div>

</div>

<style>

table { 
    border-spacing: 0px;
    border-collapse: collapse;
}

table tr td {
    vertical-align: top;
    border: 1px solid black;
    border-collapse: collapse;
    padding: 5px;
    margin: 0px;
}

</style>