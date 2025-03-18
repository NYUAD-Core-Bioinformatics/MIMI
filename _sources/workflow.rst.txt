Detailed Workflow
===============

This document provides a detailed explanation of MIMI's workflow for mass spectrometry data analysis.

Overview
--------

MIMI's workflow consists of three main phases:

1. **Database Preparation**: Extract and format compound data
2. **Cache Creation**: Precompute molecular masses and isotope patterns
3. **Sample Analysis**: Match sample masses against cached data

Each phase is described in detail below.

Database Preparation
------------------

Before analysis, you need a database of compounds with their chemical formulas. MIMI provides tools to extract this information from common databases:

HMDB Extraction
~~~~~~~~~~~~~

The Human Metabolome Database (HMDB) contains detailed information about small molecule metabolites found in the human body.

1. Download the HMDB database XML file from https://hmdb.ca/downloads
2. Extract metabolites using the MIMI tool::

    mimi_hmdb_extract -x hmdb_metabolites.xml -o hmdb_compounds.tsv -l 100 -u 500

This extracts metabolites with molecular weights between 100 and 500 Da.

KEGG Extraction
~~~~~~~~~~~~~

The Kyoto Encyclopedia of Genes and Genomes (KEGG) provides a comprehensive database of compounds.

1. Extract compounds by mass range::

    mimi_kegg_extract -l 100 -u 500 -o kegg_compounds.tsv

2. Or extract specific compounds by ID::

    mimi_kegg_extract -i compound_ids.tsv -o kegg_compounds.tsv

Custom Database
~~~~~~~~~~~~~

You can also create your own compound database as a TSV file with the following columns:

1. **CF**: Chemical formula (e.g., C6H12O6)
2. **ID**: Compound identifier
3. **name**: Compound name

Example::

    CF      ID      name
    C6H12O6 glucose Glucose
    C5H10O5 ribose  Ribose
    C3H7NO2 alanine Alanine

Cache Creation
------------

Once you have your compound database, create cache files for efficient analysis:

Natural Abundance Cache
~~~~~~~~~~~~~~~~~~~~~

For analyzing samples with natural isotope abundances::

    mimi_cache_create -i neg -d compounds.tsv -c natural_cache

Labeled Compounds Cache
~~~~~~~~~~~~~~~~~~~~~

For analyzing samples with isotope-labeled compounds, you need a JSON file describing the labeled atoms.

Example C13 labeling JSON::

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

Create the labeled cache::

    mimi_cache_create -i neg -l c13_labeling.json -d compounds.tsv -c c13_cache

Cache Inspection
~~~~~~~~~~~~~~

To verify the contents of your cache files::

    mimi_cache_dump -n 5 -i 2 outdir/db_nat.pkl

    # Cache Metadata:
    # Creation Date: YYYY-MM-DDTHH:MM:SS
    # MIMI Version: 1.0.0

    # Creation Parameters:
    # Full Command: /path/to/mimi_cache_create -i neg -d path/to/KEGGDB.tsv -c outdir/db_nat
    # Ionization Mode: neg
    # Labeled Atoms File: None
    # Compound DB Files: path/to/KEGGDB.tsv
    # Cache Output File: outdir/db_nat.pkl
    # Isotope Data File: path/to/natural_isotope_abundance_NIST.json

    ============================================================
    Compound ID:      C00003
    Name:             NAD+
    Formula:          [12]C21[1]H28[14]N7[16]O14[31]P2
    Mono-isotopic:    Yes (most abundant isotope)
    Mass:             663.109671
    Relative Abund:   1.000000 (reference)
    ------------------------------------------------------------
    ISOTOPE VARIANTS:
      Variant #1:
      Formula:        [12]C20 [13]C1 [1]H28 [14]N7 [16]O14 [31]P2
      Mono-isotopic:  No (isotope variant)
      Mass:           664.113026
      Relative Abund: 0.227130
    ------------------------------------------------------------
      Variant #2:
      Formula:        [12]C21 [1]H28 [14]N7 [16]O13 [18]O1 [31]P2
      Mono-isotopic:  No (isotope variant)
      Mass:           665.113916
      Relative Abund: 0.028770
    ------------------------------------------------------------

    ============================================================
    Compound ID:      C00006
    Name:             NADP+
    Formula:          [12]C21[1]H29[14]N7[16]O17[31]P3
    Mono-isotopic:    Yes (most abundant isotope)
    Mass:             743.076002
    Relative Abund:   1.000000 (reference)
    ------------------------------------------------------------
    ISOTOPE VARIANTS:
      Variant #1:
      Formula:        [12]C20 [13]C1 [1]H29 [14]N7 [16]O17 [31]P3
      Mono-isotopic:  No (isotope variant)
      Mass:           744.079357
      Relative Abund: 0.227130
    ------------------------------------------------------------
      Variant #2:
      Formula:        [12]C21 [1]H29 [14]N7 [16]O16 [18]O1 [31]P3
      Mono-isotopic:  No (isotope variant)
      Mass:           745.080247
      Relative Abund: 0.034935
    ------------------------------------------------------------

    ============================================================
    Compound ID:      C00015
    Name:             UDP
    Formula:          [12]C9[1]H14[14]N2[16]O12[31]P2
    Mono-isotopic:    Yes (most abundant isotope)
    Mass:             402.994921
    Relative Abund:   1.000000 (reference)
    ------------------------------------------------------------
    ISOTOPE VARIANTS:
      Variant #1:
      Formula:        [12]C8 [13]C1 [1]H14 [14]N2 [16]O12 [31]P2
      Mono-isotopic:  No (isotope variant)
      Mass:           403.998276
      Relative Abund: 0.097342
    ------------------------------------------------------------
      Variant #2:
      Formula:        [12]C9 [1]H14 [14]N2 [16]O11 [18]O1 [31]P2
      Mono-isotopic:  No (isotope variant)
      Mass:           404.999166
      Relative Abund: 0.024660
    ------------------------------------------------------------

    ============================================================
    Compound ID:      C00016
    Name:             FAD
    Formula:          [12]C27[1]H33[14]N9[16]O15[31]P2
    Mono-isotopic:    Yes (most abundant isotope)
    Mass:             784.149859
    Relative Abund:   1.000000 (reference)
    ------------------------------------------------------------
    ISOTOPE VARIANTS:
      Variant #1:
      Formula:        [12]C26 [13]C1 [1]H33 [14]N9 [16]O15 [31]P2
      Mono-isotopic:  No (isotope variant)
      Mass:           785.153214
      Relative Abund: 0.292025
    ------------------------------------------------------------
      Variant #2:
      Formula:        [12]C27 [1]H33 [14]N8 [15]N1 [16]O15 [31]P2
      Mono-isotopic:  No (isotope variant)
      Mass:           785.146894
      Relative Abund: 0.032880
    ------------------------------------------------------------

    ============================================================
    Compound ID:      C00018
    Name:             Pyridoxal phosphate
    Formula:          [12]C8[1]H10[14]N[16]O6[31]P1
    Mono-isotopic:    Yes (most abundant isotope)
    Mass:             246.017298
    Relative Abund:   1.000000 (reference)
    ------------------------------------------------------------
    ISOTOPE VARIANTS:
      Variant #1:
      Formula:        [12]C7 [13]C1 [1]H10 [14]N1 [16]O6 [31]P1
      Mono-isotopic:  No (isotope variant)
      Mass:           247.020652
      Relative Abund: 0.086526
    ------------------------------------------------------------
      Variant #2:
      Formula:        [12]C8 [1]H10 [14]N1 [16]O5 [18]O1 [31]P1
      Mono-isotopic:  No (isotope variant)
      Mass:           248.021543
      Relative Abund: 0.012330
    ------------------------------------------------------------

