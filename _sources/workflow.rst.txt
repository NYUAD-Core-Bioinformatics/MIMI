Usage Guide
===========

MIMI is a tool that identifies small molecules present in mass spectrometry datasets by matching observed peaks against theoretical masses of known compounds and and verifies the assigments using fine-structure isotope patterns.

.. _installation:

Installation
------------

MIMI can be installed using the Conda package manager, which is the recommended method as it handles all dependencies automatically::

    $ conda install -c conda-forge mimi

Alternatively, you can install from source if you need the latest development version::

    $ git clone https://github.com/NYUAD-Core-Bioinformatics/MIMI.git
    $ cd MIMI
    $ pip install .

MIMI requires Python 3.11.11 or above.

Workflow Overview
-----------------

A full MIMI analysis involves three steps:


1. Database Preparation
~~~~~~~~~~~~~~~~~~~~~~~~

**Choose a reference compound database and prepare a database file for input to MIMI.**

Prepare an input file in TSV format containing at least three column headers: CF (chemical formula), ID (compound ID), and Name (compound name)

Select from KEGG, HMDB, or other publicly available sources, or create a custom database with specific compounds of interest

- For KEGG and HMDB, use a MIMI helper script to extract compounds by ID or filtered by mass range
- For custom metabolite lists, use the commandline tool provided here to generate pseudo-IDs for compounds with no IDs

For details, jump to: 
:ref:`database-preparation`, :ref:`database-sources`, :ref:`mass-range-filtering`, :ref:`database-preparation-example`


2. Cache Creation
~~~~~~~~~~~~~~~~~~

**Generate precomputed molecular masses and fine-structure isotope patterns against reference compounds.**

* Cache creation is essential for MIMI analysis and improves run time performance
* A separate cache is needed for each combination of database and atomic isotope ratios (natural abundance or labeled)
* Cache contents can be inspected using `mimi_cache_dump` to ensure everything was processed correctly

For details, jump to: 
:ref:`step2-cache-creation`, :ref:`ppm-thresholds`, :ref:`isotope-configuration`, :ref:`verify-cache`


3. Sample Analysis
~~~~~~~~~~~~~~~~~~~

**Compare MS data against precomputed molecular masses of reference compounds with natural or non-natural atomic isotope ratios.**

- Analyze UHR-FT-ICR peak lists with measured mass, intensity, and resolution
- Find peak matches for monoisotopic mass and molecular variants for fine-structure isotope patterns
- Analyze multiple cache files to identify metabolites with different isotope abundances
- Analyze multiple sample files to compare results across replicates, time series, or treatment groups
- Generate a results file with detailed information about all matched compounds, including computed vs. observed monoisotopic mass and ppm erros and counts of minor molecular isotope variants detected 

In addition to these basic functions, MIMI also provides script templates that enable users to:

- Explore the effect of different error thresholds for both mass matching (-p) and isotope fine-structure pattern verification (-vp)
- Plot the number of metabolites and molecular variants identified using different error thresholds

For details, jump to: 
:ref:`step3-sample-analysis`, :ref:`input-file-format`, :ref:`batch-processing`, :ref:`results-format`, :ref:`comprehensive-analysis-runs`


.. _database-preparation:

Step1: Database Preparation
---------------------------

MIMI provides flexible options for preparing a compound database and includes helper scripts to extract data from online databases (KEGG or HMDB) or to create a custom database file. The choice depends on your research needs.

.. _database-sources:

Database Sources
~~~~~~~~~~~~~~~~

1. **KEGG Database**: Best for general biological samples

  The `Kyoto Encyclopedia of Genes and Genomes (KEGG) <https://hmdb.ca/>`_ is an online compendium of molecular information relevant to living systems, including reactions, pathways, orthologs, diseases, and drugs. Advantages:

  - Comprehensive compound coverage
  - Integrated pathway information
  - Suitable for broad metabolomics studies

  Usage:
    The `mimi_hmdb_extract` tool automatically extracts data from the `KEGG COMPOUND database <https://www.genome.jp/kegg/compound/>`_, a catalog of biological metabolites, biopolymers, and other small molecules and chemicals, using its `REST API <https://www.kegg.jp/kegg/rest/keggapi.html>`_. It can filter metabolites by molecular weight range and validates chemical formulas to ensure compatibility with MIMI's formula parser. 

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


2. **HMDB Database**: Optimal for human studies 

  The `Human Metabolome Database (HMDB) <https://hmdb.ca/>`_ is a freely available electronic database containing detailed information about small molecule metabolites found in the human body. Advantages:

  - Human-specific metabolites
  - Best for clinical and biomedical research
  - Detailed metabolite annotations

  Usage:
    The `mimi_hmdb_extract` tool extracts data from an XML file downloaded from the `HMDB <https://www.hmdb.ca/downloads>`_ and converts it to an appropriate TSV format for MIMI. It can filter metabolites by molecular weight range and validates chemical formulas to ensure compatibility with MIMI's formula parser.

.. code-block:: text

    $ mimi_hmdb_extract --help
    usage: mimi_hmdb_extract [-h] -x XML [-l MIN_MASS] [-u MAX_MASS] [-o OUTPUT]

    Extract metabolite information from HMDB XML file

    options:
    -h, --help            show this help message and exit
    --id-tag ID_TAG       Preferred ID tag to use. Options: accession, kegg_id, chebi_id, pubchem_compound_id, drugbank_id
    -x XML, --xml XML     Path to HMDB metabolites XML file
    -l MIN_MASS, --min-mass MIN_MASS
                            Lower bound of molecular weight in Da
    -u MAX_MASS, --max-mass MAX_MASS
                            Upper bound of molecular weight in Da
    -o OUTPUT, --output OUTPUT
                            Output TSV file path (default: metabolites.tsv)

