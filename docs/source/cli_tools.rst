MIMI Command Line Tools
========================

Overview
--------
MIMI (Molecular Isotope Mass Identifier) provides two main command-line tools:
- ``mimi_cache_create``: Creates binary database files for compound matching
- ``mimi_analysis``: Analyzes mass spectrometry data against the cached databases

Basic Concepts
---------------

Terms and Abbreviations
~~~~~~~~~~~~~~~~~~~~~~~~
- ``CF``: Chemical formula
- ``ID``: Index 
- ``neg``: Negative ionisation
- ``pos``: Positive ionisation
- ``zero``: Zero ionisation

Constants
~~~~~~~~~~
- ``Electron mass(e)``: 0.000548
- ``Proton mass(h)``: 1.007276467
- ``Clab + pos``: Mass of Labeled Carbon + Proton mass(h) 
- ``Clab + neg``: Mass of Labeled Carbon - Proton mass(h)

Command Reference
------------------

mimi_cache_create
~~~~~~~~~~~~~~~~~~
Creates binary cache files for compound matching.

Usage:
::

    mimi_cache_create -d DBTSV -c DBBINARY [-i {pos,neg,zero}] [-l JSON] [-g]

Required Arguments:
::

    -d DBTSV, --dbfile DBTSV
                         Input file with list of compounds
    -c DBBINARY, --cache DBBINARY
                         Output binary DB file

Optional Arguments:
::

    -h, --help            Show this help message and exit
    -i {pos,neg,zero}, --ion {pos,neg,zero}
                         Ionisation mode (default: zero)
    -l JSON, --label JSON
                         Labeled atoms configuration file
    -g, --debug          Enable debug output

mimi_analysis
~~~~~~~~~~~~~~
Analyzes mass spectrometry data using cached databases.

Usage:
::

    mimi_analysis -p PPM -vp VPPM -c DBBINARY [DBBINARY ...] -s SAMPLE [SAMPLE ...] [-o OUTPUT] [-g]

Required Arguments:
::

    -p PPM, --ppm PPM     Parts per million for mono isotopic mass matching
    -vp VPPM              Parts per million for isotope verification
    -c DBBINARY, --cache DBBINARY
                         Binary DB input file(s)
    -s SAMPLE, --sample SAMPLE
                         Input sample file(s)

Optional Arguments:
::

    -h, --help            Show this help message and exit
    -o OUTPUT, --output OUTPUT
                         Output file (default: prints to stdout)
    -g, --debug          Enable debug output

Workflow Examples
-----------------

Basic Workflow
~~~~~~~~~~~~~~~
1. Create cache files for both natural and labeled compounds:
::

    # Natural abundance cache
    mimi_cache_create -i neg -d data/KEGGDB.tsv -c db_nat

    # C13-labeled cache
    mimi_cache_create -i neg -l data/Clab.json -d data/KEGGDB.tsv -c db_13C

2. Analyze samples using the cache files:
::

    # Single analysis
    mimi_analysis -p 1.0 -vp 1.0 -c db_nat db_13C \
        -s data/testdata.asc \
        -o results.tsv

Analysis with Different PPM Thresholds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Fine-tune analysis using different PPM thresholds:

::

    # Tight thresholds
    mimi_analysis -p 1.0 -vp 1.0 -c db_nat -s data/testdata.asc -o results_p1_vp1.tsv

    # Wider verification threshold
    mimi_analysis -p 1.0 -vp 2.0 -c db_nat -s data/testdata.asc -o results_p1_vp2.tsv

    # Matching thresholds
    mimi_analysis -p 2.0 -vp 2.0 -c db_nat -s data/testdata.asc -o results_p2_vp2.tsv

PPM Threshold Effects:
~~~~~~~~~~~~~~~~~~~~~~~
- Lower PPM values (1.0): Higher precision in mass matching
- Higher PPM values (5.0): Wider mass matching window
- Verification PPM (-vp): Controls isotope pattern matching accuracy

Batch Processing
~~~~~~~~~~~~~~~~~
For analyzing multiple samples with multiple thresholds:

