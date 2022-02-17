<script>
    export let disabled;

    import { getContext } from 'svelte';
    import DataAnalysisAndExportModalContent from '/components/modals/DataAnalysisAndExportModalContent.svelte';
 
    const { open } = getContext('simple-modal');
 
    const showModal = () => {
        open(DataAnalysisAndExportModalContent, {}, {styleWindow: { width: '50%' /*, height: '92vh'*/ }});
    };
</script> 
 
<button on:click|preventDefault={showModal} disabled={disabled} type="button" class="divbrowse-btn divbrowse-btn-light">Data Analysis / Export</button>