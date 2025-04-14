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


# mimi_cache_create  -i neg   -d "kegg_compounds_40-1000Da.tsv"  -c "$outdir/db_nat"
# mimi_cache_create  -i neg -l "$datadir/C13_95.json"  -d "kegg_compounds_40-1000Da.tsv"  -c "$outdir/db_C13"
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

# Remove the first two rows from all output TSV files
# echo "Removing first two rows from all output files..."
# for output_file in "$outdir"/*.tsv; do
#     if [ -f "$output_file" ]; then
#         # Create a temporary file
#         temp_file=$(mktemp)
#         # Skip the first two lines and write the rest to the temp file
#         tail -n +3 "$output_file" > "$temp_file"
#         # Replace the original file with the temp file
#         mv "$temp_file" "$output_file"
#         echo "Processed: $(basename "$output_file")"
#     fi
# done

echo "Processing complete."


