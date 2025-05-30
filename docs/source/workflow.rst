Workflow
========

MIMI is a tool for analyzing mass spectrometry data. It helps identify compounds by matching observed masses against known compounds and verifying their isotope patterns.

Installation
------------

MIMI can be installed using conda, which is the recommended method as it handles all dependencies automatically::

    conda install -c conda-forge mimi

Alternatively, you can install from source if you need the latest development version::

    git clone https://github.com/NYUAD-Core-Bioinformatics/MIMI.git
    cd MIMI
    pip install .

Basic Workflow
--------------

MIMI's analysis involves three steps:

Step1: Prepare your compound database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* This involves extracting compounds from either KEGG (for general biological samples) or HMDB (for human-specific metabolites) or manually create a custom database.
* You can filter compounds by mass range using -l (lower limit) and -u (upper limit) parameters
* The output is a TSV file containing compounds with their chemical formulas(CF), Compound IDs(ID), and names(Name)
* You can also create a custom database with specific compounds of interest

See for more details: :ref:`step1-database-preparation-from-kegg-and-hmdb` :ref:`database-options`, :ref:`mass-range-filtering`, :ref:`custom-database-format`, 

Step2: Create cache files for faster matching
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* This step precomputes molecular masses and isotope patterns for all compounds in your database
* You can create caches for different isotope configurations (natural abundance or labeled)
* The cache creation is essential for fast analysis performance
* You can specify tolerance levels for both mass matching (-p) and isotope pattern verification (-vp).
* You can verify the cache contents using `mimi_cache_dump` to ensure everything was processed correctly

See for more details: :ref:`step2-cache-creation`, :ref:`ppm-thresholds`, :ref:`isotope-configuration`  :ref:`verify-cache`

Step3: Sample Analysis
~~~~~~~~~~~~~~~~~~~~~~

- This step matches your mass spectrometry data against the precomputed database.
- You can analyze samples in `.asc` format, which should contain mass, intensity, and resolution columns.
- The analysis process includes both mass matching and isotope pattern verification.
- Multiple cache files can be specified for comparative or labeled analyses.
- The output is a TSV file containing detailed information about all matched compounds.
- For convenience, a provided script allows you to run comprehensive analysis across multiple cache files and sample files, testing different PPM thresholds automatically.

See for more details: :ref:`step3-sample-analysis`, :ref:`input-file-format`,, :ref:`multiple-cache-analysis`, :ref:`batch-processing`, :ref:`results-format`, :ref:`comprehensive-analysis-runs`

.. _database-options:

Database Options
----------------

MIMI supports two ways to prepare your compound database from external sources with a given mass range:

1. **KEGG Database**:

   - Broad compound coverage
   - Uses REST API
   - Includes pathway data
   - Works well for general biological samples


2. **HMDB Database** (For human samples):

   - Human-specific metabolites
   - Requires XML file download
   - More detailed metabolite info
   - Best for clinical samples


   The HMDB database is provided as an XML file named **hmdb_metabolites.xml**. This file contains:
   
   - Detailed information about each metabolite
   - Chemical formulas and molecular weights
   - Names and identifiers
   - Additional metadata about human metabolites

   Download the HMDB XML file from `https://hmdb.ca/downloads <https://hmdb.ca/downloads>`_ and save it as **hmdb_metabolites.xml**.

.. _mass-range-filtering:

Mass Range Filtering
--------------------

Filter compounds by mass using:

- `-l`: Lower mass limit (e.g., 40 Da)

  - Filters out compounds lighter than this mass
  - Useful for removing small molecules or contaminants
  - Example: -l 100 filters out compounds < 100 Da

- `-u`: Upper mass limit (e.g., 1000 Da)

  - Filters out compounds heavier than this mass
  - Useful for focusing on specific mass ranges
  - Example: -u 1000 filters out compounds > 1000 Da

Example: `-l 40 -u 1000` keeps compounds between 40-1000 Da.

.. _custom-database-format:

Custom Database Format
----------------------

Create a custom database when:

