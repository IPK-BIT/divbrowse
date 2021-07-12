<script>
    export let disabled;

    import { getContext } from 'svelte';
    import BlastModalContent from '/components/modals/SnpEffAnnotationModalContent.svelte';
 
    const { open, close } = getContext('simple-modal');
 
    const showModal = () => {
        open(BlastModalContent, {close: close}, {styleWindow: { width: '80em' }});
    };
</script> 
 
<button on:click|preventDefault={showModal} disabled={disabled} type="button" class="divbrowse-btn divbrowse-btn-light">BLAST</button>