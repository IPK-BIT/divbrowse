<script>
import { getContext } from 'svelte';

const context = getContext('app');
let { controller } = context.app();

import SelectSnpsDialogue from '/components/modals/SelectSnpsDialogue.svelte';

let gffExportHiddenForm;
let apiUrlGffExport = controller.config.apiBaseUrl+'/gff3_export';
let startpos, endpos, snpcount;

function onCallToAction(_startpos, _endpos, _useVariantFilter, callbackSuccess) {

    startpos = _startpos;
    endpos = _endpos;

    /*let params = {
        startpos: startpos,
        endpos: endpos,
    }*/

    //controller.gff_export_check(params, result => {
        //callbackSuccess();
        //if (result.success === true && result.status === 'export_possible') {
            //gffExportHiddenForm.submit();
            setTimeout(() => gffExportHiddenForm.submit(), 500);
        //}
    //});
}

let settingsSelectSnpsDialogue = {
    modeSelectLabel: 'Export GFF3 file for:',
    ctaBtnLabel: 'Start export now',
    allowSnpFiltering: false,
    showSnpCount: false,
}

</script> 
 

<div>
    <div class="divbrowse-modal-dialogue-headline">GFF3 Export</div>

    <SelectSnpsDialogue onCallToAction={onCallToAction} settings={settingsSelectSnpsDialogue} />

    <form bind:this={gffExportHiddenForm} ref="form-gffexport-download" action="{apiUrlGffExport}" method="post">
        <input type="hidden" name="chrom" value="{controller.chromosome}" />
        <input type="hidden" name="startpos" value="{startpos}" />
        <input type="hidden" name="endpos" value="{endpos}" />
    </form>

</div>

<style>

</style>