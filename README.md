# MIMI
Molecular Isotope Mass Identifier

MIMI (Molecular Isotope Mass Identifier) is a powerful tool for analyzing isotope-labeled FT-ICR mass spectrometry data, developed by the CGSB Lab at New York University Abu Dhabi. It helps identify compounds by matching observed masses against known compounds and verifying their isotope patterns.

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

## Basic Workflow

### 1. Prepare Compound Database
Extract compounds from KEGG or HMDB within your desired mass range:
```bash
# From KEGG
mimi_kegg_extract -l 40 -u 1000 -o data/processed/kegg_compounds.tsv

# From HMDB (requires hmdb_metabolites.xml)
mimi_hmdb_extract -l 40 -u 1000 -x data/processed/hmdb_metabolites.xml -o data/processed/hmdb_compounds.tsv
```

### 2. Create Cache Files
Generate cache files for natural abundance and labeled compounds:
```bash
# Natural abundance
mimi_cache_create -i neg -d data/processed/kegg_compounds.tsv -c outdir/db_nat

# C13-labeled (requires isotope configuration file)
mimi_cache_create -i neg -l data/processed/C13_95.json -d data/processed/kegg_compounds.tsv -c outdir/db_C13
```

### 3. Analyze Samples
Process your mass spectrometry data:
```bash
mimi_mass_analysis -p 1.0 -vp 1.0 -c outdir/db_nat outdir/db_C13 -s data/processed/sample.asc -o outdir/results.tsv
```

## Input Format
MIMI accepts mass spectrometry data in .asc format with three columns:
- Mass (m/z)
- Intensity
- Resolution

Example:
```
43.16184    1089317    0.00003
43.28766    1115802    0.00003
43.28946    1226947    0.00003
```

## Output Format
Results are provided in TSV format with detailed information including:
- Chemical formula (CF)
- Compound ID
- Name
- Atomic composition
- Calculated and measured masses
- Error (ppm)
- Intensity
- Isotope count

## Documentation
For detailed documentation and advanced usage, please visit our [official documentation](https://corebioinf.abudhabi.nyu.edu/MIMI/index.html).

## License
Copyright 2025 New York University. All Rights Reserved.

MIMI is available for internal non-commercial research and evaluation purposes only. Created by Nabil Rahiman (NYU Abu Dhabi) and Kristin Gunsalus (NYU New York, NYU Abu Dhabi).

For commercial licensing opportunities, please contact:  
NYU Technology Opportunities & Ventures (TOV)  
Phone: +1 (212) 263-8178  
Email: innovationscontracts@nyulangone.org

## Citation
If you use MIMI in your research, please cite:
[Add citation information here]

## Support
For issues and feature requests, please visit our [GitHub repository](https://github.com/NYUAD-Core-Bioinformatics/MIMI).