- Working with novel compounds
- Having specific compounds of interest
- Needing to add custom annotations
- Combining multiple sources

The file must contain these required columns::

    CF      ID        Name
    C6H12O6 C00031    Glucose
    C5H10O5 C00036    Ribose
    C3H7NO2 C00041    Alanine
    C7H6O2  C00042    Benzoic Acid
    C4H8O4  C00043    Erythritol

.. _step1-database-preparation-from-kegg-and-hmdb:

Step1: Database Preparation from KEGG and HMDB
----------------------------------------------

The first step in using MIMI is to prepare your compound database. This involves extracting relevant compounds from either KEGG or HMDB and saving them in a format that MIMI can use.
Since the observed mass range is 40-1000 Da from Mass Spectrometry, we use the same mass range 40-1000 Da for KEGG and HMDB.

Mass Spectrometry data::

    $ head data/processed/testdata1.asc 
    43.16184	1089317	0.00003
    43.28766	1115802	0.00003
    43.28946	1226947	0.00003
    43.30269	1107425	0.00005
    43.36457	2236071	0.00004
    43.36459	1891040	0.00004
    43.37268	1281049	0.00004
    43.4223	2184166	0.00002
    43.42234	23344476	0.00004
    43.42237	22443004	0.00004

    $ tail  data/processed/testdata1.asc 
    998.43509	1206308	0.00535
    998.46616	1131300	0.00695
    998.73782	1093661	0.00813
    999.04497	1088280	0.00781
    999.2502	1257493	0.00659
    999.26602	1114389	0.00842
    999.50487	2941816	0.02121
    999.52689	2547575	0.01782
    999.90084	1347088	0.00892
    999.99347	2578292	0.00277

For KEGG database, use the following command to extract compounds within a specific mass range::

    mimi_kegg_extract -l 40 -u 1000 -o data/processed/kegg_compounds_40_1000Da.tsv

Expected Output: A TSV file containing compounds with their chemical formulas(CF), IDs(ID), and names(Name). The file will include compounds with molecular weights between 40 and 1000 Da from the KEGG database.

For HMDB database, first download the XML file, then use this command to extract the metabolites::

    mimi_hmdb_extract -l 40 -u 1000 -x data/processed/hmdb_metabolites.xml -o data/processed/hmdb_compounds_40_1000Da.tsv

Expected Output: Similar to KEGG, but with human metabolites from HMDB. Useful when studying human samples and need human-specific compounds.

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

For natural abundance compounds, use::

    mimi_cache_create -i neg -d data/processed/kegg_compounds_40_1000Da.tsv -c outdir/db_nat

Expected Output: A binary cache file containing precomputed masses and isotope patterns for all compounds in your database. This file will be used for fast matching during analysis.

.. _isotope-configuration:

Isotope Configuration
---------------------

MIMI uses atomic weights and natural isotope abundances from the National Institute of Standards and Technology (NIST). The original data, sourced from the `NIST Atomic Weights database <https://www.nist.gov/pml/atomic-weights-and-isotopic-compositions-relative-atomic-masses>`_, was converted from plain text to JSON format for easier processing and is distributed with MIMI as `natural_isotope_abundance_NIST.json <https://raw.githubusercontent.com/NYUAD-Core-Bioinformatics/MIMI/refs/heads/main/mimi/data/natural_isotope_abundance_NIST.json>`_. This file serves as the foundation for all isotopic calculations.

For each element in `natural_isotope_abundance_NIST.json`, it provides detailed information about all its naturally occurring isotopes, including:

1. **Element Organization**: Data is organized by element symbol (e.g., "H", "C", "O", etc.)
2. **Isotope Information**: For each isotope of an element, the file includes:

   - `periodic_number`: The atomic number of the element
   - `element_symbol`: The chemical symbol of the element
   - `nominal_mass`: The mass number (number of protons + neutrons)
   - `exact_mass`: The precise atomic mass in atomic mass units (u)
   - `natural_abundance`: The relative abundance of the isotope in nature

