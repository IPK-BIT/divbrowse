<script>
export let close;
export let position;
export let snpeff_data;

let snpeffAnnAttrs = [
    'Allele',
    'Annotation',
    'Annotation_Impact',
    'Gene_Name',
    'Gene_ID',
    'Feature_Type',
    'Feature_ID',
    'Transcript_BioType',
    'Rank',
    'HGVS.c',
    'HGVS.p',
    'cDNA.pos / cDNA.length',
    'CDS.pos / CDS.length',
    'AA.pos / AA.length',
    'Distance',
    'ERRORS / WARNINGS / INFO'
];


if (!Array.isArray(snpeff_data)) {
    snpeff_data = [snpeff_data];
}

let lines = [];
snpeff_data.forEach(ann => {
    if (ann !== "") {
        let tmp = ann.split("|");
        let i = 0;
        let entries = [];
        tmp.forEach(attrValue => {
            entries.push(attrValue);
            i++;
        });
        lines.push(entries);
    }
});

</script> 
 

<div style="max-width: 80vw;">
    <div class="divbrowse-modal-dialogue-headline">SnpEff annotation</div>

    Position: {position}<br /><br />

    <div style="width: 100%; overflow: auto;">
    <table id="snpeff-annotations" border="1" cellpadding="0" cellspacing="0">
        <tr>
        {#each snpeffAnnAttrs as attr}
        <th>{attr}</th>
        {/each}
        </tr>

        {#each lines as line}
        <tr>
            {#each line as attr_entry}
            <td>{attr_entry}</td>
            {/each}
        </tr>
        {/each}

    </table>
    </div>

</div>

<style>

table#snpeff-annotations {
    font-size: 90%;
}

table#snpeff-annotations tr th,td {
    padding: 3px;
}

</style>