::

    # Create output directory
    mkdir -p analysis_results

    # Run analysis with PPM combinations
    for ppm in 1.0 2.0 5.0; do
        for vppm in 1.0 2.0 5.0; do
            mimi_analysis -p $ppm -vp $vppm \
                -c db_nat db_13C \
                -s data/testdata.asc \
                -o analysis_results/results_p${ppm}_vp${vppm}.tsv
        done
    done

Multiple Sample Analysis with Spike Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Analyze samples with both natural abundance and isotope spikes:

::

    # Create cache files
    mimi_cache_create -i neg -d data/KEGGDB.tsv -c db_nat
    mimi_cache_create -i neg -l data/Clab.json -d data/KEGGDB.tsv -c db_spike

    # Analyze samples with spike detection
    mimi_analysis -p 1.0 -vp 1.0 -c db_nat db_spike \
        -s data/sample1.asc data/sample2.asc \
        -o results_with_spike.tsv

Spike Detection
~~~~~~~~~~~~~~~~
When analyzing data with multiple cache files, MIMI performs spike detection:

- Natural abundance peaks are matched using the natural isotope cache (db_nat)
- Spike signals are detected using labeled isotope caches (db_spike)
- Common spike analysis scenarios:
  - C13 metabolic spikes
  - N15 enrichment spikes
  - Multiple spike types simultaneously
- Output includes columns for both natural and spike matches
- Relative intensities indicate spike incorporation rates

Input File Formats
-------------------

Compound Database (DBTSV)
~~~~~~~~~~~~~~~~~~~~~~~~~~
Tab-separated file containing compound information:
::

    CF              ID      Name
    C10H16N5O13P3   C19969  2-Hydroxy-dATP
    C21H28N7O14P2   C00003  NAD+
    C21H29N7O14P2   C21424  1,6-Dihydro-beta-NAD
    ...

Labeled Atoms Configuration (JSON)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
JSON file defining isotope properties:
::

    {
        "C": [
            {
                "periodic_number": 6,
                "element_symbol": "C",
                "nominal_mass": 13,
                "exact_mass": 13.00335484,
                "natural_abundance": 0.95,
                "highest_abundance": 0.95
            },
            {
                "periodic_number": 6,
                "element_symbol": "C",
                "nominal_mass": 12,
                "exact_mass": 12.000,
                "natural_abundance": 0.05,
                "highest_abundance": 0.95
            }
        ]
    }

Sample Data (ASC)
~~~~~~~~~~~~~~~~~~
ASCII format mass spectrometry data:
::

    43.16184    1089317    0.00003
    43.28766    1115802    0.00003
    43.28946    1226947    0.00003
    ...

Natural Isotope Abundances
---------------------------
Following are default atomic information(Builtin data sets/used while precomputing) which can be override with -l option

