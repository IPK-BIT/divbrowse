<script>
import { getContext } from 'svelte';
const context = getContext('app');
let { controller, eventbus } = context.app();

import getStores from '/utils/store';
const { variantFilterSettings, filteredVariantsCoordinates } = getStores();

import SelectVariantsComponent from '/components/modals/SelectVariantsComponent.svelte';

import DataAnalysisModalContent from '/components/modals/DataAnalysisModalContent.svelte';
const { open } = getContext('2nd-modal');

let vcfExportHiddenForm;
let apiUrlVcfExport = controller.config.apiBaseUrl+'/vcf_export';

let gffExportHiddenForm;
let apiUrlGffExport = controller.config.apiBaseUrl+'/gff3_export';

let showPcaResultPlot = 'none';
let selectedAccessions = [];
let startpos, endpos, useVariantFilter;

let instanceSelectVariantComponent;





function openDataAnalysisModal(startpos, endpos, useVariantFilter, callbackSuccess) {

    let params = {
        startpos: startpos,
        endpos: endpos,
    }
    if (useVariantFilter) {
        params['variantFilterSettings'] = $variantFilterSettings;
    }

    open(DataAnalysisModalContent, {params: params}, {styleWindow: { width: '100%', height: '92vh' }}, {onClosed: () => { console.log('CLOSED') }});
}



function callbackExportVcf(_startpos, _endpos, _useVariantFilter, callbackSuccess) {
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

    instanceSelectVariantComponent.loadingAnimation.show();
    controller.vcf_export_check(params, result => {
        //callbackSuccess();
        instanceSelectVariantComponent.loadingAnimation.hide();
        if (result.success === true && result.status === 'export_possible') {
            vcfExportHiddenForm.submit();
        } else if (result.success === false && result.status === 'error_snp_window_too_big') {
            instanceSelectVariantComponent.setErrorMsg(result.message);
        }
    });
}


function callbackExportGff(_startpos, _endpos, _useVariantFilter, callbackSuccess) {

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
    modeSelectLabel: 'Setup genomic region:',
    ctaBtnLabel: 'Perform calculation now'
}

</script> 
 

<div>
    <div class="divbrowse-modal-dialogue-headline">Data Analysis and Export</div>

    <SelectVariantsComponent 
        bind:this={instanceSelectVariantComponent} 
        onCallToAction={openDataAnalysisModal} 
        callbackExportVcf={callbackExportVcf} 
        callbackExportGff={callbackExportGff} 
        settings={settingsSelectSnpsDialogue} 
    />

    {#if selectedAccessions.length > 0}
    <div>You have selected {selectedAccessions.length} samples.</div>
    {/if}

    <div id="plotDivModal" style="display: {showPcaResultPlot}; width: 520px; height: 520px; margin-top:20px; padding: 5px; border: 1px solid black;"></div>


    <form bind:this={vcfExportHiddenForm} ref="form-vcfexport-download" action="{apiUrlVcfExport}" method="post">
        <input type="hidden" name="chrom" value="{controller.chromosome}" />
        <input type="hidden" name="startpos" value="{startpos}" />
        <input type="hidden" name="endpos" value="{endpos}" />
        <input type="hidden" name="samples" value="{JSON.stringify(controller.config.samples)}" />
        {#if useVariantFilter}
        <input type="hidden" name="variant_filter_settings" value="{JSON.stringify($variantFilterSettings)}" />
        {/if}
    </form>


    <form bind:this={gffExportHiddenForm} ref="form-gffexport-download" action="{apiUrlGffExport}" method="post">
        <input type="hidden" name="chrom" value="{controller.chromosome}" />
        <input type="hidden" name="startpos" value="{startpos}" />
        <input type="hidden" name="endpos" value="{endpos}" />
    </form>


</div>

<style lang="less">

a.dim-red-select-range {
    color: rgb(150,150,150);

    div {
        display: inline-block;
        width: 200px;
        border: 1px solid rgb(200,200,200);
        border-radius: 8px;
        width: 200px;
        padding: 10px;
    }

    &.active {
        color: black;

        div {
            background: rgb(230,230,230);
        }
    }

    &:hover {
        color: black;

        div {
            /*border: 1px solid rgb(235,235,235);*/
            background: rgb(230,230,230);
        }
    }
}

</style>