<script>
    export let disabled;

    import { getContext } from 'svelte';
    import VariantFilterModalContent from '/components/modals/VariantFilterModalContent.svelte';

    const { open, close } = getContext('simple-modal');
 
    const showModal = () => {
        open(VariantFilterModalContent, {close: close}, {styleWindow: { width: '45em' }});
    };
</script> 
 
<button on:click|preventDefault={showModal} disabled={disabled} type="button" class="divbrowse-btn divbrowse-btn-light">Filter SNPs</button>