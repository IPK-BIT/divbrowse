import { setContext, getContext } from "svelte";
import { writable } from "svelte/store";

let appId;

const key = "__stores";


function createGenesBookmarksStore() {

    const localStorageKey = appId+'-genes-bookmarks';

    const store = writable(new Set());

    const bookmarkedGenes = localStorage.getItem(localStorageKey);
    if (bookmarkedGenes !== null) {
        const bookmarkedGenesSet = new Set(JSON.parse(bookmarkedGenes));
        store.set(bookmarkedGenesSet);
    }

    const bookmarkGene = (id) => {
        store.update($ => {
            $.add(id);
            localStorage.setItem(localStorageKey, JSON.stringify(Array.from($)));
            return $;
        });
    }

    const unbookmarkGene = (id) => {
        store.update($ => {
            $.delete(id);
            localStorage.setItem(localStorageKey, JSON.stringify(Array.from($)));
            return $;
        });
    }

    return {
        ...store,
        bookmarkGene,
        unbookmarkGene
    }
}


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
        geneSearch: writable({
            query: '',
            searchInInterval: false,
            selectedChromosome: undefined,
            startpos: null,
            endpos: null
        }),
        genesBookmarks: createGenesBookmarksStore(),
    }

    setContext(key, stores);

    return stores;
}

export default function getStores() {
    
    appId = getContext('app').app().appId;

    const stores = getContext(key);

    if (!stores) {
        return createStores();
    }

    return stores;
}