3. **Custom Database**: Create your own list of compounds.

  Useful for:

  - Working with novel compounds
  - Focusing on specific compounds of interest
  - Combining multiple data sources

  Users can easily prepare a custom database file by creating a TSV file containing molecular formulas for any set of compounds (names are optional). Any custom database file must contain a header row with CF and Name columns (names are optional).

  MIMI relies on the unique identifiers in the "ID" column of an input database file for its analysis. If you have a list of compounds without standard identifiers, and you know (or suspect) the chemical formulas for them, you may use the commandline template provided here to automatically generate and add custom IDs to your list.

  Example:
    Starting with a TSV file containing CFs and Names:

.. code-block:: text

    $ head data/processed/customDB.tsv
    CF              Name
    C21H28N7O14P2   NAD+
    C21H29N7O17P3   NADP+
    C9H14N2O12P2    UDP
    C27H33N9O15P2   FAD
    C8H10NO6P1      Pyridoxal phosphate
    C15H22N6O5S1    S-Adenosyl-L-methionine
    C14H20N6O5S     S-Adenosyl-L-homocysteine
    C23H38N7O17P3S  Acetyl-CoA
    C34H32FeN4O4    Heme


The following command reads from `customDB.tsv`, adds custom IDs to the TSV file by combining a timestamp with row numbers, and writes to `customDBwithID.tsv`, both located in the data/processed directory.


.. code-block:: text
   
    $ timestamp=$(date +"%Y%m%d%H%M%S"); awk -v ts="$timestamp" 'BEGIN {OFS="\t"} NR==1 {print $1, "ID", $2} NR>1 {printf "%s\tMIMI_%s_%04d\t%s\n", $1, ts, NR-1, $2}' data/processed/customDB.tsv | sed 's/\r//' > data/processed/customDBwithID.tsv


  The output file (`customDBwithID.tsv`) contains the original chemical formula (CF) and compound name, with an additional ID column. Each ID is prefixed with `MIMI_` followed by a timestamp and a sequential number, ensuring unique identifiers for each compound.

.. code-block:: text

    $ head data/processed/customDBwithID.tsv
    CF              ID                          Name
    C21H28N7O14P2   MIMI_20250603132713_0001    NAD+
    C21H29N7O17P3   MIMI_20250603132713_0002    NADP+
    C9H14N2O12P2    MIMI_20250603132713_0003    UDP
    C27H33N9O15P2   MIMI_20250603132713_0004    FAD
    C8H10NO6P1      MIMI_20250603132713_0005    Pyridoxal
    C15H22N6O5S1    MIMI_20250603132713_0006    S-Adenosyl-L-methionine
    C14H20N6O5S     MIMI_20250603132713_0007    S-Adenosyl-L-homocysteine
    C23H38N7O17P3S  MIMI_20250603132713_0008    Acetyl-CoA
    C34H32FeN4O4    MIMI_20250603132713_0009    Heme



.. _mass-range-filtering:

Mass Range Filtering
~~~~~~~~~~~~~~~~~~~~

All database preparation methods support mass filtering to focus on your range of interest:

- `-l`: Lower mass limit
  
  - Excludes compounds below specified mass
  - Example: `-l 40` removes compounds < 40 Da
  - Useful for filtering out small molecules/contaminants

- `-u`: Upper mass limit
  
  - Excludes compounds above specified mass
  - Example: `-u 1000` removes compounds > 1000 Da
  - Helps focus on relevant mass ranges

Example: `-l 40 -u 1000` retains only compounds between 40-1000 Da.


.. _database-preparation-example:

Database Preparation Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's how to prepare databases from different sources using a typical mass range of 40-1000 Da (based on common MS data ranges):

1. **From KEGG**::


    # Extract compounds
    $ mimi_kegg_extract -l 40 -u 1000 -o data/processed/kegg_compounds_40_1000Da.tsv



    # Example output from KEGG:
    $ head -20  data/processed/kegg_compounds_40_1000Da.tsv 
    # Run Date: 2025-06-09 18:12:24
    # Command: mimi_kegg_extract -l 40 -u 1000 -o data/processed/kegg_compounds_40_1000Da.tsv
    # Number of compounds: 16089     
    #
    # compound         KEGG Compound Database
    # cpd              Release 114.0+/06-09, Jun 25
    #                  Kanehisa Laboratories
    # 
    # Mass range: 40.0-1000.0 Da
    #
    CF          ID      Name
    C5H8O5      C02994  L-Xylono-1,4-lactone
    C7H3Br2NO   C04178  Bromoxynil
    C15H12O4    C16760  Aloe emodin anthrone
    C12H3Cl7O   C15213  2,2',3',4,4',5,5'-Heptachloro-3-biphenylol
    C15H22O3    C22629  5-Dehydro-6-demethoxyfumagillol
    C20H26O2    C15142  3-Methoxy-D-homoestra-1,3,5(10),8-tetraen-17abeta-ol
    C30H46O8    C08876  Neriifolin
    C20H32O2    C15176  17-Methyl-5alpha-androst-2-ene-1alpha,17beta-diol
    C15H10O7    C100726-Hydroxyluteolin

    

    # Sort by compound ID (second column). Skips the comments and header lines.
    $ { head -n 11 data/processed/kegg_compounds_40_1000Da.tsv; tail -n +12 data/processed/kegg_compounds_40_1000Da.tsv | sort -k2,2; } > data/processed/kegg_compounds_40_1000Da_sorted.tsv

    # Finally remove duplicate chemical formulas
    $ { head -n 11 data/processed/kegg_compounds_40_1000Da_sorted.tsv; tail -n +12 data/processed/kegg_compounds_40_1000Da_sorted.tsv | awk '!seen[$1]++'; } > data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv

    # Count the number of compounds, including the comments and header lines
    $ wc -l data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv
    8540 data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv


    # The number of unique compounds
    $ expr 8540 - 11
    8529

