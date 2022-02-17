<script>
    export let disabled;

    import { getContext } from 'svelte';
    import GeneSearchModalContent from '/components/modals/GeneSearchModalContent.svelte';
 
    const { open, close } = getContext('simple-modal');
 
    const showModal = () => {
        open(GeneSearchModalContent, {close: close}, {styleWindow: { width: '80em' }});
    };
</script> 
 
<button on:click|preventDefault={showModal} disabled={disabled} type="button" class="divbrowse-btn divbrowse-btn-light">Genes</button>