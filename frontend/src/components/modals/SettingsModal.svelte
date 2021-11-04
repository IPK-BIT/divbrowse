<script>
  import { getContext } from 'svelte';
  import SettingsModalContent from '/components/modals/SettingsModalContent.svelte';
 
  const { open } = getContext('simple-modal');
 
  const showModal = () => {
    open(SettingsModalContent);
  };
</script> 
 
<button on:click|preventDefault={showModal} type="button" class="divbrowse-btn divbrowse-btn-light">Settings</button>