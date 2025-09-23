#!/bin/bash

# MIMI Performance Test Runner
# This script sets up and runs performance tests for mimi_cache_create and mimi_mass_analysis

set -e  # Exit on any error

# Check if required arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <data_directory> [output_directory] [number_of_runs]"
    echo ""
    echo "Arguments:"
    echo "  data_directory    : Path to MIMI data directory (required)"
    echo "  output_directory  : Path for test results (default: ./performance_test_results)"
    echo "  number_of_runs    : Number of test runs for averaging (default: 3)"
    echo ""
    echo "Examples:"
    echo "  $0 /path/to/data"
    echo "  $0 /path/to/data ./test_results"
    echo "  $0 /path/to/data ./test_results 5"
    echo ""
    echo "Required files in data directory:"
    echo "  - data/processed/kegg_compounds_40_1000Da.tsv"
    echo "  - data/processed/C13_95.json"
    echo "  - data/processed/testdata1.asc"
    echo "  - data/processed/testdata2.asc"
    exit 1
fi

# Set variables
DATA_DIR="$1"
OUTPUT_DIR="${2:-./performance_test_results}"
NUM_RUNS="${3:-3}"

# Script directory (where this script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PERFORMANCE_SCRIPT="$SCRIPT_DIR/performance_test.py"

# Validate inputs
if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Data directory '$DATA_DIR' does not exist"
    exit 1
fi

if [ ! -f "$PERFORMANCE_SCRIPT" ]; then
    echo "Error: Performance test script not found at '$PERFORMANCE_SCRIPT'"
    exit 1
fi

# Check for required test files
echo "Checking for required test files..."
REQUIRED_FILES=(
    "data/processed/kegg_compounds_40_1000Da.tsv"
    "data/processed/C13_95.json" 
    "data/processed/testdata1.asc"
    "data/processed/testdata2.asc"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$DATA_DIR/$file" ]; then
        MISSING_FILES+=("$DATA_DIR/$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "Error: Missing required test files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "Please ensure all required files are present in the data directory."
    echo "You may need to run data preparation scripts first."
    exit 1
fi

echo "All required files found!"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Display configuration
echo ""
echo "MIMI Performance Test Configuration:"
echo "====================================="
echo "Data directory    : $DATA_DIR"
echo "Output directory  : $OUTPUT_DIR"
echo "Number of runs    : $NUM_RUNS"
echo "Performance script: $PERFORMANCE_SCRIPT"
echo ""

# Check if mimi commands are available
echo "Checking MIMI command availability..."
if ! command -v mimi_cache_create &> /dev/null; then
    echo "Error: mimi_cache_create command not found"
    echo "Please ensure MIMI is properly installed and in your PATH"
    exit 1
fi

if ! command -v mimi_mass_analysis &> /dev/null; then
    echo "Error: mimi_mass_analysis command not found"
    echo "Please ensure MIMI is properly installed and in your PATH"
    exit 1
fi

echo "MIMI commands found!"

# Run the performance test
echo ""
echo "Starting performance tests..."
echo "=============================="

# Check if we're in a Python environment with required packages
if ! python3 -c "import statistics, subprocess, pathlib" 2>/dev/null; then
    echo "Error: Required Python packages not available"
    echo "Please ensure Python 3 with standard library is available"
    exit 1
fi

# Execute the performance test script
python3 "$PERFORMANCE_SCRIPT" "$DATA_DIR" "$OUTPUT_DIR" --runs "$NUM_RUNS"

RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "Performance testing completed successfully!"
    echo "=========================================="
    echo "Results saved in: $OUTPUT_DIR"
    echo ""
    echo "Key findings will be in the performance report file."
    echo "Look for files matching: *performance_report_*.txt"
    
    # List generated files
    echo ""
    echo "Generated files:"
    find "$OUTPUT_DIR" -name "*performance_report_*.txt" -exec echo "  Report: {}" \;
    find "$OUTPUT_DIR" -name "*.pkl" -exec echo "  Cache: {}" \;
    find "$OUTPUT_DIR" -name "*.tsv" -exec echo "  Results: {}" \;
    
else
    echo ""
    echo "Performance testing failed!"
    echo "==========================="
    echo "Check the output above for error details."
    exit 1
fi
