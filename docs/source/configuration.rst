=============
Configuration
=============

The configuration of your DivBrowse instance is managed by a YAML file:

.. code-block:: yaml

   metadata:
     general_description: 
     vcf_doi: 
     vcf_reference_genome_doi: 
     gff3_doi:


   datadir: /opt/shape/uwsgi/shape/data/


   variants:
     zarr_dir: SNP_matrix_WGS_300_samples.vcf.zarr
     sample_id_mapping_filename: 


   gff3:
     filename: 
     additional_attributes_keys: biotype,gene_id
     feature_type_with_description: gene
     count_exon_variants: true
     key_confidence: 
     key_ontology: Ontology_term
     main_feature_types_for_genes_track:
       - gene
       - pseudogene
       - ncRNA_gene
     external_link_ontology_term: https://www.ebi.ac.uk/QuickGO/term/{ID}
     external_links:
       - feature_attribute: ID
         url: https://some.external.resource.org/{FEATURE_ID}
         linktext: Open this gene in an external resource 


   chromosome_labels:
     1: 1H
     2: 2H
     3: 3H
     4: 4H
     5: 5H
     6: 6H
     7: 7H
     0: Un


   gff3_chromosome_labels:
     1: chr1H
     2: chr2H
     3: chr3H
     4: chr4H
     5: chr5H
     6: chr6H
     7: chr7H
     0: chrUn


   centromeres_positions:
     1: 205502676
     2: 305853815
     3: 271947776
     4: 282386439
     5: 205989812
     6: 260041240
     7: 328847863
     0: 0


   blast:
     active: false
     galaxy_server_url: https://galaxy-web.ipk-gatersleben.de
     galaxy_user: 
     galaxy_pass: 
     galaxy_tool_id: ncbi_blastn_wrapper_barley
     blast_database: morex_v3
     blast_type: megablast
     blast_result_to_vcf_chromosome_mapping:
       chr1H: 1
       chr2H: 2
       chr3H: 3
       chr4H: 4
       chr5H: 5
       chr6H: 6
       chr7H: 7
       chrUn: 0



.. include:: ../../backend/divbrowse.config.yml.example
   :literal:
   :code: yaml