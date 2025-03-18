Comprehensive Tutorial
====================

This tutorial provides a step-by-step guide to using MIMI for mass spectrometry data analysis, with detailed examples and explanations.

Prerequisites
-----------

Before starting, ensure you have:

1. Installed MIMI (see :doc:`installation`)
2. Basic understanding of mass spectrometry concepts
3. Sample data files in ASC format
4. Access to compound databases (KEGG, HMDB, or custom)

Example Files
-----------

For this tutorial, we'll use the following example files:

- ``sample.asc``: Mass spectrometry data file
- ``compounds.tsv``: Custom compound database
- ``c13_labeling.json``: C13 labeling configuration

You can create these files or use your own data.

Step 1: Create a Custom Compound Database
---------------------------------------

First, let's create a simple compound database with common metabolites:

1. Create a file named ``compounds.tsv`` with the following content::

    CF      ID      name
    C6H12O6 glc     Glucose
    C5H10O5 rib     Ribose
    C3H7NO2 ala     Alanine
    C4H9NO3 asp     Aspartic acid
    C5H9NO4 glu     Glutamic acid
    C2H5NO2 gly     Glycine
    C6H14N4O2 arg   Arginine
    C9H11NO3 tyr    Tyrosine
    C5H11NO2S met   Methionine
    C3H7NO3  ser    Serine

2. Alternatively, extract compounds from KEGG or HMDB::

    # From KEGG
    mimi_kegg_extract -l 100 -u 500 -o compounds.tsv
    
    # From HMDB
    mimi_hmdb_extract -x hmdb_metabolites.xml -o compounds.tsv

Step 2: Create Cache Files
------------------------

Next, create cache files for different isotope configurations:

1. Create a natural abundance cache::

    mimi_cache_create -i neg -d compounds.tsv -c natural_cache

2. Create a C13-labeled cache:

   a. Create a file named ``c13_labeling.json`` with the following content::

       {
         "C": [
           {
             "element_symbol": "C",
             "nominal_mass": 13,
             "exact_mass": 13.003354826,
             "natural_abundance": 0.9893
           },
           {
             "element_symbol": "C",
             "nominal_mass": 12,
             "exact_mass": 12.0,
             "natural_abundance": 0.0107
           }
         ]
       }

   b. Create the labeled cache::

       mimi_cache_create -i neg -l c13_labeling.json -d compounds.tsv -c c13_cache

3. Verify the cache contents::

    mimi_cache_dump natural_cache.pkl -n 3 -o natural_cache_contents.tsv
    mimi_cache_dump c13_cache.pkl -n 3 -o c13_cache_contents.tsv

Step 3: Analyze a Sample
----------------------

Now, analyze a mass spectrometry sample:

1. Basic analysis with natural abundance cache::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c natural_cache.pkl -s sample.asc -o results_natural.tsv

2. Analysis with C13-labeled cache::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c c13_cache.pkl -s sample.asc -o results_c13.tsv

3. Combined analysis with both caches::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c natural_cache.pkl c13_cache.pkl -s sample.asc -o results_combined.tsv

Step 4: Optimize PPM Thresholds
-----------------------------

Experiment with different PPM thresholds to optimize results:

1. Tight threshold (high precision, fewer matches)::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c natural_cache.pkl -s sample.asc -o results_p1.tsv

2. Medium threshold (balanced precision and recall)::

    mimi_mass_analysis -p 2.0 -vp 2.0 -c natural_cache.pkl -s sample.asc -o results_p2.tsv

3. Wide threshold (lower precision, more matches)::

    mimi_mass_analysis -p 5.0 -vp 5.0 -c natural_cache.pkl -s sample.asc -o results_p5.tsv

4. Compare the results to determine the optimal threshold for your data.

Step 5: Batch Processing
----------------------

Process multiple samples in a single run:

1. Prepare multiple sample files: ``sample1.asc``, ``sample2.asc``, ``sample3.asc``

2. Process all samples with the same parameters::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c natural_cache.pkl -s sample1.asc sample2.asc sample3.asc -o batch_results.tsv

Step 6: Interpret Results
-----------------------

The output TSV file contains detailed information about matched compounds:

1. Open the results file in a spreadsheet program or text editor
2. Look for compounds with:
   - Low PPM values (high mass accuracy)
   - High isotope scores (good pattern matching)
   - High intensity values (strong signal)

3. Filter results based on your criteria:
   - PPM < 2.0 for high confidence matches
   - Isotope score > 0.8 for reliable pattern matching

Advanced Topics
-------------

Isotope Labeling Experiments
~~~~~~~~~~~~~~~~~~~~~~~~~~

For tracking isotope incorporation:

1. Create caches for natural and labeled compounds
2. Analyze samples against both caches
3. Compare isotope patterns to determine labeling efficiency
4. Look for shifts in mass corresponding to labeled atoms

Custom Labeling Configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create custom labeling configurations for different experiments:

1. N15 labeling::

    {
      "N": [
        {
          "element_symbol": "N",
          "nominal_mass": 15,
          "exact_mass": 15.000108898,
          "natural_abundance": 0.9963
        },
        {
          "element_symbol": "N",
          "nominal_mass": 14,
          "exact_mass": 14.003074,
          "natural_abundance": 0.0037
        }
      ]
    }

2. Multiple element labeling (C13 and N15)::

    {
      "C": [
        {
          "element_symbol": "C",
          "nominal_mass": 13,
          "exact_mass": 13.003354826,
          "natural_abundance": 0.9893
        },
        {
          "element_symbol": "C",
          "nominal_mass": 12,
          "exact_mass": 12.0,
          "natural_abundance": 0.0107
        }
      ],
      "N": [
        {
          "element_symbol": "N",
          "nominal_mass": 15,
          "exact_mass": 15.000108898,
          "natural_abundance": 0.9963
        },
        {
          "element_symbol": "N",
          "nominal_mass": 14,
          "exact_mass": 14.003074,
          "natural_abundance": 0.0037
        }
      ]
    }

Troubleshooting
-------------

Common Issues and Solutions:

1. **No matches found**:
   - Try increasing the PPM threshold
   - Verify sample format and mass range
   - Check ionization mode matches sample preparation

2. **Too many matches**:
   - Decrease the PPM threshold
   - Use stricter verification PPM
   - Filter results by isotope score

3. **Cache creation errors**:
   - Check chemical formulas in database
   - Verify labeled atoms configuration
   - Enable debug mode for detailed error messages

4. **Slow analysis**:
   - Use smaller compound databases
   - Process samples individually
   - Optimize cache files for specific mass ranges

Conclusion
---------

This tutorial covered the basic and advanced usage of MIMI for mass spectrometry data analysis. By following these steps, you should be able to:

1. Create compound databases from various sources
2. Generate cache files for different isotope configurations
3. Analyze samples with appropriate PPM thresholds
4. Process multiple samples efficiently
5. Interpret results and identify compounds with confidence

For more information, refer to the other documentation sections:

- :doc:`user_guide` for detailed usage information
- :doc:`command_reference` for command-line options
- :doc:`api_reference` for programmatic usage 