2. **From HMDB**::

    # First download the HMDB XML file, then extract compounds
    $ mimi_hmdb_extract -l 40 -u 1000 -x data/raw/hmdb_metabolites.xml -o data/processed/hmdb_compounds_40_1000Da.tsv

    # Example output from HMDB:
    head -20  data/processed/hmdb_compounds_40_1000Da.tsv
    # Run Date: 2025-06-09 19:43:08
    # Command: mimi_hmdb_extract -l 40 -u 1000 -x data/raw/hmdb_metabolites.xml -o data/processed/hmdb_compounds_40_1000Da.tsv
    # Number of metabolites: 121144    
    # HMDB Metabolites Database
    # Version: 5.0
    # HMDB XML Database Creation: 2005-11-16 15:48:42 UTC
    # HMDB XML Database Last Update: 2021-10-13 17:34:04 UTC
    # Mass range: 40.0 to 1000.0 Da
    #
    CF          ID          Name
    C7H11N3O2   HMDB06704   Protein arginine N-methyltransferase 3
    C3H10N2     HMDB60172   Ornithine decarboxylase
    C4H6O3      HMDB06544   2-oxoglutarate receptor 1
    C4H8O3      HMDB00008   L-lactate dehydrogenase A-like 6B
    C19H24O3    HMDB04991   UDP glycosyltransferase 1 family polypeptide A7
    C4H8O3      HMDB00357   Novel protein similar to 3-hydroxymethyl-3-methylglutaryl-Coenzyme A lyase (Hydroxymethylglutaricaciduria)
    C9H12N2O5   HMDB00012   DNA dC->dU-editing enzyme APOBEC-3G
    C9H13N3O4   HMDB00014   DNA dC->dU-editing enzyme APOBEC-3G
    C21H30O4    HMDB00015   Steroid 21-hydroxylase
    C21H30O3    HMDB00016   Steroid 21-hydroxylase



    # Then sort by compound ID (second column). Skips the comments and header lines.
    $ { head -n 10 data/processed/hmdb_compounds_40_1000Da.tsv; tail -n +11 data/processed/hmdb_compounds_40_1000Da.tsv | sort -k2,2; } > data/processed/hmdb_compounds_40_1000Da_sorted.tsv

    # Finally remove duplicate chemical formulas
    $ { head -n 10 data/processed/hmdb_compounds_40_1000Da_sorted.tsv; tail -n +11 data/processed/hmdb_compounds_40_1000Da_sorted.tsv | awk '!seen[$1]++'; } > data/processed/hmdb_compounds_40_1000Da_sorted_uniq.tsv


    # Count the number of unique compounds, including the comments and header lines
    $ wc -l data/processed/hmdb_compounds_40_1000Da_sorted_uniq.tsv
    20112 data/processed/hmdb_compounds_40_1000Da_sorted_uniq.tsv


    # The number of unique compounds
    $ expr 20112 - 10
    20102

The output in both cases will be a TSV file containing:

- Comments and header lines(Database version and last release or update date)
- Chemical formulas (CF)
- Compound IDs (ID)
- Compound names (Name)
- Only compounds within the specified mass range if mass range filtering is used

This mass range we used is suitable for typical MS data, as shown in this example data::

    $ head -4 data/processed/testdata1.asc 
    43.16184    1089317  0.00003
    43.28766    1115802  0.00003
    43.28946    1226947  0.00003
    43.30269    1107425  0.00005
    
    $head -4  data/processed/testdata2.asc 
    43.16185    991278.47   0.00003
    43.28765    1093485.96  0.00003
    43.28946    1104252.3   0.00003
    43.3027     1018831	    0.00005



    $tail  -4  data/processed/testdata1.asc 
    999.50487   2941816 0.02121
    999.52689   2547575 0.01782
    999.90084   1347088 0.00892
    999.99347   2578292 0.00277
    
    $tail  -4  data/processed/testdata2.asc 
    999.50507   2794725.2   0.02121
    999.52709   2343769     0.01782
    999.90104   1225850.08  0.00892
    999.99367   2552509.08  0.00277


.. _step2-cache-creation:

Step2: Cache Creation
---------------------

Create cache files to store precomputed molecular masses and isotope patterns. This step is essential for:

- Fast analysis performance
- Initial setup before any analysis
- Updates when:

    * Database changes
    * Isotope settings change
    * New project begins

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

For natural abundance compounds, use:

.. code-block:: text

    $ mimi_cache_create -i neg -d data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv -c outdir/nat_nist

Expected Output: A binary cache file containing precomputed masses and isotope patterns for all compounds in your database.
This file will be used for fast matching during analysis.

.. _isotope-configuration:

Isotope Configuration
~~~~~~~~~~~~~~~~~~~~~

MIMI uses atomic weights and natural isotope abundances from the National Institute of Standards and Technology (NIST). The original data, sourced from the `NIST Atomic Weights database <https://www.nist.gov/pml/atomic-weights-and-isotopic-compositions-relative-atomic-masses>`_, was converted from plain text to JSON format for easier processing and is distributed with MIMI as `natural_isotope_abundance_NIST.json <https://raw.githubusercontent.com/NYUAD-Core-Bioinformatics/MIMI/refs/heads/main/mimi/data/natural_isotope_abundance_NIST.json>`_. This file serves as the foundation for all isotopic calculations.

For each element in `natural_isotope_abundance_NIST.json`, it provides detailed information about all its naturally occurring isotopes, including:

1. **Element Organization**: Data is organized by element symbol (e.g., "H", "C", "O", etc.)
2. **Isotope Information**: For each isotope of an element, the file includes:

   - `periodic_number`: The atomic number of the element
   - `element_symbol`: The chemical symbol of the element
   - `nominal_mass`: The mass number (number of protons + neutrons)
   - `exact_mass`: The precise atomic mass in atomic mass units (u)
   - `isotope_abundance`: The relative abundance of the isotope in nature

Example entry for Carbon (C) in `natural_isotope_abundance_NIST.json <https://raw.githubusercontent.com/NYUAD-Core-Bioinformatics/MIMI/refs/heads/main/mimi/data/natural_isotope_abundance_NIST.json>`_:

.. code-block:: text

    "C": [
        {
            "periodic_number": 6,
            "element_symbol": "C",
            "nominal_mass": 12,
            "exact_mass": 12.0,
            "isotope_abundance": 0.9893
        },
        {
            "periodic_number": 6,
            "element_symbol": "C",
            "nominal_mass": 13,
            "exact_mass": 13.00335483507,
            "isotope_abundance": 0.0107
        }
    ]

This data is used for:

- Calculating exact molecular masses
- Determining molecular isotope patterns
- Computing Molecular abundances



.. _label-option:

The --label Option for Stable Isotope Labeling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For samples with stable isotope labeling, you can override the natural abundance values using the `--label` (`-l`) option with a custom JSON file. This is particularly useful for experimental studies using stable isotope labeling with:

- Carbon (13C)
- Hydrogen (2H)
- Nitrogen (15N)
- Oxygen (17O, 18O)
- Sulfur (33S, 34S)

Key points about the `--label` option:

- Only specify the elements you want to override
- Isotope abundances must sum to 1.0 (MIMI verifies this)

Example: For 95% 13C labeling, you can use the provided configuration file at `C13_95.json <https://raw.githubusercontent.com/NYUAD-Core-Bioinformatics/MIMI/refs/heads/main/data/processed/C13_95.json>`_:

::

    C13_95.json 
    {
      "C": [
        {
          "periodic_number": 6,
          "element_symbol": "C",
          "nominal_mass": 12,
          "exact_mass": 12.000,
          "isotope_abundance": 0.05
        },
        {
          "periodic_number": 6,
          "element_symbol": "C",
          "nominal_mass": 13,
          "exact_mass": 13.00335484,
          "isotope_abundance": 0.95
        }
      ]
    }

For C13-95% labeled compounds, create a cache with the isotope configuration::

    mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv -c outdir/C13_95

Expected Output: A cache file with isotope patterns adjusted for C13-95% labeling. 

Use this when analyzing labeled samples.

.. _verify-cache:

Verify Cache
~~~~~~~~~~~~

Before proceeding with analysis, it's good practice to verify your cache contents. This helps ensure that the compounds and their isotope patterns were processed correctly::
    
    mimi_cache_dump outdir/nat_nist.pkl -n 2 -i 2

.. code-block:: text

    $ mimi_cache_dump outdir/nat_nist.pkl -n 2 -i 2
    # Cache Metadata:
    # Creation Date: 2025-06-03T14:47:08
    # MIMI Version: 1.0.0

    # Creation Parameters:
    # Full Command: /Users/aaa/anaconda3/envs/v_mimi/bin/mimi_cache_create -i neg -d data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv -c outdir/nat_nist
    # Ionization Mode: neg
    # Labeled Atoms File: None
    # Compound DB Files: data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv
    # Cache Output File: outdir/nat_nist.pkl
    # Isotope Data File: mimi/data/natural_isotope_abundance_NIST.json

    ============================================================
    Compound ID:      C00002
    Name:             ATP
    Formula:          [12]C10[1]H16[14]N5[16]O13[31]P3
    Mono-isotopic:    Yes (most abundant isotope)
    Mass:             505.988470
    Relative Abund:   1.000000 (reference)
    ------------------------------------------------------------
    ISOTOPE VARIANTS:
    Variant #1:
    Formula:        [12]C9 [13]C1 [1]H16 [14]N5 [16]O13 [31]P3
    Mono-isotopic:  No (isotope variant)
    Mass:           506.991825
    Relative Abund: 0.108157 (expected)
    ------------------------------------------------------------
    Variant #2:
    Formula:        [12]C10 [1]H16 [14]N5 [16]O12 [18]O1 [31]P3
    Mono-isotopic:  No (isotope variant)
    Mass:           507.992715
    Relative Abund: 0.026715 (expected)
    ------------------------------------------------------------

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
    Relative Abund: 0.227130 (expected)
    ------------------------------------------------------------
    Variant #2:
    Formula:        [12]C21 [1]H28 [14]N7 [16]O13 [18]O1 [31]P2
    Mono-isotopic:  No (isotope variant)
    Mass:           665.113916
    Relative Abund: 0.028770 (expected)
    ------------------------------------------------------------

Computing Molecular abundances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This guide explains how to calculate the relative abundance of a specific isotopologue in a molecule, accounting for both the fractional abundance of minor isotopes and their combinatorial placement within the molecule.

**Key Concepts:**

- **Isotopologue:** A molecule variant with specific isotopic composition.
- **Fractional Abundance:** The ratio of a minor isotope's natural abundance to the most abundant isotope of that element.
- **Combinatorial Factor:** The number of ways minor isotopes can be arranged within the molecule (binomial coefficient).
- **Relative Abundance:** The final likelihood of observing this isotopologue in mass spectrometry.

**Algorithm:**

1. **Initialize** the relative abundance to 1.

2. **For each isotope in the molecule**:
   - If it is a *minor isotope* (not the most abundant isotope for its element):
   
     a. Compute the **abundance factor**:

     .. math::

        \text{abundance_factor} = \left(\frac{\text{isotope_abundance}}{\text{highest_abundance}}\right)^{\text{count}}


     b. Update the relative abundance:

     .. math::

        \text{relative_abundance} *= \text{abundance_factor} \times \text{total_atoms_of_element}

   - If it is the **major isotope** (most abundant), it does not affect the calculation (factor = 1).

3. The **final relative abundance** is the product of all these factors.


Let's work through a detailed example calculation for the following molecular isotope



**Molecular Composition:**

- **Formula:** [12]C19 [13]C2 [1]H28 [14]N7 [16]O13 [17]O1 [31]P2
- **Carbon:** 21 atoms total (Nineteen [12]C and two [13]C)
- **Hydrogen:** 28 atoms (Twenty-eight [1]H only)
- **Nitrogen:** 7 atoms (Seven [14]N only)
- **Oxygen:** 14 atoms total (Thirteen [16]O and one [17]O)
- **Phosphorus:** 2 atoms (Two [31]P only)