::

    {
        "H": [
                {
                    "periodic_number": 1,
                    "element_symbol": "H",
                    "nominal_mass": 1,
                    "exact_mass": 1.007825,
                    "natural_abundance": 0.999885,
                    "highest_abundance": 0.999885
                },
                {
                    "periodic_number": 1,
                    "element_symbol": "H",
                    "nominal_mass": 2,
                    "exact_mass": 2.014102,
                    "natural_abundance": 0.00115,
                    "highest_abundance": 0.999885
                }
        ],
        "B": [
                {
                    "periodic_number": 5,
                    "element_symbol": "B",
                    "nominal_mass": 11,
                    "exact_mass": 11.009305,
                    "natural_abundance": 0.801,
                    "highest_abundance": 0.801
                },
                {
                    "periodic_number": 5,
                    "element_symbol": "B",
                    "nominal_mass": 10,
                    "exact_mass": 10.012937,
                    "natural_abundance": 0.199,
                    "highest_abundance": 0.801
                }
        ],
        "C": [
                {
                    "periodic_number": 6,
                    "element_symbol": "C",
                    "nominal_mass": 12,
                    "exact_mass": 12.0,
                    "natural_abundance": 0.9893,
                    "highest_abundance": 0.9893
                },
                {
                    "periodic_number": 6,
                    "element_symbol": "C",
                    "nominal_mass": 13,
                    "exact_mass": 13.00335484,
                    "natural_abundance": 0.0107,
                    "highest_abundance": 0.9893
                }
        ],
        "N": [
                {
                    "periodic_number": 7,
                    "element_symbol": "N",
                    "nominal_mass": 14,
                    "exact_mass": 14.003074,
                    "natural_abundance": 0.99632,
                    "highest_abundance": 0.99632
                },
                {
                    "periodic_number": 7,
                    "element_symbol": "N",
                    "nominal_mass": 15,
                    "exact_mass": 15.0001089,
                    "natural_abundance": 0.00368,
                    "highest_abundance": 0.99632
                }
        ],
        "O": [
                {
                    "periodic_number": 8,
                    "element_symbol": "O",
                    "nominal_mass": 16,
                    "exact_mass": 15.994915,
                    "natural_abundance": 0.99757,
                    "highest_abundance": 0.99757
                },
                {
                    "periodic_number": 8,
                    "element_symbol": "O",
                    "nominal_mass": 17,
                    "exact_mass": 16.999132,
                    "natural_abundance": 0.00038,
                    "highest_abundance": 0.99757
                },
                {
                    "periodic_number": 8,
                    "element_symbol": "O",
                    "nominal_mass": 18,
                    "exact_mass": 17.99916,
                    "natural_abundance": 0.00205,
                    "highest_abundance": 0.99757
                }
        ],
        "F": [
                {
                    "periodic_number": 9,
                    "element_symbol": "F",
                    "nominal_mass": 19,
                    "exact_mass": 18.998403,
                    "natural_abundance": 1.0,
                    "highest_abundance": 1.0
                }
        ],
        "Mg": [
                {
                    "periodic_number": 12,
                    "element_symbol": "Mg",
                    "nominal_mass": 24,
                    "exact_mass": 23.985042,
                    "natural_abundance": 0.7899,
                    "highest_abundance": 0.7899
                },
                {
                    "periodic_number": 12,
                    "element_symbol": "Mg",
                    "nominal_mass": 25,
                    "exact_mass": 24.985837,
                    "natural_abundance": 0.1000,
                    "highest_abundance": 0.7899
                },
                {
                    "periodic_number": 12,
                    "element_symbol": "Mg",
                    "nominal_mass": 26,
                    "exact_mass": 25.982593,
                    "natural_abundance": 0.1000,
                    "highest_abundance": 0.1101
                }
        ],
        "Si": [
                {
                    "periodic_number": 14,
                    "element_symbol": "Si",
                    "nominal_mass": 28,
                    "exact_mass": 27.976927,
                    "natural_abundance": 0.92297,
                    "highest_abundance": 0.92297
                },
                {
                    "periodic_number": 14,
                    "element_symbol": "Si",
                    "nominal_mass": 29,
                    "exact_mass": 28.976495,
                    "natural_abundance": 0.046832,
                    "highest_abundance": 0.92297
                },
                {
                    "periodic_number": 14,
                    "element_symbol": "Si",
                    "nominal_mass": 30,
                    "exact_mass": 28.973770,
                    "natural_abundance": 0.030872,
                    "highest_abundance": 0.92297
                }
        ],
        "P": [
                {
                    "periodic_number": 15,
                    "element_symbol": "P",
                    "nominal_mass": 31,
                    "exact_mass": 30.973762,
                    "natural_abundance": 1.0,
                    "highest_abundance": 1.0
                }
        ],
        "S": [
                {
                    "periodic_number": 16,
                    "element_symbol": "S",
                    "nominal_mass": 32,
                    "exact_mass": 31.972071,
                    "natural_abundance": 0.9493,
                    "highest_abundance": 0.9493
                },
                {
                    "periodic_number": 16,
                    "element_symbol": "S",
                    "nominal_mass": 34,
                    "exact_mass": 33.967867,
                    "natural_abundance": 0.0429,
                    "highest_abundance": 0.9493
                },
                {
                    "periodic_number": 16,
                    "element_symbol": "S",
                    "nominal_mass": 33,
                    "exact_mass": 32.971458,
                    "natural_abundance": 0.0076,
                    "highest_abundance": 0.9493
                },
                {
                    "periodic_number": 16,
                    "element_symbol": "S",
                    "nominal_mass": 36,
                    "exact_mass": 35.967081,
                    "natural_abundance": 0.0002,
                    "highest_abundance": 0.9493
                }
        ],
        "Cl": [
                {
                    "periodic_number": 17,
                    "element_symbol": "Cl",
                    "nominal_mass": 35,
                    "exact_mass": 34.968853,
                    "natural_abundance": 0.7578,
                    "highest_abundance": 0.7578
                },
                {
                    "periodic_number": 17,
                    "element_symbol": "Cl",
                    "nominal_mass": 37,
                    "exact_mass": 36.965903,
                    "natural_abundance": 0.2422,
                    "highest_abundance": 0.7578
                }
        ],
        "K": [
                {
                    "periodic_number": 18,
                    "element_symbol": "K",
                    "nominal_mass": 39,
                    "exact_mass": 38.963707,
                    "natural_abundance": 0.932581,
                    "highest_abundance": 0.932581
                },
                {
                    "periodic_number": 18,
                    "element_symbol": "K",
                    "nominal_mass": 41,
                    "exact_mass": 40.961826,
                    "natural_abundance": 0.067302,
                    "highest_abundance": 0.932581
                },
                {
                    "periodic_number": 18,
                    "element_symbol": "K",
                    "nominal_mass": 40,
                    "exact_mass": 39.963707,
                    "natural_abundance": 0.000117,
                    "highest_abundance": 0.932581
                }
        ],
        "Ca": [
                {
                    "periodic_number": 20,
                    "element_symbol": "Ca",
                    "nominal_mass": 40,
                    "exact_mass": 39.96259086,
                    "natural_abundance": 0.96941,
                    "highest_abundance": 0.96941
                }
        ],
        "Mn": [
                {
                    "periodic_number": 25,
                    "element_symbol": "Mn",
                    "nominal_mass": 25,
                    "exact_mass": 54.93805,
                    "natural_abundance": 1.0,
                    "highest_abundance": 1.0
                }
        ],
        "Fe": [
                {
                    "periodic_number": 26,
                    "element_symbol": "Fe",
                    "nominal_mass": 56,
                    "exact_mass": 55.93493633,
                    "natural_abundance": 0.91754,
                    "highest_abundance": 0.91754
                },
                {
                    "periodic_number": 26,
                    "element_symbol": "Fe",
                    "nominal_mass": 54,
                    "exact_mass": 53.939615,
                    "natural_abundance": 0.05845,
                    "highest_abundance": 0.91754
                }
        ],
        "Co": [
                {
                    "periodic_number": 27,
                    "element_symbol": "Co",
                    "nominal_mass": 59,
                    "exact_mass": 58.933200,
                    "natural_abundance": 1.0,
                    "highest_abundance": 1.0
                }
        ],
        "Zn": [
                {
                    "periodic_number": 30,
                    "element_symbol": "Zn",
                    "nominal_mass": 64,
                    "exact_mass": 63.929147,
                    "natural_abundance": 0.4863,
                    "highest_abundance": 0.4863
                },
                {
                    "periodic_number": 30,
                    "element_symbol": "Zn",
                    "nominal_mass": 66,
                    "exact_mass": 65.926037,
                    "natural_abundance": 0.2790,
                    "highest_abundance": 0.4863
                },
                {
                    "periodic_number": 30,
                    "element_symbol": "Zn",
                    "nominal_mass": 68,
                    "exact_mass": 67.924848,
                    "natural_abundance": 0.1875,
                    "highest_abundance": 0.4863
                },
                {
                    "periodic_number": 30,
                    "element_symbol": "Zn",
                    "nominal_mass": 67,
                    "exact_mass": 66.927131,
                    "natural_abundance": 0.0410,
                    "highest_abundance": 0.4863
                },
                {
                    "periodic_number": 30,
                    "element_symbol": "Zn",
                    "nominal_mass": 70,
                    "exact_mass": 69.925325,
                    "natural_abundance": 0.0062,
                    "highest_abundance": 0.4863
                }
        ],
        "As": [
                {
                    "periodic_number": 33,
                    "element_symbol": "As",
                    "nominal_mass": 75,
                    "exact_mass": 74.92159457,
                    "natural_abundance": 1.0,
                    "highest_abundance": 1.0
                }
        ],
        "Se": [
                {
                    "periodic_number": 34,
                    "element_symbol": "Se",
                    "nominal_mass": 80,
                    "exact_mass": 79.916522,
                    "natural_abundance": 0.4961,
                    "highest_abundance": 0.4961
                },
                {
                    "periodic_number": 34,
                    "element_symbol": "Se",
                    "nominal_mass": 78,
                    "exact_mass": 77.917310,
                    "natural_abundance": 0.2377,
                    "highest_abundance": 0.4961
                },
                {
                    "periodic_number": 34,
                    "element_symbol": "Se",
                    "nominal_mass": 82,
                    "exact_mass": 81.916700,
                    "natural_abundance": 0.0873,
                    "highest_abundance": 0.4961
                },
                {
                    "periodic_number": 34,
                    "element_symbol": "Se",
                    "nominal_mass": 76,
                    "exact_mass": 75.919214,
                    "natural_abundance": 0.0937,
                    "highest_abundance": 0.4961
                },
                {
                    "periodic_number": 34,
                    "element_symbol": "Se",
                    "nominal_mass": 77,
                    "exact_mass": 76.919915,
                    "natural_abundance": 0.0763,
                    "highest_abundance": 0.4961
                },
                {
                    "periodic_number": 34,
                    "element_symbol": "Se",
                    "nominal_mass": 74,
                    "exact_mass": 73.922477,
                    "natural_abundance": 0.0089,
                    "highest_abundance": 0.4961
                }
        ],
        "Br": [
                {
                    "periodic_number": 35,
                    "element_symbol": "Br",
                    "nominal_mass": 79,
                    "exact_mass": 79.918338,
                    "natural_abundance": 0.5069,
                    "highest_abundance": 0.5069
                },
                {
                    "periodic_number": 35,
                    "element_symbol": "Br",
                    "nominal_mass": 81,
                    "exact_mass": 80.916291,
                    "natural_abundance": 0.4931,
                    "highest_abundance": 0.5069
                }
        ],
        "Mo": [
                {
                    "periodic_number": 42,
                    "element_symbol": "Mo",
                    "nominal_mass": 98,
                    "exact_mass": 97.905408,
                    "natural_abundance": 0.2413,
                    "highest_abundance": 0.2413
                },
                {
                    "periodic_number": 42,
                    "element_symbol": "Mo",
                    "nominal_mass": 96,
                    "exact_mass": 95.904679,
                    "natural_abundance": 0.1668,
                    "highest_abundance": 0.2413
                },
                {
                    "periodic_number": 42,
                    "element_symbol": "Mo",
                    "nominal_mass": 95,
                    "exact_mass": 94.905841,
                    "natural_abundance": 0.1592,
                    "highest_abundance": 0.2413
                },
                {
                    "periodic_number": 42,
                    "element_symbol": "Mo",
                    "nominal_mass": 92,
                    "exact_mass": 91.906810,
                    "natural_abundance": 0.1484,
                    "highest_abundance": 0.2413
                },
                {
                    "periodic_number": 42,
                    "element_symbol": "Mo",
                    "nominal_mass": 97,
                    "exact_mass": 96.906021,
                    "natural_abundance": 0.0955,
                    "highest_abundance": 0.2413
                },
                {
                    "periodic_number": 42,
                    "element_symbol": "Mo",
                    "nominal_mass": 94,
                    "exact_mass": 93.905088,
                    "natural_abundance": 0.0925,
                    "highest_abundance": 0.2413
                }
        ],
        "Sn": [
                {
                    "periodic_number": 50,
                    "element_symbol": "Sn",
                    "nominal_mass": 120,
                    "exact_mass": 119.9022016,
                    "natural_abundance": 0.3258,
                    "highest_abundance": 0.3258
                }
        ],
        "Te": [
                {
                    "periodic_number": 52,
                    "element_symbol": "Te",
                    "nominal_mass": 130,
                    "exact_mass": 129.906223,
                    "natural_abundance": 0.34,
                    "highest_abundance": 0.34
                }
        ],
        "I": [
                {
                    "periodic_number": 53,
                    "element_symbol": "I",
                    "nominal_mass": 127,
                    "exact_mass": 126.9044719,
                    "natural_abundance": 1.0,
                    "highest_abundance": 1.0
                }
        ],
        "Pt": [
                {
                    "periodic_number": 78,
                    "element_symbol": "Pt",
                    "nominal_mass": 195,
                    "exact_mass": 194.964774,
                    "natural_abundance": 33.832,
                    "highest_abundance": 33.832
                }
        ],
        "Au": [
                {
                    "periodic_number": 79,
                    "element_symbol": "Au",
                    "nominal_mass": 197,
                    "exact_mass": 196.9665688,
                    "natural_abundance": 1.0,
                    "highest_abundance": 1.0
                }
        ],
        "Hg": [
                {
                    "periodic_number": 80,
                    "element_symbol": "Hg",
                    "nominal_mass": 202,
                    "exact_mass": 201.970626,
                    "natural_abundance": 0.2986,
                    "highest_abundance": 0.2986
                },
                {
                    "periodic_number": 80,
                    "element_symbol": "Hg",
                    "nominal_mass": 200,
                    "exact_mass": 199.968309,
                    "natural_abundance": 0.2310,
                    "highest_abundance": 0.2986
                },
                {
                    "periodic_number": 80,
                    "element_symbol": "Hg",
                    "nominal_mass": 199,
                    "exact_mass": 198.968262,
                    "natural_abundance": 0.1687,
                    "highest_abundance": 0.2986
                },
                {
                    "periodic_number": 80,
                    "element_symbol": "Hg",
                    "nominal_mass": 201,
                    "exact_mass": 200.970285,
                    "natural_abundance": 0.1318,
                    "highest_abundance": 0.2986
                },
                {
                    "periodic_number": 80,
                    "element_symbol": "Hg",
                    "nominal_mass": 198,
                    "exact_mass": 197.966752,
                    "natural_abundance": 0.0997,
                    "highest_abundance": 0.2986
                },
                {
                    "periodic_number": 80,
                    "element_symbol": "Hg",
                    "nominal_mass": 204,
                    "exact_mass": 203.973476,
                    "natural_abundance": 0.0687,
                    "highest_abundance": 0.2986
                },
                {
                    "periodic_number": 80,
                    "element_symbol": "Hg",
                    "nominal_mass": 196,
                    "exact_mass": 195.965815,
                    "natural_abundance": 0.0015,
                    "highest_abundance": 0.2986
                }
        ],
        "Bi": [
                {
                    "periodic_number": 83,
                    "element_symbol": "Bi",
                    "nominal_mass": 209,
                    "exact_mass": 208.980383,
                    "natural_abundance": 1.0,
                    "highest_abundance": 1.0
                }
        ],
        "Ge":[
                {
                "periodic_number": 32,
                "element_symbol": "Ge",
                "nominal_mass": 74,
                "exact_mass": 73.921177761,
                "natural_abundance": 0.3650,
                "highest_abundance": 0.3650
                
                }
        ],
        "Gb":[
                {
                "periodic_number": 32,
                "element_symbol": "Gb",
                "nominal_mass": 74,
                "exact_mass": 73.921177761,
                "natural_abundance": 0.3650,
                "highest_abundance": 0.3650
                
                }
        ],
        "Gd":[
                {
                "periodic_number": 32,
                "element_symbol": "Gd",
                "nominal_mass": 74,
                "exact_mass": 73.921177761,
                "natural_abundance": 0.3650,
                "highest_abundance": 0.3650
                
                }
        ],
        "Al":[
                {
                "periodic_number": 32,
                "element_symbol": "Al",
                "nominal_mass": 74,
                "exact_mass": 73.921177761,
                "natural_abundance": 0.3650,
                "highest_abundance": 0.3650
                
                }
        ]
    }