<script context="module">
    import { writable } from "svelte/store";

    let allModals = writable([]);

    export function newModal(component) {
        allModals.update($ => {
            $ = [...$, component];
            return $;
        });
    }

    function closeModal(index) {
        allModals.update($ => {
            let closedModal;
            if (index === -1) { // close highest modal
                closedModal = $.pop();
            } else {
                closedModal = $.splice(index, 1)[0];
            }

            if (closedModal.onClose && typeof closedModal.onClose === 'function') {
                closedModal.onClose();
            }
            $ = [...$];
            return $;
        });
    }

    function closeHighestModal() {
        closeModal(-1);
    }
</script>

<script>
import { onMount, onDestroy, getContext } from 'svelte'

const rootElem = getContext('rootElem');
    
let topDiv;
let visible = false;

let prevOnTop
let closeCallback
let modalContentComponent;

/*export let id=''

function keyPress(ev){
    //only respond if the current modal is the top one
    if(ev.key=="Escape" && onTop==topDiv) close() //ESC
}
*/

/**  API **/
/*
function open(component, callback){
    modalContentComponent = component;
    closeCallback=callback
    if(visible) return
    prevOnTop=onTop
    onTop=topDiv
    window.addEventListener("keydown",keyPress)
    
    //this prevents scrolling of the main window on larger screens
    document.body.style.overflow="hidden" 

    visible=true
    //Move the modal in the DOM to be the last child of <BODY> so that it can be on top of everything
    //document.body.appendChild(topDiv)
    rootElem.appendChild(topDiv);
}
    
function close(retVal){
    if(!visible) return
    window.removeEventListener("keydown",keyPress)
    onTop=prevOnTop
    if(onTop==null) document.body.style.overflow=""
    visible=false
    if(closeCallback) closeCallback(retVal)
}
*/
    
//expose the API
//modals[id] = { open, close }
    
/*onDestroy(()=>{
    delete modals[id]
    window.removeEventListener("keydown",keyPress)
});*/

allModals.subscribe($ => {
    if ($.length > 0) {
        //rootElem.appendChild(topDiv);
        //document.body.appendChild(topDiv);
        visible = true;
    } else {
        visible = false;
    }
});

/*onMount(async () => {
    let _type = typeof topDiv;
    console.log(_type);
    console.log(topDiv);
});*/

</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div id="divbrowse-modal-background" class:divbrowse-modal-visible={visible} bind:this={topDiv} on:click|stopPropagation={() => closeHighestModal()}> <!-- on:click={()=>close()} -->

    {#each $allModals as modal, index}
    <div class="divbrowse-modal-wrapper">
        <div class="divbrowse-modal" on:click|stopPropagation={()=>{}}>
            <svg class="divbrowse-modal-close" on:click|stopPropagation={() => closeModal(index)} viewBox="0 0 14 14">
                <circle cx=7 cy=7 r=6 />
                <line x1=4 y1=4 x2=10 y2=10 />
                <line x1=10 y1=4 x2=4 y2=10 />
            </svg>
            <div class="divbrowse-modal-content">
                <svelte:component this={modal.component} {...modal.props} close={() => { closeModal(index) } } />
            </div>
        </div>
    </div>
    {/each}

</div>


<svelte:head>
<style>
    #divbrowse-modal-background {
        visibility: hidden;
        z-index: 9999;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.6);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .divbrowse-modal-wrapper {
        /*z-index: 9999;*/
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .divbrowse-modal {
        position: relative;
        border-radius: 6px;
        background: white;
        border: 1px solid #000;
        filter: drop-shadow(5px 5px 5px #555);
        padding: 1em;
    }

    .divbrowse-modal-visible {
        visibility: visible !important;
    }

    .divbrowse-modal-close {
        position: absolute;
        top:10px;
        right:10px;
        width:24px;
        height:24px;
        cursor: pointer;
        fill: rgb(255,255,255);
    }

    .divbrowse-modal-close circle {
        stroke: rgb(50,50,50);
        stroke-width:0.5;
    }

    .divbrowse-modal-close:hover {
        fill: rgb(220,220,220);
    }

    .divbrowse-modal-close line {
        stroke: rgb(50,50,50);
        stroke-width:1;
    }

    .divbrowse-modal-content {
        max-width: calc(100vw - 20px);
        max-height: calc(100vh - 20px);
        overflow: auto;
    }
</style>
</svelte:head>

<style>
    #divbrowse-modal-background {
        visibility: hidden;
        z-index: 9999;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.6);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .divbrowse-modal-wrapper {
        /*z-index: 9999;*/
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .divbrowse-modal {
        position: relative;
        border-radius: 6px;
        background: white;
        border: 1px solid #000;
        filter: drop-shadow(5px 5px 5px #555);
        padding: 1em;
    }

    .divbrowse-modal-visible {
        visibility: visible !important;
    }

    .divbrowse-modal-close {
        position: absolute;
        top:10px;
        right:10px;
        width:24px;
        height:24px;
        cursor: pointer;
        fill: rgb(255,255,255);
    }

    .divbrowse-modal-close circle {
        stroke: rgb(50,50,50);
        stroke-width:0.5;
    }

    .divbrowse-modal-close:hover {
        fill: rgb(220,220,220);
    }

    .divbrowse-modal-close line {
        stroke: rgb(50,50,50);
        stroke-width:1;
    }

    .divbrowse-modal-content {
        max-width: calc(100vw - 100px);
        max-height: calc(100vh - 100px);
        /*overflow-y: scroll;*/
    }
</style>