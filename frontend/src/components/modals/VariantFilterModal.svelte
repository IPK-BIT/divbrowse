<script>
    export let disabled;

    import { getContext } from 'svelte';
    import VariantFilterModalContent from '/components/modals/VariantFilterModalContent.svelte';

    const { open } = getContext('simple-modal');
 
    const showModal = () => {
        open(VariantFilterModalContent, {}, {styleWindow: { width: '45em' }});
    };
</script> 
 
<button on:click|preventDefault={showModal} disabled={disabled} type="button" class="divbrowse-btn divbrowse-btn-light">Filter Variants</button>