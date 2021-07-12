<script>
    export let disabled;

    import { getContext } from 'svelte';
    import VcfExportModalContent from '/components/modals/VcfExportModalContent.svelte';

    const { open } = getContext('simple-modal');

    const showModal = () => {
        open(VcfExportModalContent);
    };
</script> 
 
<button on:click|preventDefault={showModal} disabled={disabled} type="button" class="divbrowse-btn divbrowse-btn-light">VCF Export</button>