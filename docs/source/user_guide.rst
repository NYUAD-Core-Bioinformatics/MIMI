User Guide
=========

This guide provides detailed information on using MIMI for mass spectrometry data analysis.

Basic Workflow
-------------
1. Create cache files for your compounds
2. Analyze samples using the cache files
3. Process and interpret results

Creating Cache Files
------------------

Cache files store precomputed molecular masses and isotope patterns for efficient analysis.

1. **Natural abundance cache**::

    mimi_cache_create -i neg -d data/KEGGDB.tsv -c db_nat

2. **Labeled compounds cache** (e.g., C13)::

    mimi_cache_create -i neg -l data/Clab.json -d data/KEGGDB.tsv -c db_13C

Parameters:
  - `-i neg`: Ionization mode (negative)
  - `-d data/KEGGDB.tsv`: Input database file
  - `-c db_nat`: Output cache file name
  - `-l data/Clab.json`: Optional labeled atoms configuration

Analyzing Samples
---------------

Basic analysis with a single cache::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat -s data/sample.asc -o results.tsv

Analysis with multiple caches::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat db_13C -s data/sample.asc -o results.tsv

Batch processing multiple samples::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat -s data/sample1.asc data/sample2.asc -o batch_results.tsv

Parameters:
  - `-p 1.0`: PPM tolerance for initial mass matching
  - `-vp 1.0`: PPM tolerance for isotope pattern verification
  - `-c db_nat`: Cache file(s) to use
  - `-s data/sample.asc`: Sample file(s) to analyze
  - `-o results.tsv`: Output file for results

PPM Threshold Effects
-------------------

The PPM (parts per million) threshold controls the precision of mass matching:

- **Lower PPM values (1.0)**: Higher precision, fewer but more confident matches
- **Higher PPM values (5.0)**: Lower precision, more matches but potentially more false positives
- **Verification PPM (-vp)**: Controls isotope pattern matching accuracy

Examples with different thresholds::

    # Tight thresholds
    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat -s data/sample.asc -o results_p1_vp1.tsv

    # Wider verification threshold
    mimi_mass_analysis -p 1.0 -vp 2.0 -c db_nat -s data/sample.asc -o results_p1_vp2.tsv

    # Matching thresholds
    mimi_mass_analysis -p 2.0 -vp 2.0 -c db_nat -s data/sample.asc -o results_p2_vp2.tsv

Database Extraction
-----------------

MIMI provides tools to extract compound information from common databases:

1. **From HMDB**::

    mimi_hmdb_extract -x metabolites.xml -o hmdb_compounds.tsv -l 100 -u 500

2. **From KEGG**::

    mimi_kegg_extract -l 100 -u 500 -o kegg_compounds.tsv

Parameters:
  - `-x metabolites.xml`: Input HMDB XML file
  - `-l 100`: Minimum molecular weight in Da
  - `-u 500`: Maximum molecular weight in Da
  - `-o hmdb_compounds.tsv`: Output TSV file

Inspecting Cache Files
--------------------

View cache contents for verification::

    mimi_cache_dump cache_file.pkl -n 10 -o cache_contents.tsv

Parameters:
  - `cache_file.pkl`: Input cache file
  - `-n 10`: Number of compounds to display
  - `-i 5`: Number of isotopes per compound to display
  - `-o cache_contents.tsv`: Output file (omit for stdout)

Interpreting Results
------------------

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

Tips for Best Results
-------------------

1. **Use appropriate PPM thresholds** for your instrument's resolution
2. **Create separate caches** for different isotope labeling experiments
3. **Process multiple samples** in batch for consistent analysis
4. **Compare results** from different PPM thresholds
5. **Verify matches** by examining isotope patterns 