Example entry for Carbon (C):
::

    "C": [
        {
            "periodic_number": 6,
            "element_symbol": "C",
            "nominal_mass": 12,
            "exact_mass": 12.0,
            "natural_abundance": 0.9893
        },
        {
            "periodic_number": 6,
            "element_symbol": "C",
            "nominal_mass": 13,
            "exact_mass": 13.00335483507,
            "natural_abundance": 0.0107
        }
    ]

This data is used for:

- Calculating exact molecular masses
- Determining molecular isotope patterns
- Computing Molecular abundances


For samples with stable isotope enrichment, you can override these values using the `--label` (`-l`) option with a custom JSON file. 
This is particularly useful for experimental studies using stable isotope labeling with:

- Carbon (13C)
- Hydrogen (2H)
- Nitrogen (15N)
- Oxygen (17O, 18O)
- Sulfur (33S, 34S)

Key points about isotope configuration:

- Use the `--label` (`-l`) option with a custom JSON file
- Only specify the elements you want to override
- Isotope abundances must sum to 1.0 (MIMI verifies this)
- For multiple labeled elements, include all in one file

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

For C13-labeled compounds, create a cache with the isotope configuration::

    mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/kegg_compounds_40_1000Da.tsv -c outdir/db_C13

Expected Output: A cache file with isotope patterns adjusted for 95% C13 labeling. 

Use this when analyzing labeled samples.

.. _verify-cache:

Verify Cache
-------------

Before proceeding with analysis, it's good practice to verify your cache contents. This helps ensure that the compounds and their isotope patterns were processed correctly::

    mimi_cache_dump outdir/db_nat.pkl -n 2 -i 2

Example output::

    mimi_cache_dump outdir/db_nat.pkl -n 2 -i 2
    # Cache Metadata:
    # Creation Date: 2025-04-26T00:08:03
    # MIMI Version: 1.0.0

    # Creation Parameters:
    # Full Command: /Users/aaa/anaconda3/envs/v_test/bin/mimi_cache_create -i neg -d data/processed/kegg_compounds_40_1000Da.tsv -c outdir/db_nat
    # Ionization Mode: neg
    # Labeled Atoms File: None
    # Compound DB Files: data/processed/kegg_compounds_40_1000Da.tsv
    # Cache Output File: outdir/db_nat.pkl
    # Isotope Data File: mimi/data/natural_isotope_abundance_NIST.json

    ============================================================
    Compound ID:      C07350
    Name:             Phlorisovalerophenone
    Formula:          [12]C11[1]H14[16]O4
    Mono-isotopic:    Yes (most abundant isotope)
    Mass:             209.081932
    Relative Abund:   1.000000 (reference)
    ------------------------------------------------------------
    ISOTOPE VARIANTS:
    Variant #1:
    Formula:        [12]C10 [13]C1 [1]H14 [16]O4
    Mono-isotopic:  No (isotope variant)
    Mass:           210.085287
    Relative Abund: 0.118973 (expected)
    ------------------------------------------------------------
    Variant #2:
    Formula:        [12]C11 [1]H14 [16]O3 [18]O1
    Mono-isotopic:  No (isotope variant)
    Mass:           211.086177
    Relative Abund: 0.008220 (expected)
    ------------------------------------------------------------

    ============================================================
    Compound ID:      C08999
    Name:             Capillarisin
    Formula:          [12]C16[1]H12[16]O7
    Mono-isotopic:    Yes (most abundant isotope)
    Mass:             315.051026
    Relative Abund:   1.000000 (reference)
    ------------------------------------------------------------
    ISOTOPE VARIANTS:
    Variant #1:
    Formula:        [12]C15 [13]C1 [1]H12 [16]O7
    Mono-isotopic:  No (isotope variant)
    Mass:           316.054381
    Relative Abund: 0.173052 (expected)
    ------------------------------------------------------------
    Variant #2:
    Formula:        [12]C16 [1]H12 [16]O6 [18]O1
    Mono-isotopic:  No (isotope variant)
    Mass:           317.055271
    Relative Abund: 0.014385 (expected)
    ------------------------------------------------------------

