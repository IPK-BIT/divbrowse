<script>
import { getContext } from 'svelte';

const context = getContext('app');
let { controller } = context.app();

import getStores from '@/utils/store';
const { settings } = getStores();

function sampleDisplayName(sampleId) {
    if (controller.config.sampleDisplayNameTransformer !== undefined && typeof controller.config.sampleDisplayNameTransformer === "function") {
        sampleId = controller.config.sampleDisplayNameTransformer(sampleId);
    }
    return sampleId;
}

</script>

<div style="min-width: 700px;">
    <div class="divbrowse-modal-dialogue-headline">Settings</div>

    <div class="option">
        <label class="form-label" for="snp-coloring-selector" style="display: inline-block; width: 300px;">SNP coloring</label>
        <select id="snp-coloring-selector" bind:value={$settings.variantDisplayMode} class="divbrowse-form-control">
            <option value="reference_mismatch">Reference mismatch</option>
            <option value="nucleotides">Nucleotides</option>
        </select>
    </div>

    <div class="option" style="">
        <label class="form-label" for="colorblind-mode" style="display: inline-block; width: 300px; vertical-align: middle;">Colour vision deficiency mode</label>
        <input style="vertical-align: middle; margin-left: 0;" id="colorblind-mode" type=checkbox bind:checked={$settings.statusColorblindMode}>
    </div>

</div>

<style>

.option {
    position: relative;
    padding: 20px 0;
    border-bottom: 1px dotted rgb(170,170,170);
}

</style>