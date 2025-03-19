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

Example of ``compound_ids.tsv`` file::

    ID
    C00003
    C00006
    C00015
    C00016
    C00018
    C00019
    C00021
    C00024

This file should contain a header row with **ID** followed by the KEGG compound IDs you wish to extract.

You can download a sample ``compound_ids.tsv`` file from the following link: `compound_ids.tsv <https://raw.githubusercontent.com/NYUAD-Core-Bioinformatics/MIMI/main/data/processed/compound_ids.tsv>`_

Custom Database
~~~~~~~~~~~~~

You can also create your own compound database as a TSV file. While the file can include other metadata, it must contain the following mandatory columns:

1. **CF**: Chemical formula (e.g., C6H12O6)
2. **ID**: Compound identifier
3. **Name**: Compound name

These columns can appear in any order within the file.

Updated Example::

    CF      ID        Name
    C6H12O6 C00031    Glucose
    C5H10O5 C00036    Ribose
    C3H7NO2 C00041    Alanine
    C7H6O2  C00042    Benzoic Acid
    C4H8O4  C00043    Erythritol

Ensure that your TSV file includes a header row and follows this format for compatibility with MIMI.

Cache Creation
------------

Once you have your compound database, create cache files for efficient analysis:

1. **Natural abundance cache**::

    mimi_cache_create -i neg -d data/KEGGDB.tsv -c db_nat

2. **Labeled compounds cache** (e.g., 95% C13-labeled)::

    mimi_cache_create -i neg -l data/C13_95.json -d data/KEGGDB.tsv -c db_13C

Parameters:
  - `-i neg`: Ionization mode (negative)
  - `-d data/KEGGDB.tsv`: Input database file
  - `-c db_nat`: Output cache file name
  - `-l data/C13_95.json`: Optional labeled atoms configuration

Example C13 labeling configuration (C13_95.json)::

    {
        "C": [
            {
                "element_symbol": "C",
                "nominal_mass": 12,
                "exact_mass": 12.000,
                "natural_abundance": 0.05
            },
            {
                "element_symbol": "C",
                "nominal_mass": 13,
                "exact_mass": 13.00335484,
                "natural_abundance": 0.95
            }
        ]
    }

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

    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat -s data/sample.asc -o results.tsv

Parameters:
  - `-p 1.0`: PPM tolerance for initial mass matching
  - `-vp 1.0`: PPM tolerance for isotope pattern verification
  - `-c db_nat`: Cache file(s) to use
  - `-s data/sample.asc`: Sample file(s) to analyze
  - `-o results.tsv`: Output file for results

Multiple Cache Analysis
~~~~~~~~~~~~~~~~~~~~~

Analyze a sample against multiple caches simultaneously::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat db_13C -s data/sample.asc -o results.tsv

This is useful for comparing natural abundance patterns with labeled patterns.

Batch Processing
~~~~~~~~~~~~~~

Process multiple samples in a single run::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat -s data/sample1.asc data/sample2.asc -o batch_results.tsv

PPM Threshold Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

The PPM threshold critically affects match precision and reliability:

- **Excellent (p=0.5, vp=0.5)**: Highest confidence identifications, recommended for ultra-high resolution data
- **Good (p=1.0, vp=1.0)**: Reliable identifications when combined with isotope pattern validation
- **Low Confidence (p=1.0-2.0, vp=1.0-2.0)**: Use with caution, requires additional validation
- **Not Recommended (p>2.0, vp>2.0)**: Should not be used for ultra-high resolution MS data

Example threshold usage::

    # Highest confidence analysis
    mimi_mass_analysis -p 0.5 -vp 0.5 -c db_nat -s sample.asc -o results_excellent.tsv

    # Good confidence analysis
    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat -s sample.asc -o results_good.tsv

Result Interpretation
-------------------

The output TSV file contains the following columns:

1. **Compound ID**: Identifier from the original database
2. **Formula**: Chemical formula of the matched compound
3. **Name**: Compound name
4. **Mass**: Calculated mass of the compound
5. **Sample Mass**: Observed mass in the sample
6. **PPM**: Parts per million difference between calculated and observed mass
7. **Intensity**: Signal intensity in the sample
8. **Isotope Score**: Confidence score based on isotope pattern matching
9. **Cache Source**: Which cache file provided the match

Best Practices and Troubleshooting
-------------------

Best Practices
Best Practices:

1. Use appropriate PPM thresholds based on instrument resolution:
   - <0.5 ppm: Excellent mass accuracy, highest confidence
   - 0.5-1.0 ppm: Good mass accuracy, reliable with isotope validation
   - 1.0-2.0 ppm: Low confidence, requires additional validation
   - >2.0 ppm: Not recommended for ultra-high resolution data

2. Always combine mass accuracy with isotope pattern matching

3. Use isotope score > 0.8 for reliable matches

4. Compare results from natural and labeled caches

5. Process replicates together for consistency

6. Verify important matches manually

Common Issues and Solutions:

1. **No matches found**:
   - Increase PPM threshold
   - Verify sample format
   - Check ionization mode

2. **Too many matches**:
   - Decrease PPM threshold
   - Use stricter verification PPM
   - Filter by isotope score

3. **Cache creation errors**:
   - Verify chemical formulas
   - Check labeling configuration
   - Enable debugging

4. **Performance issues**:
   - Use focused databases
   - Process samples in smaller batches
   - Optimize mass ranges

