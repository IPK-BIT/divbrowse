<script>
export let data;

import GenomicRegionGrid from '@/components/tracks/GenomicRegionGrid.svelte';

import { onMount, getContext } from 'svelte';
let { appId, eventbus, controller } = getContext('app').app();

const rootElem = getContext('rootElem');

import getStores from '@/utils/store';
const { variantWidth } = getStores();

import { delegate } from 'tippy.js';

let widthAllVariants;

let maxmin;

let features = {};
let featuresKeyedById = {};

let yOffset = {
    plusStrand: 20,
    minusStrand: 32,
    variant: 40,
    curveTop: 45,
    controlPoint: 62,
    curveBottom: 80
}

const tippyProps = {
    delay: 0,
    appendTo: rootElem,
    target: 'div#'+appId+' line.gene',
    animation: false,
    placement: "bottom",
    allowHTML: true,
    onShow(instance) {
        let content = 'Type: '+featuresKeyedById[instance.reference.dataset.featureId].type;
        content += '<br /><br />ID: '+instance.reference.dataset.featureId;
        
        if (featuresKeyedById[instance.reference.dataset.featureId].description !== '.') {
            content += '<br /><br />Description: '+featuresKeyedById[instance.reference.dataset.featureId].description;
        }

        content += '<br /><br />Click to show more details.';

        instance.setContent(content);
    }
};

let svg;
let height = 30;

let tippyInstance;

$: {
    widthAllVariants = controller.getCurrentWidthOfVariants();
    maxmin = data.coordinate_last - data.coordinate_first;

    features = {
        plus: {
            gene: [],
            exon: []
        },
        minus: {
            gene: [],
            exon: []
        },
    };

    let x1, x2;
    for (const feature of data.features) {

        featuresKeyedById[feature.ID] = feature;
        
        x1 = 0;
        x2 = 1;

        if (feature.strand == '+') {

            if (feature.start > data.coordinate_first) {
                x1 = (feature.start - data.coordinate_first) / maxmin;
            }
            if (feature.end < data.coordinate_last) {
                x2 = (feature.end - data.coordinate_first) / maxmin;
            }

            if (controller.metadata.gff3.main_feature_types_for_genes_track.includes(feature.type)) {
                features.plus.gene.push({x1: x1, x2: x2, description: feature.description, ID: feature.ID, gff3: feature});
            }
            if (feature.type == 'exon') {
                features.plus.exon.push({x1: x1, x2: x2});
            }
        }
        if (feature.strand == '-') {

            if (feature.start > data.coordinate_first) {
                x1 = (feature.start - data.coordinate_first) / maxmin;
            }
            if (feature.end < data.coordinate_last) {
                x2 = (feature.end - data.coordinate_first) / maxmin;
            }

            if (controller.metadata.gff3.main_feature_types_for_genes_track.includes(feature.type)) {
                features.minus.gene.push({x1: x1, x2: x2, description: feature.description, ID: feature.ID, gff3: feature});
            }
            if (feature.type == 'exon') {
                features.minus.exon.push({x1: x1, x2: x2});
            }
        }
    }

    if (tippyInstance !== undefined && typeof tippyInstance.destroy === "function") {
        tippyInstance.destroy();
    }
    tippyInstance = delegate(rootElem.querySelector('#tracks-container'), tippyProps);

}


const openGeneDetailsModal = (featureId) => {
    eventbus.emit('modal:open', {
        component: 'GeneDetails',
        props: {
            featureId: featureId
        }
    });
};

let cursorlinePos = '0px';
let cursorlabelPos = 0;
let _div;
let x = 0;
let bounds; // = _div.getBoundingClientRect();
let cursorlineVisibility = 'hidden';


function cursorpos(ev) {
    bounds = _div.getBoundingClientRect();
    x = ev.clientX - bounds.left;
    cursorlinePos = x+'px';
    let position = ((x / (widthAllVariants-5)) * maxmin) + data.coordinate_first;
    cursorlabelPos = Math.ceil(position);
}

</script>




