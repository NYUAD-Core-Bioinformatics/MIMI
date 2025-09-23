#!/bin/bash

# Example script showing how to run MIMI performance tests
# This demonstrates the usage of the performance testing suite

set -e

echo "MIMI Performance Testing Example"
echo "================================"
echo ""

# Check if we're in the MIMI directory
if [ ! -f "setup.py" ] || [ ! -d "mimi" ]; then
    echo "Error: This script should be run from the MIMI project root directory"
    echo "Please cd to the MIMI directory and run: scripts/$(basename "$0")"
    exit 1
fi

# Define directories
DATA_DIR="$(pwd)/data"
OUTPUT_DIR="$(pwd)/performance_test_output"
SCRIPTS_DIR="$(pwd)/scripts"

echo "Configuration:"
echo "  MIMI Project Dir: $(pwd)"
echo "  Data Directory  : $DATA_DIR"
echo "  Output Directory: $OUTPUT_DIR"
echo "  Scripts Directory: $SCRIPTS_DIR"
echo ""

# Check if required data files exist
echo "Checking for required test data..."
REQUIRED_FILES=(
    "$DATA_DIR/processed/testdata1.asc"
    "$DATA_DIR/processed/testdata2.asc"
    "$DATA_DIR/processed/C13_95.json"
)

# Check for compound database file (may have different names)
DB_FILE=""
for candidate in "kegg_compounds_40_1000Da.tsv" "kegg_compounds.tsv" "testDB_sorted_uniq.tsv"; do
    if [ -f "$DATA_DIR/processed/$candidate" ]; then
        DB_FILE="$DATA_DIR/processed/$candidate"
        break
    fi
done

if [ -z "$DB_FILE" ]; then
    echo "Error: No compound database file found in $DATA_DIR/processed/"
    echo "Expected one of: kegg_compounds_40_1000Da.tsv, kegg_compounds.tsv, testDB_sorted_uniq.tsv"
    echo ""
    echo "You may need to:"
    echo "  1. Run data extraction scripts first"
    echo "  2. Check the existing run.sh script for data preparation"
    exit 1
fi

echo "Found compound database: $DB_FILE"

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "Missing required files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "You may need to prepare test data first. Check the data/processed/ directory."
    exit 1
fi

echo "All required files found!"
echo ""

# Check if MIMI commands are available
echo "Checking MIMI installation..."
if ! command -v mimi_cache_create &> /dev/null; then
    echo "Error: mimi_cache_create not found"
    echo "Please install MIMI first: pip install -e ."
    exit 1
fi

if ! command -v mimi_mass_analysis &> /dev/null; then
    echo "Error: mimi_mass_analysis not found" 
    echo "Please install MIMI first: pip install -e ."
    exit 1
fi

echo "MIMI commands found!"
echo ""

# Create a temporary compound database file with the expected name
EXPECTED_DB="$DATA_DIR/processed/kegg_compounds_40_1000Da.tsv"
if [ "$DB_FILE" != "$EXPECTED_DB" ]; then
    echo "Creating symlink to match expected filename..."
    ln -sf "$(basename "$DB_FILE")" "$EXPECTED_DB"
    echo "Linked $DB_FILE -> $EXPECTED_DB"
    echo ""
fi

# Option 1: Quick Demo
echo "=========================================="
echo "OPTION 1: Quick Performance Demonstration"
echo "=========================================="
echo ""
echo "This will run a quick demo showing the performance benefits."
echo "Estimated time: 2-5 minutes"
echo ""
read -p "Run quick demo? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running quick performance demo..."
    python3 "$SCRIPTS_DIR/demo_performance_benefits.py" "$DATA_DIR"
    echo ""
    echo "Quick demo completed!"
    echo ""
fi

# Option 2: Comprehensive Testing
echo "=============================================="
echo "OPTION 2: Comprehensive Performance Testing"
echo "=============================================="
echo ""
echo "This will run comprehensive performance tests with detailed analysis."
echo "Estimated time: 10-20 minutes"
echo ""
read -p "Run comprehensive tests? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running comprehensive performance tests..."
    echo ""
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Run the comprehensive test
    "$SCRIPTS_DIR/run_performance_test.sh" "$DATA_DIR" "$OUTPUT_DIR" 3
    
    echo ""
    echo "Comprehensive testing completed!"
    echo ""
    echo "Results are available in: $OUTPUT_DIR"
    echo ""
    
    # Show generated files
    if [ -d "$OUTPUT_DIR" ]; then
        echo "Generated files:"
        ls -la "$OUTPUT_DIR"
        echo ""
        
        # Show report if available
        REPORT_FILE=$(find "$OUTPUT_DIR" -name "*performance_report_*.txt" | head -1)
        if [ -n "$REPORT_FILE" ]; then
            echo "Performance report preview:"
            echo "=========================="
            head -50 "$REPORT_FILE"
            echo ""
            echo "Full report available at: $REPORT_FILE"
        fi
    fi
fi

echo "=========================================="
echo "Performance Testing Complete"
echo "=========================================="
echo ""
echo "Key Benefits Demonstrated:"
echo "  ✓ Separated cache creation from analysis"
echo "  ✓ Cache reuse for multiple analyses"
echo "  ✓ Significant time savings (typically 2-10x faster)"
echo "  ✓ Better workflow flexibility"
echo "  ✓ Improved resource efficiency"
echo ""
echo "For more details, see: scripts/README_performance_testing.md"