.. _step3-sample-analysis:

Step3: Sample Analysis
----------------------

.. _input-file-format:

Input File Format
-----------------

MIMI accepts mass spectrometry data in .asc format. Each line contains three columns:

- Mass (m/z)
- Intensity
- Resolution

Example input file (data/processed/testdata1.asc)::

    43.16184    1089317    0.00003
    43.28766    1115802    0.00003
    43.28946    1226947    0.00003
    43.30269    1107425    0.00005
    43.36457    2236071    0.00004
    43.36459    1891040    0.00004
    43.37268    1281049    0.00004
    43.4223     2184166    0.00002
    43.42234    23344476   0.00004
    43.42237    22443004   0.00004

Now you're ready to analyze your mass spectrometry data. The analysis command matches your sample masses against the precomputed database and verifies matches using isotope patterns::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/db_nat outdir/db_C13 -s data/processed/testdata1.asc -o outdir/results.tsv

Key parameters:

- `-p 1.0`: Mass matching tolerance (1 ppm) - controls how close the observed mass needs to be to the theoretical mass
- `-vp 1.0`: Isotope pattern verification tolerance (1 ppm) - controls how well the isotope pattern must match
- `-c`: Cache files to use (can specify multiple for comparing natural and labeled patterns)
- `-s`: Sample file to analyze (in .asc format)
- `-o`: Output file for results

.. _ppm-thresholds:

PPM Thresholds
--------------

The PPM threshold affects match precision and reliability:

- **<0.5 ppm**: Excellent mass accuracy, high confidence in exact mass identification
- **0.5 - 1 ppm**: Good mass accuracy, reliable identification with isotope pattern validation
- **1-2 ppm**: Lower mass accuracy, less reliable identifications
- **>2 ppm**: Not recommended for high-resolution mass spectrometry data

Example::

    # High confidence analysis
    mimi_mass_analysis -p 0.5 -vp 0.5 -c db_nat -s sample.asc -o results_excellent.tsv

    # Standard confidence analysis
    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat -s sample.asc -o results_good.tsv

.. _multiple-cache-analysis:

Multiple Cache Analysis
-----------------------

You can analyze your samples against multiple caches simultaneously. This is useful when comparing natural and labeled patterns::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat db_13C -s data/processed/testdata1.asc -o results.tsv



.. _batch-processing:

Batch Processing
----------------

MIMI supports processing multiple samples in a single run. This is useful for analyzing replicates or comparing different conditions::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c db_nat -s data/processed/testdata1.asc data/processed/testdata2.asc -o batch_results.tsv



.. _results-format:

Results Format
--------------

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
- **db_mass_nat**: Calculated mass for natural abundance(User specified)
- **db_mass_C13**: Calculated mass for C13-labeled (User specified)
- **mass_measured**: Observed mass in the sample
- **error_ppm**: Parts per million difference between calculated and observed mass
- **intensity**: Signal intensity in the sample
- **iso_count**: Number of isotopes detected

Example output file::

    Log file  /Users/aaa/test/log/results_20250426_000954.log
                                                                            data/processed/testdata1.asc						
                                                                            db_nat                                            db_C13			
    CF        ID      Name              C H N O P S db_nat_mass db_C13_mass mass_measured error_ppm     intensity   iso_count mass_measured error_ppm     intensity     iso_count
    C5H5N5    C00147  Adenine           5 5 5 0 0 0 134.0472187 139.0639929 134.04722     -0.009576476  10030305.6  3         139.06396     0.236698942   143680406.4   4
    C5H9NO2   C00148  L-Proline         5 9 1 2 0 0 114.0560521 119.0728263 114.05601     0.368824269   18852508.02 4         119.0728      0.220593068   72633081.845  8
    C4H6O5    C00149  (S)-Malate        4 6 0 5 0 0 133.0142468 137.0276662 133.01424     0.051304504   4229908.65  2         137.02769     -0.173802639  2550057.38    4
    C4H8N2O3  C00152  L-Asparagine      4 8 2 3 0 0 131.0462157 135.059635  131.04617     0.348414563   4418266.3   4         135.0596      0.259281095   123609409.5   8
    C6H6N2O   C00153  Nicotinamide      6 6 2 1 0 0 121.0407364             121.04075     -0.112732212  640304.28   1
    C4H9NO2S  C00155  L-Homocysteine    4 9 1 2 0 1 134.0281232 138.0415426 134.02816     -0.274263036  1882881.1   3         138.04156     -0.126041477  554962.24     7
    C7H6O3    C00156  4-Hydroxybenzoate	7 6 0 3 0 0 137.0244176             137.02444     -0.163583326  87231044.64 2
  

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

     * Natural abundance cache (`db_nat.pkl`)
     * C13-labeled cache (`db_C13.pkl`)

   - Uses the test database and C13 labeling configuration

