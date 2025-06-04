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

# Sort and remove duplicates from KEGG compounds file
cp "$datadir/kegg_compounds_40_1000Da.tsv" "$outdir/testDB.tsv"
{ head -n 1 "$outdir/testDB.tsv"; tail -n +2 "$outdir/testDB.tsv" | sort -k2,2; } > "$outdir/testDB_sorted.tsv"
awk '!seen[$1]++' "$outdir/testDB_sorted.tsv" > "$outdir/testDB_sorted_uniq.tsv"



# Create cache files in outdir and check for success
mimi_cache_create  -i neg   -d "$outdir/testDB_sorted_uniq.tsv"  -c "$outdir/nat"
mimi_cache_create  -i neg   -l "$datadir/C13_95.json" -d "$outdir/testDB_sorted_uniq.tsv"  -c "$outdir/C13_95"


if [ ! -f "$outdir/nat.pkl" ] || [ ! -f "$outdir/C13_95.pkl" ]; then
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
        mimi_mass_analysis -p $p -vp 0.5 -c "$outdir/nat" "$outdir/C13_95" -s "$datadir/$test_file" -o "$outdir/n${base_name}_p${p_str}_vp05_combined.tsv"
    done
    
    # Analysis for bottom graph (fixed p=0.5, varying vp)
    for vp in "${vp_values[@]}"; do
        # Format vp value without underscore, just remove the dot
        vp_str=$(echo $vp | tr -d '.')
        mimi_mass_analysis -p 0.5 -vp $vp -c "$outdir/nat" "$outdir/C13_95" -s "$datadir/$test_file" -o "$outdir/n${base_name}_p05_vp${vp_str}_combined.tsv"
    done
done


echo "Processing complete."


