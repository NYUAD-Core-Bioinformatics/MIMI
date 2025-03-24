Command Reference
=================

This section provides detailed information about all command-line tools available in MIMI.


mimi_hmdb_extract
-----------------
This tool extracts metabolite information from the Human Metabolome Database (HMDB)
XML file and converts it to a TSV format that can be used with MIMI. It can filter
metabolites by molecular weight range and validates chemical formulas to ensure
compatibility with MIMI's formula parser.

::

    mimi_hmdb_extract --help
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

mimi_kegg_extract
-----------------

This tool extracts compound information from the KEGG database using its REST API.
It can retrieve compounds within a specific molecular weight range or from a list
of compound IDs. The tool handles KEGG's 10,000 result limit by breaking large
mass ranges into smaller chunks.


::

    mimi_kegg_extract --help
    usage: mimi_kegg_extract [-h] [-l MIN_MASS] [-u MAX_MASS] [-i COMPOUND_IDS]
                            [-o OUTPUT]

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







mimi_cache_create
-----------------

This tool creates precomputed cache files containing molecular mass data and isotope
patterns for compounds. These cache files significantly speed up analysis by avoiding
repeated calculations. You can create different cache files for different isotope
configurations (natural abundance, C13-labeled, etc.).

::

    mimi_cache_create --help
    usage: mimi_cache_create [-h] [-l JSON] -d DBTSV [DBTSV ...] -i {pos,neg} -c
                            DBBINARY

    Molecular Isotope Mass Identifier

    options:
      -h, --help            show this help message and exit
      -l JSON, --label JSON
                            Labeled atoms
      -d DBTSV [DBTSV ...], --dbfile DBTSV [DBTSV ...]
                            File(s) with list of compounds
      -i {pos,neg}, --ion {pos,neg}
                            Ionisation mode
      -c DBBINARY, --cache DBBINARY
                            Binary DB output file





mimi_cache_dump
---------------
This tool dumps the contents of a MIMI cache file to a human-readable TSV format.
It's useful for inspecting cache files, verifying their contents, and understanding
the isotope patterns being used for analysis. The output includes compound information,
chemical formulas with nominal masses, and isotope variant details. 

::

  mimi_cache_dump --help
  usage: mimi_cache_dump [-h] [-n NUM_COMPOUNDS] [-i NUM_ISOTOPES] [-o OUTPUT]
                        cache_file

  MIMI Cache Dump Tool

  positional arguments:
    cache_file            Input cache file (.pkl)

  options:
    -h, --help            show this help message and exit
    -n NUM_COMPOUNDS, --num-compounds NUM_COMPOUNDS
                          Number of compounds to output (default: all)
    -i NUM_ISOTOPES, --num-isotopes NUM_ISOTOPES
                          Number of isotopes per compound to output (default:
                          all)
    -o OUTPUT, --output OUTPUT
                          Output file (default: stdout)



mimi_mass_analysis
------------------
This tool analyzes mass spectrometry data by comparing sample masses against precomputed
molecular masses stored in cache files. It can process multiple samples against multiple
cache files simultaneously, allowing for efficient batch processing and comparison of
different isotope configurations.

::

    mmimi_mass_analysis --help
    usage: mimi_mass_analysis [-h] -p PPM -vp VPPM -c DBBINARY [DBBINARY ...] -s
                              SAMPLE [SAMPLE ...] -o OUTPUT

    Molecular Isotope Mass Identifier

    options:
      -h, --help            show this help message and exit
      -p PPM, --ppm PPM     Parts per million for the mono isotopic mass of
                            chemical formula
      -vp VPPM              Parts per million for verification of isotopes
      -c DBBINARY [DBBINARY ...], --cache DBBINARY [DBBINARY ...]
                            Binary DB input file(s)
      -s SAMPLE [SAMPLE ...], --sample SAMPLE [SAMPLE ...]
                            Input sample file
      -o OUTPUT, --output OUTPUT
                            Output file
                  