**Natural Abundances:**

- 13C: 0.0107 (minor),  12C: 0.9893 (major)
- 17O: 0.00038 (minor), 16O: 0.99757 (major)

**Step 1: Calculate abundance factors**

- For 13C:

  .. math::

     \left(\frac{0.0107}{0.9893}\right)^2  = (0.0108)^2  = 0.00011664

- For 17O:

  .. math::

     \frac{0.00038}{0.99757} \approx 0.000381





**Step 2: Compute final relative abundance**

- Final relative abundance:

  .. math::

     (0.00011664 \times 21) \times  (0.000381 \times 14) = 0.00001306

Thus, the **relative abundance** of the isotopologue **[12]C19 [13]C2 [1]H28 [14]N7 [16]O13 [17]O1 [31]P2** is approximately **0.000013** which is the same as the result from the MIMI software.

.. code-block:: text

    $ mimi_cache_dump outdir/nat_nist.pkl -n 2 -i 30 | grep -A5  "Variant #26:" 
    Variant #26:
    Formula:        [12]C19 [13]C2 [1]H28 [14]N7 [16]O13 [17]O1 [31]P2
    Mono-isotopic:  No (isotope variant)
    Mass:           666.120598
    Relative Abund: 0.000013 (expected)





.. _step3-sample-analysis:

Step3: Sample Analysis
----------------------

After preparing your database and creating the cache files, you can analyze your mass spectrometry data using the mimi_mass_analysis command. This command matches your experimental peak lists against the precomputed theoretical masses and isotope patterns stored in the cache files.

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

The command requires two main inputs:

- One or more cache files (.pkl format) specified with --cache (-c) that contain the theoretical masses and patterns to match against
- One or more sample files (.asc format) specified with --sample (-s) containing your experimental peak lists

A key feature of MIMI is its flexibility in handling multiple datasets simultaneously. You can:

- Compare a single sample against multiple cache files with different isotope configurations
- Analyze multiple samples against a single cache file
- Process any combination of samples and cache files in parallel

This versatility makes MIMI particularly valuable for:

- Analyzing samples containing isotope-labeled standards
- Comparing time series measurements
- Contrasting treated vs untreated samples
- Examining samples under different experimental conditions



.. _input-file-format:

Mass spectrometry data input format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MIMI accepts mass spectrometry data in .asc format. Each line contains three columns:

- Mass (m/z)
- Intensity
- Resolution

Example input file (data/processed/testdata1.asc)::

    $ head -4 data/processed/testdata1.asc 
    43.16184    1089317  0.00003
    43.28766    1115802  0.00003
    43.28946    1226947  0.00003
    43.30269    1107425  0.00005

Now you're ready to analyze your mass spectrometry data. The analysis command matches your sample masses against the precomputed database and verifies matches using isotope patterns

.. code-block:: text


    $ mimi_mass_analysis -p 0.5 -vp 0.5 -c outdir/nat outdir/C13_95 -s data/processed/testdata1.asc -o outdir/results.tsv

Key parameters:

- `-p 0.5`: Mass matching tolerance (0.5 ppm) - controls how close the observed mass needs to be to the theoretical mass
- `-vp 0.5`: Isotope pattern verification tolerance (0.5 ppm) - controls how well the isotope pattern must match
- `-c`: Cache files to use (can specify multiple for comparing natural and labeled patterns)
- `-s`: Sample file to analyze (in .asc format)
- `-o`: Output file for results

.. _ppm-thresholds:

PPM Thresholds
~~~~~~~~~~~~~~

The PPM threshold affects match precision and reliability:

- **<0.5 ppm**: Excellent mass accuracy, high confidence in exact mass identification
- **0.5 - 1 ppm**: Good mass accuracy, reliable identification with isotope pattern validation
- **1-2 ppm**: Lower mass accuracy, less reliable identifications
- **>2 ppm**: Not recommended for high-resolution mass spectrometry data

Example::

    # High confidence analysis
    $ mimi_mass_analysis -p 0.5 -vp 0.5 -c outdir/nat -s data/processed/testdata1.asc -o outdir/results_excellent.tsv

    # Standard confidence analysis
    $ mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/nat -s data/processed/testdata1.asc -o outdir/results_good.tsv




.. _batch-processing:

Batch Processing
~~~~~~~~~~~~~~~~

