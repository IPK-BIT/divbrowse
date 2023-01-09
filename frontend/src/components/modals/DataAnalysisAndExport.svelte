<script>
import { getContext } from 'svelte';
const context = getContext('app');
let { controller, eventbus } = context.app();

import getStores from '@/utils/store';
const { variantFilterSettings } = getStores();

import SelectVariantsComponent from '@/components/modals/SelectVariantsComponent.svelte';

let vcfExportHiddenForm;
let apiUrlVcfExport = controller.config.apiBaseUrl+'/vcf_export';

let gffExportHiddenForm;
let apiUrlGffExport = controller.config.apiBaseUrl+'/gff3_export';


let startpos, endpos, useVariantFilter;

let instanceSelectVariantComponent;





function openDataAnalysisModal(startpos, endpos, useVariantFilter, callbackSuccess) {

    let params = {startpos, endpos};

    if (useVariantFilter) {
        params['variantFilterSettings'] = $variantFilterSettings;
    }

    eventbus.emit('modal:open', {
        component: 'DataAnalysis',
        props: {params}
    });
}



function callbackExportVcf(startpos, endpos, _useVariantFilter, callbackSuccess) {

    useVariantFilter = _useVariantFilter;

    let params = {startpos, endpos};

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
    setTimeout(() => gffExportHiddenForm.submit(), 500);
}



let settingsSelectSnpsDialogue = {
    modeSelectLabel: 'Setup genomic region:',
    ctaBtnLabel: 'Perform calculation now'
}

</script> 
 

<div style="min-width: 700px;">
    <div class="divbrowse-modal-dialogue-headline">Data Analysis and Export</div>

    <SelectVariantsComponent 
        bind:this={instanceSelectVariantComponent} 
        onCallToAction={openDataAnalysisModal} 
        callbackExportVcf={callbackExportVcf} 
        callbackExportGff={callbackExportGff} 
        settings={settingsSelectSnpsDialogue} 
    />

    <form bind:this={vcfExportHiddenForm} action="{apiUrlVcfExport}" method="post">
        <input type="hidden" name="chrom" value="{controller.chromosome}" />
        <input type="hidden" name="startpos" value="{startpos}" />
        <input type="hidden" name="endpos" value="{endpos}" />
        <input type="hidden" name="samples" value="{JSON.stringify(controller.config.samples)}" />
        {#if useVariantFilter}
        <input type="hidden" name="variant_filter_settings" value="{JSON.stringify($variantFilterSettings)}" />
        {/if}
    </form>


    <form bind:this={gffExportHiddenForm} action="{apiUrlGffExport}" method="post">
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