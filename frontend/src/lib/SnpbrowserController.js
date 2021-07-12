import axios from 'axios';
import DataFrame from 'dataframe-js';

export default class SnpbrowserController {

    constructor(eventbus) {
        this.eventbus = eventbus;

        this.metadata = null;

        this.chromosome = 1;
        this.startpos = 1;
        this.endpos = null;
        this.data = null;
        this.snpWidth = 20;

        this.genes = null;

        this.lastBlastResult = false;
        this.blastResultHistory = [];
    }

    setupContainerElement(container) {

    }

    setup(setupObj) {
        this.container = setupObj.container;
        this.config = setupObj.config;

        this.loadMetadata(metadata => {
            this.metadata = metadata;

            this.chromosome = metadata.chromosomes[0]['id'];
            this.startpos = metadata.chromosomes[0]['start'];

            this.eventbus.emit('metadata:loaded', metadata);

            if (this.config.showAllSamplesOnInit === true) {
                this.config.samples = this.metadata.samples;
            }

            this.draw();

            this.loadGenes(genes => {
                this.metadata.gff3._dataframe = new DataFrame(genes.data, genes.columns);
            });
        });
    }

    setChromosome(chromosome) {
        this.chromosome = chromosome;
        this.startpos = this.metadata.chromosomesById[chromosome].start;
        this.draw();
    }

    setSnpWidth(snpWidth) {
        this.snpWidth = snpWidth;
        this.draw();
    }

    resetStartpos() {
        this.startpos = this.metadata.chromosomesById[this.chromosome]['start'];
        this.endpos = null;
    }

    setToEnd() {
        this.endpos = this.metadata.chromosomesById[this.chromosome]['end'];
        this.startpos = null;
    }

    goToPosition(position) {
        this.startpos = position;
        this.endpos = null;
        this.draw();
    }

    goToChromosomeAndPosition(chromosome, position) {
        this.chromosome = chromosome.toString();
        this.startpos = position;
        this.endpos = null;
        this.draw();
    }

    goForward(steps) {
        if (this.data.coordinate_last < this.data.coordinate_first_next) {
            this.startpos = this.data.coordinate_first_next;

            if (steps !== undefined) {
                steps = parseInt(steps);
                this.startpos = this.data.variants_coordinates[steps];
            }

            this.endpos = null;
            this.draw();
        }
    }

    goBackward(steps) {
        if (this.data.coordinate_last_prev < this.data.coordinate_first) {
            this.startpos = null;
            this.endpos = this.data.coordinate_last_prev;

            if (steps !== undefined) {
                steps = parseInt(steps);
                let endposIndex = this.data.variants_coordinates.length - steps - 1;
                this.endpos = this.data.variants_coordinates[endposIndex];
            }

            this.draw();
        }
    }

    setSamples(samples) {

        if (typeof samples[0] === 'string') {
            this.config.samples = samples;
            this.config.samplesMetadata = false;
        }

        if (typeof samples[0] === 'object') {
            let sample_ids = samples.map(item => item.id);
            this.config.samples = sample_ids;
            let bykey = {};
            samples.forEach(sample => { bykey[sample.id] = sample });
            this.config.samplesMetadata = bykey;
        }
        
        this.draw();
    }


    _calculateSnpCountInVisibleArea() {
        return Math.floor( (this.container.width() - 200) / this.snpWidth );
    }

    getCurrentWidthOfVariants() {
        return this.snpWidth * this._calculateSnpCountInVisibleArea();
    }


    async loadMetadata(callback) {
        if (this.metadata !== null) {
            callback(this.metadata);
        }
        const self = this;
        let keyedChromosomes = {};
        let url = this.config.apiBaseUrl+'/metadata';
        axios.get(url).then(function (response) {
            callback(response.data);
            self.metadata = response.data;
            self.metadata.chromosomes.forEach((chrom) => {
                keyedChromosomes[chrom.id] = chrom;
            });
            self.metadata.chromosomesById = keyedChromosomes;
        })
        .catch(function (error) {
            console.log(error);
            self.raiseError('Error: Could not load any data from the server / backend.')
        });
    }

    getMetadata() {
        return this.metadata;
    }


    async loadGenes(callback) {
        if (this.genes !== null) {
            callback(this.genes);
        }
        let url = this.config.apiBaseUrl+'/genes';
        axios.get(url).then(response => {
            callback(response.data.genes);
            this.genes = response.data.genes;
        })
        .catch(error => {
            console.log(error);
            this.raiseError('Error: Could not load genes data from the server / backend.')
        });
    }