<div class="track genomic-region" style="">

    <div class="label" style="">Genes and variants<br />in genomic region</div>

    <!--<div 
        bind:this={_div} 
        on:mousemove={(ev) => cursorpos(ev)} 
        on:mouseenter={() => cursorlineVisibility = 'visible'} 
        on:mouseleave={() => cursorlineVisibility = 'hidden'} 
        style="width: {widthAllVariants}px; border: 1px solid black; position: relative;">-->

    <div 
        bind:this={_div} 
        style="width: {widthAllVariants}px; border: 1px solid black; position: relative;">

        <div id="cursorline" style:left={cursorlinePos} style:visibility={cursorlineVisibility}></div>
        <div id="cursorline-pos" style:left={cursorlinePos} style:visibility={cursorlineVisibility}>{cursorlabelPos.toLocaleString()}</div>

        <div id="svg-container" style="width: {widthAllVariants}px;">
            <svg width="{widthAllVariants}" height="80" bind:this={svg}>
                <defs>
                    <symbol id="arrow" viewBox="0 0 50 50" width="50" height="50">
                        <g transform="scale(0.5)">
                            <path d="M21.883 12l-7.527 6.235.644.765 9-7.521-9-7.479-.645.764 7.529 6.236h-21.884v1h21.883z"/>
                        </g>
                    </symbol>
                    <symbol id="arrow-reverse" viewBox="0 0 50 50" width="50" height="50">
                        <g transform="scale(0.5) scale(-1 1) translate(-25 0)">
                            <path d="M21.883 12l-7.527 6.235.644.765 9-7.521-9-7.479-.645.764 7.529 6.236h-21.884v1h21.883z"/>
                        </g>
                    </symbol>
                </defs>

                {#each data.variants_coordinates as position}
                <rect id="snp-{position}" x="{ ((position - data.coordinate_first) / maxmin) * (widthAllVariants-5) }" y="{yOffset.variant}" width="5" height="5" stroke="rgb(140,140,140)" fill="none" />
                {/each}


                {#each features.plus.gene as feature}
                <line id="{feature.ID}" data-feature-id="{feature.ID}" class="mrna" x1="{ feature.x1 * widthAllVariants }" y1="{yOffset.plusStrand}" x2="{ feature.x2 * widthAllVariants }" y2="{yOffset.plusStrand}" stroke-width="3" stroke="rgb(200,200,200)" />
                    {#if feature.x2 < 0.99}
                    <use xlink:href="#arrow" x="{ (feature.x2 * widthAllVariants) + 1 }" y="{yOffset.plusStrand - 6}" />
                    {/if}
                {/each}


                {#each features.plus.exon as feature}
                <line class="exon" x1="{ feature.x1 * widthAllVariants }" y1="{yOffset.plusStrand}" x2="{ feature.x2 * widthAllVariants }" y2="{yOffset.plusStrand}" stroke-width="7" stroke="rgb(0,190,0)" />
                {/each}


                {#each features.plus.gene as feature}
                <a target="_blank" on:click|preventDefault={openGeneDetailsModal(feature.ID)} href="#">
                    <line id="{feature.ID}" data-feature-id="{feature.ID}" class="gene" x1="{ feature.x1 * widthAllVariants }" y1="{yOffset.plusStrand}" x2="{ feature.x2 * widthAllVariants }" y2="{yOffset.plusStrand}" stroke-width="9" stroke="rgba(200,200,200,0.0)" />
                </a>
                <!--<text text-anchor="left" x="{ feature.x1 * widthAllVariants }" y="{yOffset.plusStrand}" style="z-index: 100; font-family: sans-serif; font-size: 10px;">{feature.ID}</text>-->
                {/each}


                {#each features.minus.gene as feature}
                <line id="{feature.ID}" data-feature-id="{feature.ID}" class="mrna" x1="{ feature.x1 * widthAllVariants }" y1="{yOffset.minusStrand}" x2="{ feature.x2 * widthAllVariants }" y2="{yOffset.minusStrand}" stroke-width="3" stroke="rgb(200,200,200)" />
                    {#if feature.x1 > 0.01}
                    <use xlink:href="#arrow-reverse" x="{ (feature.x1 * widthAllVariants) - 14 }" y="{yOffset.minusStrand - 6}" />
                    {/if}
                {/each}


                {#each features.minus.exon as feature}
                <line class="exon" x1="{ feature.x1 * widthAllVariants }" y1="{yOffset.minusStrand}" x2="{ feature.x2 * widthAllVariants }" y2="{yOffset.minusStrand}" stroke-width="7" stroke="rgb(0,190,0)" />
                {/each}


                {#each features.minus.gene as feature}
                <a target="_blank" on:click|preventDefault={openGeneDetailsModal(feature.ID)} href="#">
                    <line id="{feature.ID}" data-feature-id="{feature.ID}" class="gene" x1="{ feature.x1 * widthAllVariants }" y1="{yOffset.minusStrand}" x2="{ feature.x2 * widthAllVariants }" y2="{yOffset.minusStrand}" stroke-width="9" stroke="rgba(200,200,200,0.0)" />
                </a>
                {/each}


                <!--<path class="curve" d="M1,1 C1,50 {xbot},50 {xbot},99" />-->
                <!--<path class="curve" d="M1,{yOffset.curveTop} C1,{yOffset.controlPoint} {xbot},{yOffset.controlPoint} {xbot},{yOffset.curveBottom}" />-->

                {#each data.variants_coordinates as position, col}
                <path id="variant-bezier-{position}" class="curve" d="M{(( ((position - data.coordinate_first) / maxmin) * (widthAllVariants-5) ) + 3)},{yOffset.curveTop} C{(( ((position - data.coordinate_first) / maxmin) * (widthAllVariants-5) ) + 3)},{yOffset.controlPoint} {((col * $variantWidth) + 10)},{yOffset.controlPoint} {((col * $variantWidth) + 10)},{yOffset.curveBottom}" />
                {/each}


                <GenomicRegionGrid data={data} />


            </svg>
        </div>

    </div>
</div>

<style>

#cursorline {
    position: absolute;
    /*left: 200px;*/
    top: -1px;
    width: 1px;
    height: 81px;
    border-left: 1.5px dotted rgb(50,50,50);
}

#cursorline-pos {
    position: absolute;
    /*left: 200px;*/
    top: 4px;
    
    padding: 3px;
    margin-left: 1px;
    border: 1px solid black;
    background: white;
    font-size: 11px;
}

#arrow {
    transform-origin: 50% 50%;
}

.arrow-small {
    transform: scale(2);
    transform-origin: 0% 0%;
    transform-box: fill-box;
}

:global(.highlight-snp) {
    fill: #0000FF;
    stroke: #0000FF;
}



div.track.genomic-region {
    height: 80px;
}

#svg-container {
    height: 80px;
}


#genomic-region {
    width: 400px;
    height: 14px;
    background: rgb(240,240,240);
    border: 1px solid rgb(150,150,150);
    border-radius: 7px;
    position: relative;
}



.gene:hover {
    stroke: rgba(0,0,0,0.1);
    cursor: pointer;
}

path.curve {
	stroke-width: 1;
	stroke: rgb(215,215,215);
	stroke-linecap: round;
	fill: none;
}

path.curve.fill {
	fill: rgb(215,215,215);
}

:global(.highlight-variant-bezier) {
    stroke: #0000FF !important;
    stroke-width: 2 !important;
}

</style>