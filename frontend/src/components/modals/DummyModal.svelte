<script>
export let close;
export let test = 'no prop set';

import { getContext } from 'svelte';
const context = getContext('app');
let { appId, eventbus, controller } = context.app();
</script>

<div>
    <p><strong>Dummy Modal Content</strong></p>

    <button on:click|preventDefault={() => eventbus.emit('modal:open', 'GeneSearchModalContent')}>Open another modal</button>
    <hr />
    <button on:click|preventDefault={() => close()}>Close this modal</button>

    <hr />
    {test}
</div>

<style>
    div {
        border: 2px dotted blue;
        padding: 30px;
    }
</style>