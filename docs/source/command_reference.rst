Command Reference
=================

This section provides detailed information about all command-line tools available in MIMI, including their purpose, when to use them, and what results to expect.

HMDB Database
-------------

The Human Metabolome Database (HMDB) is a comprehensive resource containing detailed information about metabolites found in the human body. MIMI provides tools to work with HMDB data, particularly for extracting and processing metabolite information.

Downloading HMDB Data
~~~~~~~~~~~~~~~~~~~~~

1. Visit the HMDB downloads page: https://hmdb.ca/downloads
2. Download the complete metabolites XML file (named "hmdb_metabolites.xml")
3. This file contains detailed information about each metabolite, including:

   - Chemical formulas
   - Names and synonyms
   - Identifiers (HMDB ID, InChI, SMILES)
   - Molecular weights
   - Other chemical properties

Extracting Metabolites
~~~~~~~~~~~~~~~~~~~~~~

The ``mimi_hmdb_extract`` command processes the HMDB XML file to extract relevant metabolite information and save it in a tab-separated format.

mimi_hmdb_extract
-----------------

Purpose: Extracts metabolite information from the Human Metabolome Database (HMDB) XML file and converts it to a TSV format compatible with MIMI.

Key Features:

- Human-specific metabolite database
- Requires downloading complete HMDB XML file
- Includes detailed metabolite information
- Validates chemical formulas
- Filters by molecular weight range

When to use:

- Analyzing human samples
- Studying human metabolism
- Need detailed metabolite information
- Working with clinical samples

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


Expected Output:
- TSV file with columns: ID, Name, Formula, Mass
- Only includes metabolites within specified mass range
- Validated chemical formulas
- Human-specific metabolites

Example::

    # Extract metabolites between 100-500 Da
    $ mimi_hmdb_extract -x hmdb_metabolites.xml -l 100 -u 500 -o hmdb_compounds.tsv

mimi_kegg_extract
-----------------

Purpose: Extracts compound information from the KEGG database using its REST API. Can retrieve compounds within a specific molecular weight range or from a list of compound IDs.

Key Features:

- Broad compound coverage
- Uses KEGG REST API
- Includes pathway information
- Can extract by mass range or specific IDs
- Handles KEGG's 10,000 result limit

When to use:

- Analyzing general biological samples
- Need broad compound coverage
- Studying metabolic pathways
- Working with non-human samples

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

Expected Output:

- TSV file with columns: ID, Name, Formula, Mass
- Compounds within specified mass range
- Pathway information when available
- Broad coverage of biological compounds

Examples::

    # Extract compounds between 100-500 Da
    $ mimi_kegg_extract -l 100 -u 500 -o kegg_compounds.tsv

    # Extract specific compounds by ID
    $ mimi_kegg_extract -i compound_ids.tsv -o kegg_compounds.tsv

mimi_cache_create
-----------------

Purpose: Creates precomputed cache files containing molecular mass data and isotope patterns for compounds. These cache files significantly speed up analysis by avoiding repeated calculations.

When to use:
- After updating your compound database
- Switching between different isotope configurations
- Starting a new analysis project
- Need to optimize analysis speed

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

Expected Output:

- Binary cache file (.pkl)
- Precomputed masses for all compounds
- Isotope patterns (natural or labeled)
- Optimized for fast searching

Examples::

    # Create natural abundance cache
    $ mimi_cache_create -i neg -d data/processed/KEGGDB.tsv -c db_nat

    # Create C13-labeled cache
    $ mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/KEGGDB.tsv -c db_13C

mimi_cache_dump
---------------

Purpose: Dumps the contents of a MIMI cache file to a human-readable TSV format. Useful for inspecting cache files and verifying their contents.

When to use:

- Debugging analysis issues
- Checking compound coverage
- Verifying isotope patterns
- Understanding cache structure

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


Expected Output:

- Cache metadata (creation date, version)
- Creation parameters
- Compound information:

  - ID and name
  - Chemical formula
  - Mass and relative abundance
  - Isotope variants with their masses and abundances

Example::

    # Dump first 5 compounds with 2 isotopes each
    $ mimi_cache_dump -n 5 -i 2 outdir/db_nat.pkl -o cache_contents.tsv

mimi_mass_analysis
------------------

Purpose: Analyzes mass spectrometry data by comparing sample masses against precomputed molecular masses stored in cache files.

When to use:

- After creating/updating caches
- Processing new samples
- Comparing different conditions
- Validating results

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

Expected Output:

- TSV file with columns:
  - CF: Chemical formula of the matched compound
  - ID: Compound identifier from the original database
  - Name: Compound name
  - C: Number of carbon atoms
  - H: Number of hydrogen atoms
  - N: Number of nitrogen atoms
  - O: Number of oxygen atoms
  - P: Number of phosphorus atoms
  - S: Number of sulfur atoms
  - db_mass_nat: Calculated mass for natural abundance(User specified)
  - db_mass_C13: Calculated mass for C13-labeled (User specified)
  - mass_measured: Observed mass in the sample
  - error_ppm: Parts per million difference between calculated and observed mass
  - intensity: Signal intensity in the sample
  - iso_count: Number of isotopes detected

Examples::

    # Analyze single sample with natural abundance cache
    $ mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat -s sample.asc -o results.tsv

    # Analyze multiple samples with multiple caches
    $ mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat db_13C -s sample1.asc sample2.asc -o batch_results.tsv
                  