Sample Analysis
-------------

With your cache files prepared, you can analyze mass spectrometry samples:

Basic Analysis
~~~~~~~~~~~~

Analyze a single sample against a single cache::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c natural_cache.pkl -s sample.asc -o results.tsv

Multiple Cache Analysis
~~~~~~~~~~~~~~~~~~~~~

Analyze a sample against multiple caches simultaneously::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c natural_cache.pkl c13_cache.pkl -s sample.asc -o results.tsv

This is useful for comparing natural abundance patterns with labeled patterns.

Batch Processing
~~~~~~~~~~~~~~

Process multiple samples in a single run::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c natural_cache.pkl -s sample1.asc sample2.asc sample3.asc -o batch_results.tsv

PPM Threshold Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

The PPM (parts per million) threshold controls the precision of mass matching. Try different thresholds to optimize results::

    # Tight threshold
    mimi_mass_analysis -p 1.0 -vp 1.0 -c natural_cache.pkl -s sample.asc -o results_p1.tsv
    
    # Medium threshold
    mimi_mass_analysis -p 2.0 -vp 2.0 -c natural_cache.pkl -s sample.asc -o results_p2.tsv
    
    # Wide threshold
    mimi_mass_analysis -p 5.0 -vp 5.0 -c natural_cache.pkl -s sample.asc -o results_p5.tsv

Result Interpretation
-------------------

The output TSV file contains detailed information about matched compounds across different isotope configurations:

Sample Information
~~~~~~~~~~~~~~~~
- **CF**: Chemical formula of the compound
- **ID**: Unique identifier from the original database
- **Name**: Common name of the compound
- **C, H, N, O, P, S**: Number of each atom type in the compound

For Each Cache Type (Natural and Labeled)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each cache type (e.g., natural abundance 'nat', C13-labeled 'C13') has its own columns:

- **db_mass**: Theoretical mass from the database
- **mass_measured**: Observed mass in the sample
- **error_ppm**: Parts per million difference between theoretical and observed mass
- **intensity**: Signal intensity in the sample
- **iso_count**: Number of isotope peaks detected

Interpreting Results
~~~~~~~~~~~~~~~~~~

Mass Error (PPM)
^^^^^^^^^^^^^^^
- **< 1 ppm**: Excellent mass accuracy, high confidence in identification
- **1-2 ppm**: Good mass accuracy, reliable identification
- **2-5 ppm**: Moderate mass accuracy, requires additional verification
- **> 5 ppm**: Poor mass accuracy, potential false positive

Isotope Count
^^^^^^^^^^^^
- Higher iso_count values indicate better isotope pattern detection
- Compare iso_count between natural and labeled samples to verify labeling



Tips for Analysis
~~~~~~~~~~~~~~~
1. Focus on compounds with low PPM error and high isotope counts
2. Compare natural vs labeled patterns to confirm labeling
3. Cross-reference multiple samples to validate findings

Advanced Workflows
----------------

Differential Analysis
~~~~~~~~~~~~~~~~~~~

To identify compounds that differ between samples:

1. Analyze multiple samples::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c natural_cache.pkl -s sample1.asc sample2.asc -o all_results.tsv


Isotope Labeling Experiments
~~~~~~~~~~~~~~~~~~~~~~~~~~

For tracking isotope incorporation:

1. Create caches for natural and labeled compounds
2. Analyze samples against both caches
3. Compare isotope patterns to determine labeling efficiency

Time Series Analysis
~~~~~~~~~~~~~~~~~

For monitoring changes over time:

1. Collect samples at different time points
2. Analyze all samples with the same parameters
3. Track compound abundances across time points 