    async vcf_export_check(params, callback) {

        let samples;
        if (this.config.samples === undefined || this.config.samples.length == 0) {
            samples = this.metadata.samples;
        } else {
            samples = this.config.samples;
        }

        let payload = {
            chrom: this.chromosome,
            startpos: params['startpos'],
            endpos: params['endpos'],
            samples: samples
        };

        if (params['variantFilterSettings'] !== undefined && typeof params['variantFilterSettings'] === 'object') {
            payload['variant_filter_settings'] = params['variantFilterSettings'];
        }

        axios.post(this.config.apiBaseUrl+'/vcf_export_check', payload).then(function (response) {
            callback(response.data);
        })
        .catch(function (error) {
            console.log(error);
        });
    }


    async snp_window_summary(params, callback) {
        let samples;
        if (this.config.samples === undefined || this.config.samples.length == 0) {
            samples = this.metadata.samples;
        } else {
            samples = this.config.samples;
        }

        let payload = {
            chrom: this.chromosome,
            startpos: params['startpos'],
            endpos: params['endpos'],
            samples: samples
        };

        if (params['variantFilterSettings'] !== undefined && typeof params['variantFilterSettings'] === 'object') {
            payload['variant_filter_settings'] = params['variantFilterSettings'];
        }

        axios.post(this.config.apiBaseUrl+'/snp_window_summary', payload).then(function (response) {
            callback(response.data);
        })
        .catch(function (error) {
            console.log(error);
        });
    }


    async pca(params, callback) {
        let samples;
        if (this.config.samples === undefined || this.config.samples.length == 0) {
            samples = this.metadata.samples;
        } else {
            samples = this.config.samples;
        }

        let payload = {
            chrom: this.chromosome,
            startpos: params['startpos'],
            endpos: params['endpos'],
            samples: samples
        };

        if (params['variantFilterSettings'] !== undefined && typeof params['variantFilterSettings'] === 'object') {
            payload['variant_filter_settings'] = params['variantFilterSettings'];
        }

        this.eventbus.emit('loading:animation:pca', {status: true});

        axios.post(this.config.apiBaseUrl+'/pca', payload).then(response => {
            this.eventbus.emit('loading:animation:pca', {status: false});
            callback(response.data);
        })
        .catch(error => {
            console.log(error);
            this.eventbus.emit('loading:animation:pca', {status: false});
            //self.raiseError('Error: Could not load any data from the server / backend.')
        });
    }


    async blast(query, callback) {
        const payload = {
            query: query
        };

        let url = this.config.apiBaseUrl+'/blast'
        axios.post(url, payload).then(response => {
            let blastResult = response.data.blast_hits;
            this.lastBlastResult = blastResult;
            this.blastResultHistory.push({
                query: query,
                blast_hits: blastResult,
                timestamp: new Date().toLocaleString()
            });
            callback(blastResult);
        })
        .catch(error => {
            console.log(error);
            //self.raiseError('Error: Could not load any data from the server / backend.')
        });

    }


    async loadData(callback) {
        let count = this._calculateSnpCountInVisibleArea();

        if (count < 1) {
            return false;
        }

        let samples = [];
        /*if (this.config.samples === undefined || this.config.samples.length == 0) {
            samples = this.metadata.samples;
        } else {
            samples = this.config.samples;
        }*/

        if (this.config.showAllSamplesOnInit === true) {
            samples = this.metadata.samples;
        }

        if (this.config.samples !== undefined && this.config.samples.length > 0) {
            samples = this.config.samples;
        }

        if (samples.length == 0) {
            return;
        }

        let url = this.config.apiBaseUrl+'/variants'
        const payload = {
            chrom: this.chromosome,
            samples: samples,
            count: count
        }

        if (this.startpos !== null && this.startpos > 0) {
            payload['startpos'] = this.startpos;
        }
        if (this.endpos !== null && this.endpos > 0) {
            payload['endpos'] = this.endpos;
        }

        this.eventbus.emit('loading:animation', {status: true});

        axios.post(url, payload).then(function (response) {
            callback(response.data);
        })
        .catch(error => {
            console.log(error);
            //self.raiseError('Error: Could not load any data from the server / backend.')
            this.eventbus.emit('loading:animation', {status: false});
        });
    }

    draw() {
        this.loadData(data => {
            this.data = data;

            if (this.data.coordinate_first > this.data.coordinate_last || this.data.coordinate_first > this.data.coordinate_first_next) {

                if (this.data.coordinate_first > this.data.coordinate_last && this.data.coordinate_first_chromosome < this.chromosome) {
                    this.resetStartpos();
                }

                if (this.data.coordinate_first > this.data.coordinate_first_next && this.data.coordinate_last_chromosome > this.chromosome) {
                    this.setToEnd();
                }

                this.loadData(data => {
                    this.data = data;
                    this.eventbus.emit('data:display:changed', data);
                    this.eventbus.emit('loading:animation', {status: false});
                });
            } else {
                this.eventbus.emit('data:display:changed', data);
                this.eventbus.emit('loading:animation', {status: false});
            }
        });
    }

    raiseError(msg) {
        alert(msg);
    }
}