MIMI supports processing multiple samples and multiple caches in a single run::

    $ mimi_mass_analysis -p 0.5 -vp 0.5 -c outdir/nat_nist outdir/C13_95 -s data/processed/testdata1.asc data/processed/testdata2.asc  -o outdir/results.tsv

   
    $ head -4 outdir/results.tsv; cat   outdir/results.tsv | grep -A6  C00147
    Log file /Users/aaa/test/log/results_20250609_223014.log
                                                                                        data/processed/testdata1.asc                                                                                    data/processed/testdata2.asc
                                                                                        nat_nist                                                 C13_95                                                 nat                                                       C13_95
    CF       ID     Name              C H N O P S nat_nist_mass      C13_95_mass        mass_measured error_ppm           intensity iso_count    mass_measured error_ppm            intensity iso_count mass_measured error_ppm             intensity   iso_count mass_measured  error_ppm           intensity    iso_count
    C5H5N5   C00147 Adenine           5 5 5 0 0 0 134.0472187163     139.06399291629998 134.04721     0.0650241017383722  9287320   2            139.06397     0.16478960145023944  159644896 4         134.04722     -0.009576476318665454 10030305.6  2         139.06396      0.2366989418442906  143680406.4  4
    C5H9NO2  C00148 L-Proline         5 9 1 2 0 0 114.05605206664    119.07282626664002 114.05603     0.19347189035452655 20271514  3            119.07282     0.052628632616788074 78100088  3         114.05601      0.36882426880317554  18852508.02 3         119.0728       0.220593067653808   72633081.84  3
    C4H6O5   C00149 (S)-Malate        4 6 0 5 0 0 133.01424682422999 137.02766618423    133.01427    -0.1742352460596866  4272635   2            137.02766     0.04513125094193654  2712827   1         133.01424      0.05130450419853602  4229908.65  2         137.02769     -0.1738026391616008  2550057.38   1
    C4H8N2O3 C00152 L-Asparagine      4 8 2 3 0 0 131.04621565841    135.05963501841    131.04618     0.27210560666728895 4508435   2            135.0596      0.2592810946979107   113403128 5         131.04617      0.34841456341916127  4418266.3   2         135.0596       0.2592810946979107  123609409.5  5
    C6H6N2O  C00153 Nicotinamide      6 6 2 1 0 0 121.04073635481                       121.04076    -0.19534902648706173 646772    1                                                                   121.04075     -0.1127322124761087   640304.28   1
    C4H9NO2S C00155 L-Homocysteine    4 9 1 2 0 1 134.02812324104002 138.04154260104002 134.02813    -0.05042941600803985 2003065   2            138.04159     -0.3433673595599844  566288    4         134.02816     -0.274263036027993    1882881.1   2         138.04156     -0.12604147747949546 554962.24    4
    C7H6O3   C00156 4-Hydroxybenzoate 7 6 0 3 0 0 137.02441758509002                    137.02447    -0.382522406671574   27237690  2                                                                   137.02444     -0.16358332604462747  87231044.64 2

Support for multiple data bases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MIMI supports processing multiple data bases in a single run. In this example, we create two data bases from KEGG and HMDB and then analyze the testdata1.asc file against both data bases::

    
    # Extract compounds, use KEGG IDs as the compound ID if available, otherwise it falls back to HMDB IDs
    $ mimi_hmdb_extract --id-tag kegg_id  -l 40 -u 1000 -x data/raw/hmdb_metabolites.xml -o data/processed/hmdb_compounds_40_1000Da.tsv

    # Count the number of compounds with KEGG IDs
    $ egrep -v "^HMDB|^#|^CF"  data/processed/hmdb_compounds_40_1000Da.tsv | wc -l
    121140


    # Sort by compound ID (second column). Skips the comments and header lines.
    $ { head -n 10 data/processed/hmdb_compounds_40_1000Da.tsv; tail -n +11 data/processed/hmdb_compounds_40_1000Da.tsv | sort -k2,2; } > data/processed/hmdb_compounds_40_1000Da_sorted.tsv

    # Remove duplicate chemical formulas
    $ { head -n 10 data/processed/hmdb_compounds_40_1000Da_sorted.tsv; tail -n +11 data/processed/hmdb_compounds_40_1000Da_sorted.tsv | awk '!seen[$1]++'; } > data/processed/hmdb_compounds_40_1000Da_sorted_uniq.tsv
    

    # Count the number of compounds with KEGG IDs
    $egrep -v "^HMDB|^#|^CF"  data/processed/hmdb_compounds_40_1000Da_sorted_uniq.tsv | wc -l
    20098

    # Kegg compounds already created in the previous example
    $ mimi_cache_create -i neg -d data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv -c outdir/kegg
    
    
    $ mimi_cache_create -i neg -d data/processed/hmdb_compounds_40_1000Da_sorted_uniq.tsv -c outdir/hmdb

    $ mimi_mass_analysis -p 0.5 -vp 0.5 -c outdir/kegg -c outdir/hmdb -s data/processed/testdata1.asc -o outdir/results.tsv


    $ head outdir/results.tsv 
    Log file    /Users/nr83/test/log/results_20250610_084653.log
                                                                                                                                                        data/processed/testdata1.asc                            
                                                                                                                                                        kegg                                                            hmdb            
    CF            ID        Name                                                       C   H   N  O  P  S  kegg_mass                hmdb_mass           mass_measured   error_ppm               intensity   iso_count   mass_measured   error_ppm               intensity   iso_count
    H3PO4         C00009    Orthophosphate                                             0   3   0  4  1  0  96.96961910639001        96.96961910639001   96.96959        0.3001598880622085      124803888   0           96.96959        0.3001598880622085      124803888   0
    H4P2O7        C00013    Diphosphate                                                0   4   0  7  2  0  176.93594999575          176.93594999575     176.93595       -2.4019898027273073e-05 3323336     0           176.93595       -2.4019898027273073e-05 3323336     0
    C15H22N6O5S   C00019    S-Adenosyl-L-methionine                                    15  22  6  5  0  1  397.12996254089          NO_MASS_MATCH       397.12984       0.3085662165101871      1360441     4                
    C10H14N5O7P   C00020    AMP                                                        10  14  5  7  1  0  346.05580834178          346.05580834178     346.0558        0.02410530271673412     3847223     1           346.0558        0.02410530271673412     3847223     1
    C14H20N6O5S   C00021    S-Adenosyl-L-homocysteine                                  14  20  6  5  0  1  383.11431247643003       383.11431247643003  383.11448       -0.43726784546911773    1524971     8           383.11448       -0.43726784546911773    1524971     8
    C5H9NO4       C00025    L-Glutamate                                                5   9   1  4  0  0  146.04588130578003       146.04588130578003  146.04582       0.4197706877343145      13906306    1           146.04582       0.4197706877343145      13906306    1
  
    $ tail  outdir/results.tsv 

    C11H21NO2     HMDB62669  11-nitro-1-undecene                                       11  21  1  2  0  0  NO_MAPPED_ID             198.1499524534                                                                      198.14989        0.31518251320303503     30164902    2
    C10H14O4S     HMDB62720  Colorectal cancer                                         10  14  0  4  0  1  NO_MAPPED_ID             229.0540036369                                                                      229.05404        -0.15875339178812753    698721664   7
    C8H8O4S       HMDB62775  4-Vinylphenol sulfate                                     8   8   0  4  0  1  NO_MAPPED_ID             199.00705344352002                                                                  199.00707        -0.08319544302948242    23203078    6
    C21H30O8S     HMDB62779  Cortisol 21-sulfate                                       21  30  0  8  0  1  NO_MAPPED_ID             441.15886263086                                                                     441.15885        0.028631092165590618    44812988    7
    C22H20OS      HMDB62791  (2,3-diphenylcyclopropyl)methyl Phenyl Sulfoxide          22  20  0  1  0  1  NO_MAPPED_ID             331.11620997157                                                                     331.11634        -0.3926972647329244     2713798     1
    C10H10N2O3S   HMDB62793  6-(2-amino-2-carboxyethyl)-4-hydroxybenzothiazole         10  10  2  3  0  1  NO_MAPPED_ID             237.03393689727                                                                     237.03394        -0.013089813408074368   6989369     2
    C22H44O4      HMDB72839  MG(19:0/0:0/0:0)                                          22  44  0  4  0  0  NO_MAPPED_ID             371.3166834294                                                                      371.31674        -0.1523513554154912     4211805     0
    C13H26O4      HMDB72866  MG(10:0/0:0/0:0)                                          13  26  0  4  0  0  NO_MAPPED_ID             245.17583284926002                                                                  245.17573        0.41949183504749804     231282528   1
    C21H40O5      HMDB92901  De Novo Triacylglycerol Biosynthesis TG(8:0/10:0/i-24:0)  21  40  0  5  0  0  NO_MAPPED_ID             371.28029792005                                                                     371.28019        0.2906700155512381      9494584     0
    C8H18O5       HMDB94708  Colorectal cancer                                         8   18  0  5  0  0  NO_MAPPED_ID             193.10814721099                                                                     193.10819        -0.2215805527299022     1863537     1