3. **Parameter Testing**:

   - Tests different combinations of parameters:

     * Mass matching tolerance (p): 0.1, 0.5, 1.0 ppm
     * Isotope pattern verification (vp): 0.1, 0.5, 1.0 ppm

4. **Analysis Types**:

   - **Fixed vp Analysis**: Varies mass matching tolerance while keeping isotope verification fixed at 0.5 ppm
   - **Fixed p Analysis**: Varies isotope verification while keeping mass matching fixed at 0.5 ppm

Example Usage::

    ./run.sh data_directory output_directory

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

    # Create cache files in outdir and check for success
    mimi_cache_create  -i neg   -d "$datadir/testDB.tsv"  -c "$outdir/db_nat"
    mimi_cache_create  -i neg   -l "$datadir/C13_95.json" -d "$datadir/testDB.tsv"  -c "$outdir/db_C13"

    if [ ! -f "$outdir/db_nat.pkl" ] || [ ! -f "$outdir/db_C13.pkl" ]; then
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
            mimi_mass_analysis -p $p -vp 0.5 -c "$outdir/db_nat" "$outdir/db_C13" -s "$datadir/$test_file" -o "$outdir/n${base_name}_p${p_str}_vp05_combined.tsv"
        done
        
        # Analysis for bottom graph (fixed p=0.5, varying vp)
        for vp in "${vp_values[@]}"; do
            # Format vp value without underscore, just remove the dot
            vp_str=$(echo $vp | tr -d '.')
            mimi_mass_analysis -p 0.5 -vp $vp -c "$outdir/db_nat" "$outdir/db_C13" -s "$datadir/$test_file" -o "$outdir/n${base_name}_p05_vp${vp_str}_combined.tsv"
        done
    done

    echo "Processing complete."



Example output files for testdata1.asc::

    ntestdata1_p01_vp05_combined.tsv    # p=0.1, vp=0.5
    ntestdata1_p05_vp05_combined.tsv    # p=0.5, vp=0.5
    ntestdata1_p1_vp05_combined.tsv     # p=1.0, vp=0.5
    ntestdata1_p05_vp01_combined.tsv    # p=0.5, vp=0.1
    ntestdata1_p05_vp05_combined.tsv    # p=0.5, vp=0.5
    ntestdata1_p05_vp1_combined.tsv     # p=0.5, vp=1.0

This comprehensive analysis approach helps you:

- Find optimal parameter combinations for your data
- Compare results across different parameter settings
- Generate multiple result sets for further analysis
- Validate the robustness of your compound identifications

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

    mimi_kegg_extract -l 40 -u 400 -o data/processed/kegg_compounds.tsv

2. Create both natural abundance and C13-labeled caches::

    # Natural abundance
    mimi_cache_create -i neg -d data/processed/kegg_compounds.tsv -c outdir/db_nat

    # C13-labeled
    mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/kegg_compounds.tsv -c outdir/db_C13

3. Verify the cache contents to ensure everything was processed correctly::

    mimi_cache_dump outdir/db_nat.pkl -n 2 -i 2

4. Finally, analyze your sample using both caches::

    mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/db_nat outdir/db_C13 -s data/processed/testdata1.asc -o outdir/results.tsv 