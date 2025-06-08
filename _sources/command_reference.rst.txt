Command Reference
=================

This section provides detailed information about all command-line tools available in MIMI, including their purpose, when to use them, and what results to expect.

mimi_kegg_extract
-----------------

Extracts compound information from the [KEGG COMPOUND database](https://www.genome.jp/kegg/compound/) using its [REST API](https://www.kegg.jp/kegg/rest/keggapi.html). Can retrieve compounds within a specific molecular weight range or from a list of compound IDs.

.. code-block:: text

    $ mimi_kegg_extract --help
    usage: mimi_kegg_extract [-h] [-l MIN_MASS] [-u MAX_MASS] [-i COMPOUND_IDS] [-o OUTPUT] [-b BATCH_SIZE]

    Extract compound information from KEGG

    options:
    -h, --help            show this help message and exit
    -l MIN_MASS, --min-mass MIN_MASS
                            Lower bound of molecular weight in Da
    -u MAX_MASS, --max-mass MAX_MASS
                            Upper bound of molecular weight in Da
    -i COMPOUND_IDS, --input COMPOUND_IDS
                            Input TSV file containing KEGG compound IDs
    -o OUTPUT, --output OUTPUT
                            Output TSV file path (default: kegg_compounds.tsv)
    -b BATCH_SIZE, --batch-size BATCH_SIZE
                            Number of compounds to process in each batch (default: 5)

**Example**::

    # Extract specific compounds by ID
    $ mimi_kegg_extract -i compound_ids.tsv -o data/processed/kegg_compounds.tsv


    # Extract compounds between 40-1000 Da
    $ mimi_kegg_extract -l 40 -u 1000 -o data/processed/kegg_compounds_40_1000Da.tsv

    # Sort and remove duplicates from the KEGG compounds file
    $ { head -n 1 data/processed/kegg_compounds_40_1000Da.tsv; tail -n +2 data/processed/kegg_compounds_40_1000Da.tsv | sort -k2,2; } > data/processed/kegg_compounds_40_1000Da_sorted.tsv
    $ awk '!seen[$1]++' data/processed/kegg_compounds_40_1000Da_sorted.tsv > data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv


mimi_hmdb_extract
-----------------

Extracts metabolite information from the [Human Metabolome Database (HMDB)](https://hmdb.ca) and converts it to a TSV format compatible with MIMI. Requires a list of metabolites downloaded from [HMDB](https://hmdb.ca/downloads) in XML format. 

.. code-block:: text

    $ mimi_hmdb_extract --help
    usage: mimi_hmdb_extract [-h] -x XML [-l MIN_MASS] [-u MAX_MASS] [-o OUTPUT]

    Extract metabolite information from HMDB XML file

    options:
    -h, --help            show this help message and exit
    -x XML, --xml XML     Path to HMDB metabolites XML file
    -l MIN_MASS, --min-mass MIN_MASS
                            Lower bound of molecular weight in Da
    -u MAX_MASS, --max-mass MAX_MASS
                            Upper bound of molecular weight in Da
    -o OUTPUT, --output OUTPUT
                            Output TSV file path (default: metabolites.tsv)


**Example**::

    # Extract metabolites between 40-1000 Da
    $ mimi_hmdb_extract -x data/processed/hmdb_metabolites.xml -l 40 -u 1000 -o data/processed/hmdb_compounds_40_1000Da.tsv


***Input files:***

HMDB provides downloads for all metabolites contained in the database, as well as specific subsets (e.g. serum, saliva, etc.). Downloaded files should automatically acquire the file extension `.xml` and will look something like this:

.. code-block:: text

    <?xml version="1.0" encoding="UTF-8"?>
    <hmdb xmlns="http://www.hmdb.ca">
    <metabolite>
      <version>5.0</version>
      <creation_date>2005-11-16 15:48:42 UTC</creation_date>
      <update_date>2021-09-14 15:44:51 UTC</update_date>

      [ data on individual compounds follows ... ]

    </metabolite>
    </hmdb>

Note that the HMDB database version (5.0) and date of the last update (2021-09-14) are included at the top of this example file, ensuring that this information is easily available for citation purposes.


mimi_cache_create
-----------------

Creates precomputed cache files containing theoretical molecular masses and isotope patterns for compounds. Caching significantly speeds up mass comparisons, and the same cache files can be reused for any mass analysis involving the same database and isotope ratios.


.. code-block:: text

    $ mimi_cache_create  --help
    usage: mimi_cache_create [-h] [-l JSON] [-n CUTOFF] -d DBTSV [DBTSV ...] -i {pos,neg} -c DBBINARY

    Molecular Isotope Mass Identifier

    options:
    -h, --help            show this help message and exit
    -l JSON, --label JSON
                            Labeled atoms
    -n CUTOFF, --noise CUTOFF
                            Threshold for filtering molecular isotope variants with relative abundance below CUTOFF w.r.t. the monoisotopic mass (defaults to 1e-5)
    -d DBTSV [DBTSV ...], --dbfile DBTSV [DBTSV ...]
                            File(s) with list of compounds
    -i {pos,neg}, --ion {pos,neg}
                            Ionisation mode
    -c DBBINARY, --cache DBBINARY
                            Binary DB output file (if not specified, will use base name from JSON file)


**Example**::

    # Create natural abundance cache
    $ mimi_cache_create -i neg -d data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv -c outdir/nat

    # Create C13-95% labeled cache
    $ mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv -c outdir/C13_95


mimi_cache_dump
---------------

Dumps the contents of a MIMI cache file in human-readable TSV format. Useful for inspecting cache files and verifying their contents.


.. code-block:: text
    
    $ mimi_cache_dump --help
    usage: mimi_cache_dump [-h] [-n NUM_COMPOUNDS] [-i NUM_ISOTOPES] [-o OUTPUT] cache_file

    MIMI Cache Dump Tool

    positional arguments:
    cache_file            Input cache file (.pkl)

    options:
    -h, --help            show this help message and exit
    -n NUM_COMPOUNDS, --num-compounds NUM_COMPOUNDS
                            Number of compounds to output (default: all)
    -i NUM_ISOTOPES, --num-isotopes NUM_ISOTOPES
                            Number of isotopes per compound to output (default: all)
    -o OUTPUT, --output OUTPUT
                            Output file (default: stdout)


**Example**::

    # Dump first 5 compounds with 2 isotopes each
    $ mimi_cache_dump -n 5 -i 2 outdir/nat.pkl -o outdir/cache_contents.tsv


mimi_mass_analysis
------------------

Analyzes mass spectrometry data by comparing measured masses in sample peak lists against precomputed theoretical molecular masses stored in cache files.


.. code-block:: text
   
    $ mimi_mass_analysis --help
    usage: mimi_mass_analysis [-h] -p PPM -vp VPPM -c DBBINARY [DBBINARY ...] -s SAMPLE [SAMPLE ...] -o OUTPUT

    Molecular Isotope Mass Identifier

    options:
    -h, --help            show this help message and exit
    -p PPM, --ppm PPM     Parts per million for the mono isotopic mass of chemical formula
    -vp VPPM              Parts per million for verification of isotopes
    -c DBBINARY [DBBINARY ...], --cache DBBINARY [DBBINARY ...]
                            Binary DB input file(s)
    -s SAMPLE [SAMPLE ...], --sample SAMPLE [SAMPLE ...]
                            Input sample file
    -o OUTPUT, --output OUTPUT
                            Output file


**Example**::

    # Analyze single sample with natural abundance cache
    $ mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/nat -s data/processed/testdata1.asc -o outdir/results.tsv

    # Analyze multiple samples with multiple caches
    $ mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/nat outdir/C13_95 -s data/processed/testdata1.asc data/processed/testdata2.asc -o outdir/batch_results.tsv
                  
