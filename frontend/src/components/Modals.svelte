<script>
import { getContext } from 'svelte';
const context = getContext('app');
let { appId, eventbus, controller } = context.app();

import Modal, { newModal } from '@/components/ModalMulti.svelte';

import Blast from '@/components/modals/Blast.svelte';
import DataAnalysisAndExport from '@/components/modals/DataAnalysisAndExport.svelte';
import DataAnalysis from '@/components/modals/DataAnalysis.svelte';
import DataSummary from '@/components/modals/DataSummary.svelte';
import GeneSearch from '@/components/modals/GeneSearch.svelte';
import GeneDetails from '@/components/modals/GeneDetails.svelte';
import DummyModal from '@/components/modals/DummyModal.svelte';
import VariantFilter from '@/components/modals/VariantFilter.svelte';
import SortSamples from '@/components/modals/SortSamples.svelte';
import Settings from '@/components/modals/Settings.svelte';
import SnpEffAnnotation from '@/components/modals/SnpEffAnnotation.svelte';


let modalMapping = {
    'Blast': Blast,
    'Dummy': DummyModal,
    'DataAnalysisAndExport': DataAnalysisAndExport,
    'DataAnalysis': DataAnalysis,
    'DataSummary': DataSummary,
    'GeneSearch': GeneSearch,
    'GeneDetails': GeneDetails,
    'SortSamples': SortSamples,
    'Settings': Settings,
    'SnpEffAnnotation': SnpEffAnnotation,
    'VariantFilter': VariantFilter,
}

eventbus.on('modal:open', payload => {

    payload.component = modalMapping[payload.component];
    
    if (!payload.props) {
        payload.props = {};
    }

    newModal(payload);
});

</script>


<Modal />


<style>
:global(.divbrowse-modal-dialogue-headline) {
    margin-bottom: 15px;
    font-weight: bold;
    font-size: 1.2rem;
}
</style>