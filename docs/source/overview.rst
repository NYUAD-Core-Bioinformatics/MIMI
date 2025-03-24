Overview
===============

About
-----
mimi, developed by `CGSB Lab <https://nyuad.nyu.edu/en/research/faculty-labs-and-projects/nyuad-cgsb.html>`_
at `New York University Abu Dhabi <http://nyuad.nyu.edu/>`_, serves as a Mass Spectrometric data analysis tool specifically
designed for processing isotope-labeled FT-ICR (Fourier transform ion cyclotron resonance)
mass spectrometry data.

Features
--------
- Analysis of FT-ICR mass spectrometry data
- Support for isotope-labeled samples
- Multiple ionization modes (positive, negative)
- Precalculated molecular mass database support
- Parts per million (PPM) based mass matching
- Isotopic pattern analysis
- Batch processing capabilities

Installation
-----------
See :doc:`getting_started` for installation instructions and basic usage.

Usage
-----
mimi provides command-line tools for:

1. Creating cache files for molecular databases::

    mimi_cache_create -i [pos/neg] -d [database_files] -c [cache_file] [-l [label_file]] [-g]

2. Analyzing mass spectrometry data::

    mimi_mass_analysis -p [ppm] -vp [verification_ppm] -c [cache_files] -s [sample_files] -o [output_file] [-g]

3. Extracting HMDB metabolites::

    mimi_hmdb_extract -x [xml_file] -o [output_file] [-l [min_mass]] [-u [max_mass]]

4. Extracting KEGG compounds::

    mimi_kegg_extract -o [output_file] (-l [min_mass] -u [max_mass] | -i [compound_ids])

5. Dumping cache contents::

    mimi_cache_dump [cache_file] [-n [num_compounds]] [-i [num_isotopes]] [-o [output_file]]

Arguments:
^^^^^^^^^

Cache Creation:
    -i, --ion            Ionization mode (pos/neg)
    -d, --dbfile         Input database file(s)
    -c, --cache          Output cache file
    -l, --label         Optional labeled atoms file
    -g, --debug         Enable debug output

Mass Analysis:
    -p, --ppm           Parts per million tolerance
    -vp                 Verification PPM tolerance
    -c, --cache         Cache file(s) to use
    -s, --sample        Sample file(s) to analyze
    -o, --output        Output file path
    -g, --debug         Enable debug output

HMDB Extraction:
    -x, --xml           Input HMDB XML file
    -l, --min-mass      Lower bound of molecular weight in Da
    -u, --max-mass      Upper bound of molecular weight in Da
    -o, --output        Output TSV file path

KEGG Extraction:
    -l, --min-mass      Lower bound of molecular weight in Da
    -u, --max-mass      Upper bound of molecular weight in Da
    -i, --input         Input TSV file with KEGG compound IDs
    -o, --output        Output TSV file path

Cache Dump:
    cache_file          Input cache file (.pkl)
    -n, --num-compounds Number of compounds to output
    -i, --num-isotopes  Number of isotopes per compound
    -o, --output        Output file (default: stdout)

License
-------
mimi is available under the MIT License.
See :doc:`license` for more information.

Report Issues
------------
Please use `GitHub Issues <https://github.com/NYUAD-Core-Bioinformatics/MIMI/issues>`_
to report bugs or request help using mimi.

Contributing
-----------
Contributions are welcome! Please feel free to submit a Pull Request.