.. _results-format:

Results Format
~~~~~~~~~~~~~~

The output TSV file contains these columns:

- **CF**: Chemical formula of the matched compound
- **ID**: Compound identifier from the original database
- **Name**: Compound name
- **C**: Number of carbon atoms
- **H**: Number of hydrogen atoms
- **N**: Number of nitrogen atoms
- **O**: Number of oxygen atoms
- **P**: Number of phosphorus atoms
- **S**: Number of sulfur atoms
- **nat**: Calculated mass for natural abundance(User specified)
- **C13_95**: Calculated mass for C13-labeled (User specified)
- **mass_measured**: Observed mass in the sample
- **error_ppm**: Parts per million difference between calculated and observed mass
- **intensity**: Signal intensity in the sample
- **iso_count**: Number of isotopes detected

Example output file::

    $ mimi_mass_analysis -g  -p 0.5 -vp 0.5 -c outdir/nat outdir/C13_95 -s data/processed/testdata1.asc data/processed/testdata2.asc -o outdir/results.tsv

    $ head -4 outdir/results.tsv; cat   outdir/results.tsv | grep -A6  C00147
    Log file /Users/aaa/test/log/results_20250609_223014.log
                                                                                        data/processed/testdata1.asc                                                                                    
                                                                                        nat_nist                                                      C13_95                                                 
    CF       ID     Name              C H N O P S nat_nist_åmass           C13_95_mass        mass_measured error_ppm           intensity iso_count    mass_measured error_ppm            intensity iso_count 
    C5H5N5   C00147 Adenine           5 5 5 0 0 0 134.0472187163     139.06399291629998 134.04721     0.0650241017383722  9287320   2            139.06397     0.16478960145023944  159644896 4         
    C5H9NO2  C00148 L-Proline         5 9 1 2 0 0 114.05605206664    119.07282626664002 114.05603     0.19347189035452655 20271514  3            119.07282     0.052628632616788074 78100088  3         
    C4H6O5   C00149 (S)-Malate        4 6 0 5 0 0 133.01424682422999 137.02766618423    133.01427    -0.1742352460596866  4272635   2            137.02766     0.04513125094193654  2712827   1         
    C4H8N2O3 C00152 L-Asparagine      4 8 2 3 0 0 131.04621565841    135.05963501841    131.04618     0.27210560666728895 4508435   2            135.0596      0.2592810946979107   113403128 5         
    C6H6N2O  C00153 Nicotinamide      6 6 2 1 0 0 121.04073635481                       121.04076    -0.19534902648706173 646772    1
    C4H9NO2S C00155 L-Homocysteine    4 9 1 2 0 1 134.02812324104002 138.04154260104002 134.02813    -0.05042941600803985 2003065   2            138.04159     -0.3433673595599844  566288    4
    C7H6O3   C00156 4-Hydroxybenzoate 7 6 0 3 0 0 137.02441758509002                    137.02447    -0.382522406671574   27237690  2

    

.. _comprehensive-analysis-runs:

Comprehensive Analysis Runs
---------------------------

MIMI provides a comprehensive analysis script that allows you to perform multiple analyses with different parameter combinations in a single run. This is particularly useful for:

- Testing different mass matching tolerances
- Comparing isotope pattern verification thresholds
- Analyzing multiple samples simultaneously
- Generating results for different parameter combinations

The comprehensive run script (`run.sh`) performs the following steps:

1. **Setup and Validation**:

   - Checks for required input and output directories
   - Creates the output directory if it doesn't exist
   - Validates the input parameters

2. **Cache Creation**:

   - Creates two cache files:

     * Natural abundance cache (`nat_nist.pkl`)
     * C13-95% labeled cache (`C13_95.pkl`)

   - Uses the test database and C13-95% labeling configuration

3. **Parameter Testing**:

   - Tests different combinations of parameters:

     * Mass matching tolerance (p): 0.1, 0.5, 1.0 ppm
     * Isotope pattern verification (vp): 0.1, 0.5, 1.0 ppm

