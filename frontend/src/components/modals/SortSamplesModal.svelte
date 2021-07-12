<script>
    export let disabled;

    import { getContext } from 'svelte';
    import SortSamplesModalContent from '/components/modals/SortSamplesModalContent.svelte';
 
    const { open, close } = getContext('simple-modal');
 
    const showModal = () => {
        open(SortSamplesModalContent, {close: close}, {styleWindow: { width: '45em' }});
    };
</script> 
 
<button on:click|preventDefault={showModal} disabled={disabled} type="button" class="divbrowse-btn divbrowse-btn-light">Sort Samples</button>