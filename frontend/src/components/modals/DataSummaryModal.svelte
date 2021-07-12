<script>
  import { getContext } from 'svelte';
  import DataSummaryModalContent from '/components/modals/DataSummaryModalContent.svelte';
 
  const { open } = getContext('simple-modal');
 
  const showModal = () => {
    open(DataSummaryModalContent);
  };
</script> 
 
<button on:click|preventDefault={showModal} type="button" class="divbrowse-btn divbrowse-btn-light">Data Summary</button>