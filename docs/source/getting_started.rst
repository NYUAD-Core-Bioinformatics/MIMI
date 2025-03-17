Getting Started
===============

Mass Spectrometry Tool
----------------------

Calculation of isotope labeled FT-ICR (fourier transform ion cyclotron resonance) mass spectrometry data 

Installation
-----------

MIMI can be installed using following methods:

Using conda
~~~~~~~~~~
Install from conda-forge channel::

    conda install -c conda-forge mimi

From source
~~~~~~~~~~
Clone the repository and install::

    git clone https://github.com/GunsalusPiano/mass_spectrometry_tool.git
    cd mass_spectrometry_tool
    pip install .


Requirements
~~~~~~~~~~~
MIMI requires the following Python packages:

* Python >= 3.11.11
* numpy
* pandas
* json5
* urllib3
* tqdm
* requests

These dependencies will be automatically installed when using pip or conda.

Usage
-----
MIMI provides five command-line tools:

1. Mass Analysis
~~~~~~~~~~~~~~
::

    mimi_mass_analysis [-h] -p PPM -vp VPPM -c DBBINARY [DBBINARY ...] -s SAMPLE [SAMPLE ...] -o OUTPUT

Options:
    -h, --help            Show this help message and exit
    -p PPM, --ppm PPM    Parts per million for the mono isotopic mass of chemical formula
    -vp VPPM             Parts per million for verification of isotopes
    -c DBBINARY, --cache DBBINARY [DBBINARY ...]
                         Binary DB input file(s)
    -s SAMPLE, --sample SAMPLE [SAMPLE ...]
                         Input sample file
    -o OUTPUT, --output OUTPUT
                         Output file

2. Cache Creation
~~~~~~~~~~~~~~~
::

    mimi_cache_create [-h] [-l JSON] -d DBTSV [DBTSV ...] -i {pos,neg} -c DBBINARY

Options:
    -h, --help            Show this help message and exit
    -l JSON, --label JSON
                         Labeled atoms
    -d DBTSV, --dbfile DBTSV [DBTSV ...]
                         File(s) with list of compounds
    -i {pos,neg}, --ion {pos,neg}
                         Ionisation mode
    -c DBBINARY, --cache DBBINARY
                         Binary DB output file

3. HMDB Extraction
~~~~~~~~~~~~~~~~
::

    mimi_hmdb_extract [-h] -x XML [-l MIN_MASS] [-u MAX_MASS] [-o OUTPUT]

Options:
    -h, --help            Show this help message and exit
    -x XML, --xml XML     Path to HMDB metabolites XML file
    -l MIN_MASS, --min-mass MIN_MASS
                         Lower bound of molecular weight in Da
    -u MAX_MASS, --max-mass MAX_MASS
                         Upper bound of molecular weight in Da
    -o OUTPUT, --output OUTPUT
                         Output TSV file path (default: metabolites.tsv)

4. KEGG Extraction
~~~~~~~~~~~~~~~~
::

    mimi_kegg_extract [-h] [-l MIN_MASS] [-u MAX_MASS] [-i COMPOUND_IDS] [-o OUTPUT]

Options:
    -h, --help            Show this help message and exit
    -l MIN_MASS, --min-mass MIN_MASS
                         Lower bound of molecular weight in Da
    -u MAX_MASS, --max-mass MAX_MASS
                         Upper bound of molecular weight in Da
    -i COMPOUND_IDS, --input COMPOUND_IDS
                         Input TSV file containing KEGG compound IDs
    -o OUTPUT, --output OUTPUT
                         Output TSV file path (default: kegg_compounds.tsv)

5. Cache Dump
~~~~~~~~~~~
::

    mimi_cache_dump [-h] [-n NUM_COMPOUNDS] [-i NUM_ISOTOPES] [-o OUTPUT] cache_file

Positional Arguments:
    cache_file            Input cache file (.pkl)

Options:
    -h, --help            Show this help message and exit
    -n NUM_COMPOUNDS, --num-compounds NUM_COMPOUNDS
                         Number of compounds to output (default: all)
    -i NUM_ISOTOPES, --num-isotopes NUM_ISOTOPES
                         Number of isotopes per compound to output (default: all)
    -o OUTPUT, --output OUTPUT
                         Output file (default: stdout)

Example
-------

First, create cache files for different isotope configurations:

::

   # Create cache for natural isotopes
   mimi_cache_create -i neg -d data/KEGGDB.tsv -c db_nat

   # Create cache for C13 spike-in
   mimi_cache_create -i neg -l data/Clab.json -d data/KEGGDB.tsv -c db_C13

Then analyze samples using multiple cache files simultaneously:

::

   # Analyze samples with natural isotopes and C13 spike-in (ppm=1.0, verification ppm=1.0)
   mimi_analysis -p 1.0 -vp 1.0 -c db_nat db_C13 -s data/sample1.asc -o results_with_spike.tsv

   # Process multiple samples
   mimi_analysis -p 1.0 -vp 1.0 -c db_nat db_C13 -s data/sample1.asc data/sample2.asc -o results_batch.tsv

Key Features
-----------

- **Multiple Cache Analysis**: Analyze samples against both natural isotopes and C13 spike-in simultaneously
- **Batch Sample Processing**: Process multiple sample files in a single run
- **Efficient Cache System**: Cache files are pre-computed once and can be reused
- **Intuitive Output**: Output column names derived from cache file names
