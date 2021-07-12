<script>
    export let disabled;

    import { getContext } from 'svelte';
    import PcaModalContent from '/components/modals/PcaModalContent.svelte';
 
    const { open } = getContext('simple-modal');
 
    const showModal = () => {
        open(PcaModalContent);
    };
</script> 
 
<button on:click|preventDefault={showModal} disabled={disabled} type="button" class="divbrowse-btn divbrowse-btn-light">PCA</button>