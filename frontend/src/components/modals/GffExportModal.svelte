<script>
    export let disabled;

    import { getContext } from 'svelte';
    import GffExportModalContent from '/components/modals/GffExportModalContent.svelte';

    const { open } = getContext('simple-modal');

    const showModal = () => {
        open(GffExportModalContent);
    };
</script> 
 
<button on:click|preventDefault={showModal} disabled={disabled} type="button" class="divbrowse-btn divbrowse-btn-light">GFF3 Export</button>