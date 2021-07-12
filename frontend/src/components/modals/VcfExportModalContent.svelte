<script>
import { getContext } from 'svelte';

const context = getContext('app');
let { controller } = context.app();

import getStores from '/utils/store';
const { variantFilterSettings } = getStores();

import SelectSnpsDialogue from '/components/modals/SelectSnpsDialogue.svelte';

let vcfExportHiddenForm;
let apiUrlVcfExport = controller.config.apiBaseUrl+'/vcf_export';
let startpos, endpos, snpcount;

let useVariantFilter = false;

function onCallToAction(_startpos, _endpos, _useVariantFilter, callbackSuccess) {

    startpos = _startpos;
    endpos = _endpos;
    useVariantFilter = _useVariantFilter;

    let params = {
        startpos: startpos,
        endpos: endpos,
    }
    if (_useVariantFilter) {
        params['variantFilterSettings'] = $variantFilterSettings;
    }

    controller.vcf_export_check(params, result => {
        callbackSuccess();
        if (result.success === true && result.status === 'export_possible') {
            vcfExportHiddenForm.submit();
        }
    });
}

let settingsSelectSnpsDialogue = {
    modeSelectLabel: 'Export VCF file for:',
    ctaBtnLabel: 'Start export now'
}

</script> 
 

<div>
    <div class="divbrowse-modal-dialogue-headline">VCF Export</div>

    <SelectSnpsDialogue onCallToAction={onCallToAction} settings={settingsSelectSnpsDialogue} />

    <form bind:this={vcfExportHiddenForm} ref="form-vcfexport-download" action="{apiUrlVcfExport}" method="post">
        <input type="hidden" name="chrom" value="{controller.chromosome}" />
        <input type="hidden" name="startpos" value="{startpos}" />
        <input type="hidden" name="endpos" value="{endpos}" />
        <input type="hidden" name="samples" value="{JSON.stringify(controller.config.samples)}" />
        {#if useVariantFilter}
        <input type="hidden" name="variant_filter_settings" value="{JSON.stringify($variantFilterSettings)}" />
        {/if}
    </form>


</div>

<style>

</style>