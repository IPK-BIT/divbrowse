==============
Javascript API
==============

DivBrowse's Javascript API can be used to control the samples to be displayed.
It also provides the possibility to get all sample IDs that have been selected in the scatterplot of a PCA/UMAP data analysis.

Control the displayed samples
=============================

First you need to instantiate the DivBrowse instance:


.. code-block:: javascript

    document.addEventListener("DOMContentLoaded", function(event) {
        const config = {
            apiBaseUrl: 'http://divbrowse.myinstitute.org'
        }
        const divbrowse_instance = divbrowse.startApp('divbrowse-container', config);
    });


Then your are able to set a list with sample IDs to be displayed in DivBrowse via the setSamples() method:

.. code-block:: javascript

    const samples = [
        { id: 'BRIDGE_WGS_FT219' },
        { id: 'BRIDGE_WGS_FT262' },
        { id: 'BRIDGE_WGS_FT340' }
    ];

    divbrowse_instance.setSamples(samples);


Control the displayed samples and change displayed labels of the samples
========================================================================

Sometimes the internal sample IDs in the VCF files are either not human readable or are different from what you want to display to the user.
In this case, you can change the display name of each sample as follows:

.. code-block:: javascript

    const samples = [
        { id: 'BRIDGE_WGS_FT219', displayName: 'FT 219' },
        { id: 'BRIDGE_WGS_FT262', displayName: 'FT 262' },
        { id: 'BRIDGE_WGS_FT340', displayName: 'FT 340' }
    ];

    divbrowse_instance.setSamples(samples);


Control the displayed samples and provided a link as label
==========================================================

It is also possible to apply <a> HTML-tags as labels for the displayed samples:

.. code-block:: javascript

    const samples = [
        { id: 'BRIDGE_WGS_FT219', link: '<a href="http://www.xyz.org/BRIDGE_WGS_FT219" target="_blank" class="extlink">FT 219</a>' },
        { id: 'BRIDGE_WGS_FT262', link: '<a href="http://www.xyz.org/BRIDGE_WGS_FT262" target="_blank" class="extlink">FT 262</a>' },
        { id: 'BRIDGE_WGS_FT340', link: '<a href="http://www.xyz.org/BRIDGE_WGS_FT340" target="_blank" class="extlink">FT 340</a>' }
    ];

    divbrowse_instance.setSamples(samples);


Getting back IDs of samples that have been selected in a scatterplot
====================================================================

Users of DivBrowse can perform dimensionality reduction of variant calls. In the resulting scatterplots, the user can select a range of
samples. DivBrowse's Javascript API provides a callback function that is automatically called when the user makes a selection of samples.
You can use this callback function as follows:


.. code-block:: javascript

    const samplesSelectedCallback = (selectedSamples) => {
        /*
            The function argument `selectedSamples` is an array 
            of sample IDs that have been selected in the scatterplot
        */
        console.log('The following samples have been selected in DivBrowse: ', selectedSamples);
    }

    document.addEventListener("DOMContentLoaded", function(event) {
        const config = {
            apiBaseUrl: 'http://divbrowse.myinstitute.org',
            samplesSelectedCallback: samplesSelectedCallback
        }
        const divbrowse_instance = divbrowse.startApp('divbrowse-container', config);
    });