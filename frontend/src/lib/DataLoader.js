import axios from 'axios';
import cloneDeep from 'lodash/cloneDeep';

export default class DataLoader {

    constructor(config, eventbus) {
        this.config = config;
        this.eventbus = eventbus;

        this.payload = {};
        this.data = {};
        this.samplesVisibleInViewport = [];
    }

    generateVariantCallsMap() {
        this.callsMap = new Map(this.config.samples.map(item => [item, null]));
    }

    mergeLazyLoadedVariantCalls(calls) {
        let lazyLoadedCallsMap = new Map(Object.entries(calls));
        this.callsMap = new Map([...this.callsMap, ...lazyLoadedCallsMap]);
    }

    mergeLazyLoadedVariantCallsMetadata(calls_metadata) {
        for (let [metadata_key, metadata_values] of Object.entries(calls_metadata)) {
            if (this.callsMetadataMaps[metadata_key] === undefined) {
                // create new map for this metadata-key
                this.callsMetadataMaps[metadata_key] = new Map(this.config.samples.map(item => [item, null]));
            }

            // merge data
            let metadataMap = new Map(Object.entries(metadata_values));
            this.callsMetadataMaps[metadata_key] = new Map([...this.callsMetadataMaps[metadata_key], ...metadataMap]);
        }
    }

    checkIfSamplesAlreadyLazyLoaded(sampleIds) {
        let samplesToLazyLoad = [];
        for (let sampleId of sampleIds) {
            if (this.callsMap.get(sampleId) === null) {
                samplesToLazyLoad.push(sampleId);
            }
        }
        return samplesToLazyLoad;
    }

    lazyLoadChunkOfVariantCalls(number) {
        
    }

    lazyLoadVariantCalls(sampleIds, callbackEarlyExit) {

        this.samplesVisibleInViewport = sampleIds;

        sampleIds = this.checkIfSamplesAlreadyLazyLoaded(sampleIds);
        
        if (sampleIds.length == 0) {
            if (typeof callbackEarlyExit === "function") {
                callbackEarlyExit();
            }
            return false;
        }

        this.eventbus.emit('loading:animation', {status: true});

        this.payload['samples'] = sampleIds;

        this.loadVariantCalls(this.payload, _data => {
            this.mergeLazyLoadedVariantCalls(_data.calls);
            this.mergeLazyLoadedVariantCallsMetadata(_data.calls_metadata);

            this.data['__lazyLoaded'] = true;
            this.data['calls'] = this.callsMap;
            this.data['calls_metadata'] = this.callsMetadataMaps;

            this.eventbus.emit('loading:animation', {status: false});
            this.eventbus.emit('data:display:changed', this.data);
        });
    }

    loadVariantsAndCalls(payload, callback) {

        this.payload = payload;
        this.generateVariantCallsMap();

        // init/reset some state vars
        this.data = {};
        this.callsMetadataMaps = {};

        let payloadVariantCalls = cloneDeep(payload);
        payloadVariantCalls['samples'] = payloadVariantCalls['samples'].slice(0,30);

        //console.info(this.samplesVisibleInViewport);

        if (this.samplesVisibleInViewport.length > 0) {
            payloadVariantCalls['samples'] = this.samplesVisibleInViewport;
        }

        const requestVariants = axios.post(this.config.apiBaseUrl+'/variants', payload);
        const requestVariantCalls = axios.post(this.config.apiBaseUrl+'/variant_calls', payloadVariantCalls);
          
        axios.all([requestVariants, requestVariantCalls]).then(
            axios.spread(({data:variants}, {data:variant_calls}) => {

                this.mergeLazyLoadedVariantCalls(variant_calls.calls);
                this.mergeLazyLoadedVariantCallsMetadata(variant_calls.calls_metadata);

                this.data = variants;
                this.data['calls'] = this.callsMap;
                this.data['calls_metadata'] = this.callsMetadataMaps;

                callback(this.data);
            })
        );
    }


    loadVariantCalls(payload, callback) {

        let endpoint = this.config.apiBaseUrl+'/variant_calls';
        axios.post(endpoint, payload).then((response) => {
            callback(response.data);
        })
        .catch(error => {
            console.log(error);
            //self.raiseError('Error: Could not load any data from the server / backend.')
            //this.eventbus.emit('loading:animation', {status: false});
        });
    }

}