4. **Analysis Types**:

   - **Fixed vp Analysis**: Varies mass matching tolerance while keeping isotope verification fixed at 0.5 ppm
   - **Fixed p Analysis**: Varies isotope verification while keeping mass matching fixed at 0.5 ppm

Example Usage::

    $ sh ./run.sh data/processed outdir

The script content::

    #!/bin/bash

    # Check if both output and data directories are provided as arguments
    if [ $# -ne 2 ]; then
        echo "Usage: $0 <data_directory> <output_directory>"
        exit 1
    fi

    # Get directories from command line arguments
    datadir="$1"
    outdir="$2"

    # Create output directory
    mkdir -p "$outdir"



    # copy the KEGG compounds file to the output directory
    cp "$datadir/kegg_compounds_40_1000Da.tsv" "$outdir/testDB.tsv"

    # sort the KEGG compounds file by ID
    { head -n 11 "$outdir/testDB.tsv"; tail -n +12 "$outdir/testDB.tsv" | sort -k2,2; } > "$outdir/testDB_sorted.tsv"
    
    # remove duplicates
    awk '!seen[$1]++' "$outdir/testDB_sorted.tsv" > "$outdir/testDB_sorted_uniq.tsv"
    


    # Create cache files in outdir and check for success
    mimi_cache_create  -i neg   -d "$outdir/testDB_sorted_uniq.tsv"  -c "$outdir/nat_nist"
    mimi_cache_create  -i neg   -l "$datadir/C13_95.json" -d "$outdir/testDB_sorted_uniq.tsv"  -c "$outdir/C13_95"


    if [ ! -f "$outdir/nat_nist.pkl" ] || [ ! -f "$outdir/C13_95.pkl" ]; then
        echo "Error: Failed to create cache files"
        exit 1
    fi

    # Define test data files
    test_files=("testdata1.asc" "testdata2.asc")

    # Define parameter sets
    p_values=(0.1 0.5 1)
    vp_values=(0.1 0.5 1)

    # Loop through each test file
    for test_file in "${test_files[@]}"; do
        base_name=$(basename "$test_file" .asc)
        
        # Analysis for top graph (fixed vp=0.5, varying p)
        for p in "${p_values[@]}"; do
            p_str=$(echo $p | tr -d '.')
            mimi_mass_analysis -p $p -vp 0.5 -c "$outdir/nat_nist" "$outdir/C13_95" -s "$datadir/$test_file" -o "$outdir/n${base_name}_p${p_str}_vp05_combined.tsv"
        done
        
        # Analysis for bottom graph (fixed p=0.5, varying vp)
        for vp in "${vp_values[@]}"; do
            # Format vp value without underscore, just remove the dot
            vp_str=$(echo $vp | tr -d '.')
            mimi_mass_analysis -p 0.5 -vp $vp -c "$outdir/nat_nist" "$outdir/C13_95" -s "$datadir/$test_file" -o "$outdir/n${base_name}_p05_vp${vp_str}_combined.tsv"
        done
    done


    echo "Processing complete."




Example output files for testdata1.asc::

    ntestdata1_p01_vp05_combined.tsv    # p=0.1, vp=0.5
    ntestdata1_p05_vp01_combined.tsv    # p=0.5, vp=0.1  
    ntestdata1_p05_vp05_combined.tsv    # p=0.5, vp=0.5
    ntestdata1_p05_vp1_combined.tsv     # p=0.5, vp=1.0
    ntestdata1_p1_vp05_combined.tsv     # p=1.0, vp=0.5

    ntestdata2_p01_vp05_combined.tsv    # p=0.1, vp=0.5
    ntestdata2_p05_vp01_combined.tsv    # p=0.5, vp=0.1
    ntestdata2_p05_vp05_combined.tsv    # p=0.5, vp=0.5
    ntestdata2_p05_vp1_combined.tsv     # p=0.5, vp=1.0
    ntestdata2_p1_vp05_combined.tsv     # p=1.0, vp=0.5

This comprehensive analysis approach helps you:

- Find optimal parameter combinations for your data
- Compare results across different parameter settings
- Generate multiple result sets for further analysis
- Validate the robustness of your compound identifications


Plotting the results
~~~~~~~~~~~~~~~~~~~~

To plot the results, you can use the following command:

.. code-block:: text

    $python scripts/plot_results.py  outdir/


Troubleshooting
---------------

1. **Data Quality**:

   - Always combine mass accuracy with isotope pattern matching
   - Compare results from natural and labeled caches
   - Process replicates together for consistency
   - Verify important matches manually

2. **Common Issues and Solutions**:

   - **No matches found**:

     - Increase PPM threshold
     - Verify sample format
     - Check ionization mode
   
   - **Too many matches**:

     - Decrease PPM threshold
     - Use stricter verification PPM
     - Filter by isotope score
   
   - **Cache creation errors**:

     - Verify chemical formulas
     - Check labeling configuration
     - Enable debugging
   
   - **Performance issues**:

     - Use focused databases
     - Process samples in smaller batches
     - Optimize mass ranges

Complete Example
----------------

Here's a complete example from start to finish:

1. First, extract compounds from KEGG within your desired mass range::

    $ mimi_kegg_extract -l 40 -u 1000 -o data/processed/kegg_compounds_40_1000Da.tsv

    #Its optional to sort by compound ID and remove duplicate chemical formulas.
    #If required, follow the steps in the previous section to do it manually.

2. Create both natural abundance and C13-95% labeled caches::

    # Natural abundance
    $ mimi_cache_create -i neg -d data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv -c outdir/nat_nist

    # C13-95% labeled
    $ mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/kegg_compounds_40_1000Da_sorted_uniq.tsv -c outdir/C13_95

3. Verify the cache contents to ensure everything was processed correctly::

    $ mimi_cache_dump outdir/nat_nist.pkl -n 2 -i 2

4. Finally, analyze your sample using both caches::

    $ mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/nat_nist outdir/C13_95 -s data/processed/testdata2.asc -o outdir/results.tsv 
