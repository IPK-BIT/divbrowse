import { setContext, getContext } from "svelte";
import { writable } from "svelte/store";

const key = "__stores";

function createStores() {

    const stores = {
        settings: writable({
            statusShowMinimap: false,
            zoomX: false,
            zoomY: false,
            statusColorblindMode: false,
            variantDisplayMode: 'reference_mismatch'
        }),
        variantWidth: writable(20),
        groups: writable({}),
        snpPosHighlights: writable({}),
        sortSettings: writable({
            sortmode: 'none',
            sortorder: undefined
        }),
        variantFilterSettings: writable({
            maf: [0.05,0.5],
            missingFreq: [0,0.1],
            heteroFreq: [0,0.1],
            vcfQual: [500,1000]
        }),
        filteredVariantsCoordinates: writable([]),
    }

    setContext(key, stores);

    return stores;
}

export default function getStores() {
    const stores = getContext(key);

    if (!stores) {
        return createStores();
    }

    return stores;
}