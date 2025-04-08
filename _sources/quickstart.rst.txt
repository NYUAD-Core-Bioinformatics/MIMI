Quick Start Guide
=================

This guide will help you get started with MIMI quickly for analyzing mass spectrometry data.

Installation
------------
MIMI can be installed using one of the following methods:

Using conda::

    conda install -c conda-forge mimi

Or install from source::

    git clone https://github.com/NYUAD-Core-Bioinformatics/MIMI.git
    cd MIMI
    pip install .

Basic Workflow
--------------

MIMI follows a three-step workflow:

1. **Extract compounds** from databases (optional)
2. **Create cache files** for your compounds
3. **Analyze samples** using the cache files

Step 1: Extract Compounds
-------------------------

You can extract compounds from KEGG or HMDB databases, or use your own compound list.

From KEGG database::

    mimi_kegg_extract -l 100 -u 500 -o data/processed/kegg_compounds.tsv

From HMDB database::

    mimi_hmdb_extract -x data/processed/hmdb_metabolites.xml -o data/processed/hmdb_compounds.tsv

Step 2: Create Cache Files
--------------------------

Create cache files for your compound databases. You can create multiple caches for different isotope configurations.

For natural abundance::

    mimi_cache_create -i neg -d data/processed/kegg_compounds.tsv -c outdir/db_nat

For C13-labeled compounds::

    mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/kegg_compounds.tsv -c outdir/db_C13

Step 3: Analyze Samples
-----------------------

Analyze your mass spectrometry data using the cache files::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/db_nat outdir/db_C13 -s data/processed/testdata1.asc -o outdir/results.tsv

Parameters explained:
  - `-p 1.0`: PPM tolerance for initial mass matching
  - `-vp 1.0`: PPM tolerance for isotope pattern verification
  - `-c outdir/db_nat outdir/db_C13`: Cache files to use (can specify multiple)
  - `-s data/processed/testdata1.asc`: Sample file to analyze
  - `-o outdir/results.tsv`: Output file for results

Complete Example
----------------

Here's a complete workflow example:

1. Extract compounds from KEGG within a specific mass range::

    mimi_kegg_extract -l 100 -u 500 -o data/processed/kegg_compounds.tsv

2. Create caches for both natural and labeled compounds::

    # Natural abundance cache
    mimi_cache_create -i neg -d data/processed/kegg_compounds.tsv -c outdir/db_nat

    # C13-labeled cache
    mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/kegg_compounds.tsv -c outdir/db_C13

3. Analyze a sample using both caches simultaneously::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/db_nat outdir/db_C13 -s data/processed/testdata1.asc -o outdir/results.tsv

4. Inspect cache contents for verification::

    mimi_cache_dump outdir/db_nat.pkl -n 5 -o outdir/cache_contents.tsv

Advanced Usage
---------------

Batch processing multiple samples::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/db_nat -s data/processed/testdata1.asc data/processed/testdata2.asc -o outdir/batch_results.tsv

Testing different PPM thresholds::

    # Tight threshold
    mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/db_nat -s data/processed/testdata1.asc -o outdir/results_p1_vp1.tsv
    
    # Medium threshold
    mimi_mass_analysis -p 2.0 -vp 2.0 -c outdir/db_nat -s data/processed/testdata1.asc -o outdir/results_p2_vp2.tsv
    
    # Wide threshold
    mimi_mass_analysis -p 5.0 -vp 5.0 -c outdir/db_nat -s data/processed/testdata1.asc -o outdir/results_p5_vp5.tsv

Debugging cache creation::

    mimi_cache_create -i neg -d data/processed/kegg_compounds.tsv -c outdir/db_nat 