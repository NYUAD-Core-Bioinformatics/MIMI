# MIMI: Molecular Isotope Mass Identifier

***MIMI is a powerful tool for analyzing ultra-high-resolution Fourier Transform Ion Cyclotron Resonance (UHR-FT-ICR) mass spectrometry data.***

MIMI identifies chemical formulas for signals in mass spectra by matching the masses of observed peaks with theoretical masses of known compounds and then verifies the initial molecular assignments by searching for isotopic fine-structure patterns. MIMI can perform peak matching using either natural isotope ratios and/or labeled isotopes using tunable mass error thresholds and can analyze multiple MS datasets in batch. This flexibility facilitates the identification of molecules across multiple samples with labeled spike-ins and experiments with multiple replicates, treatment groups, or time series data. 

MIMI was developed in the [**Center for Genomics and Systems Biology (CGSB)**](https://nyuad.nyu.edu/en/research/faculty-labs-and-projects/nyuad-cgsb.html) at [**New York University Abu Dhabi (NYUAD)**](http://nyuad.nyu.edu/). For detailed documentation, please visit the [**MIMI Website**](https://corebioinf.abudhabi.nyu.edu/MIMI/index.html).

## Features

- Compound database preparation from KEGG and HMDB
- Fast mass matching with pre-computed cache files
- Support for both natural abundance and isotope-labeled samples
- Comprehensive isotope pattern verification
- Batch processing capabilities
- Flexible PPM threshold settings

## Installation

### Using Conda (Recommended)
```bash
conda install -c conda-forge mimi
```

### From Source
```bash
git clone https://github.com/NYUAD-Core-Bioinformatics/MIMI.git
cd MIMI
pip install .
```

## QuickStart

### 1. Prepare Compound Database

Extract compounds from KEGG or HMDB within a desired mass range:

```bash
# From KEGG
mimi_kegg_extract -l 40 -u 1000 -o data/processed/kegg_compounds.tsv

# From HMDB (requires hmdb_metabolites.xml)
mimi_hmdb_extract -l 40 -u 1000 -x data/processed/hmdb_metabolites.xml -o data/processed/hmdb_compounds.tsv
```

_Compound DB files will contain CF (chemical formula), ID (identifier), and Name (human-readable names) column headers. Example:_

```
CF              ID      Name
C8H14N2O2       C07841  Levetiracetam
C17H22O5        C09536  Pyrethrosin
C6H14           C11271  n-Hexane
C14H16ClN3O4S2  C12685  Cyclothiazide
C10H6O2         C14783  1,2-Naphthoquinone
```

### 2. Create Cache Files

Generate cache files for natural abundance or stable isotope-labeled compounds:

```bash
# Natural abundance
mimi_cache_create -i neg -d data/processed/kegg_compounds.tsv -c outdir/db_nat

# 95% C13-labeled (requires isotope configuration file)
mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/kegg_compounds.tsv -c outdir/db_C13
```

*MIMI provides flexibility to analyze samples based on theoretical masses of molecules for natural isotope ratios and/or isotope-labeled molecules (especially useful for samples with isotope-labeled spike-in standards).*

### 3. Analyze Samples

Process your mass spectrometry data:
```bash
mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/db_nat outdir/db_C13 -s data/processed/sample.asc -o outdir/results.tsv
```

**Input:** MIMI accepts MS peak lists with three columns: Mass (m/z), Intensity, and Resolution. Example:

```
43.16184    1089317    0.00003
43.28766    1115802    0.00003
43.28946    1226947    0.00003
```

**Output:** Results are provided as a tab-delimited file with the following detailed information:

- Chemical formula (CF)
- Compound ID
- Name
- Atomic composition
- Theoretical monoisotopic masses
- Measured masses
- Error (ppm)
- Intensity
- Isotope count

*Multiple datasets may be analyzed at the same time, and each sample can be compared against theoretical masses for different isotope abundance ratios. Results for samples analyzed together will be presented side-by-side for easy comparison.*

## Documentation
For detailed documentation and advanced usage, please visit the [**MIMI Website**](https://corebioinf.abudhabi.nyu.edu/MIMI/index.html).

## License
Copyright 2025 New York University. All Rights Reserved.

MIMI is available for internal non-commercial research and evaluation purposes only. Created by Nabil Rahiman (NYU Abu Dhabi) and Kristin Gunsalus (NYU New York, NYU Abu Dhabi).

For commercial licensing opportunities, please contact:  
NYU Technology Opportunities & Ventures (TOV)  
Phone: +1 (212) 263-8178  
Email: innovationscontracts@nyulangone.org

## Citation
If you use MIMI in your research, please cite:
[N. Rahiman, M. Ochsenkuen, S.A. Amin, and K.C. Gunsalus. BioRXiV 2025]

## Source Code
The MIMI code base and helper scripts are available from the [**MIMI GitHub repository**](https://github.com/NYUAD-Core-Bioinformatics/MIMI). For questions, problems, and feature requests, please use the [MIMI GitHub Issues](https://github.com/NYUAD-Core-Bioinformatics/MIMI/issues) page.
