#!/bin/bash

# MIMI Performance Benefits Demonstration
# 
# This script demonstrates why separating cache creation from analysis is beneficial
# by timing both approaches and showing the performance differences.

set -e  # Exit on any error

# Configuration
DATA_DIR=""
OUTPUT_DIR=""
DB_FILE=""
SAMPLE_FILE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    printf "${BLUE}%s${NC}\n" "$1"
}

print_success() {
    printf "${GREEN}%s${NC}\n" "$1"
}

print_warning() {
    printf "${YELLOW}%s${NC}\n" "$1"
}

print_error() {
    printf "${RED}%s${NC}\n" "$1"
}

# Function to validate inputs and setup
setup_demo() {
    if [ $# -ne 1 ]; then
        print_error "Usage: $0 <data_directory>"
        echo ""
        echo "Example: $0 /path/to/MIMI/data"
        echo ""
        echo "Required files in data directory:"
        echo "  - data/processed/kegg_compounds_40_1000Da.tsv (or similar)"
        echo "  - data/processed/testdata1.asc"
        exit 1
    fi

    DATA_DIR="$1"
    OUTPUT_DIR="${DATA_DIR%/}/demo_output"
    
    # Validate data directory
    if [ ! -d "$DATA_DIR" ]; then
        print_error "Error: Data directory '$DATA_DIR' does not exist"
        exit 1
    fi

    # Find compound database file
    for candidate in "kegg_compounds_40_1000Da.tsv" "kegg_compounds.tsv" "testDB_sorted_uniq.tsv"; do
        if [ -f "$DATA_DIR/processed/$candidate" ]; then
            DB_FILE="$DATA_DIR/processed/$candidate"
            break
        fi
    done

    if [ -z "$DB_FILE" ]; then
        print_error "Error: No compound database file found in $DATA_DIR/processed/"
        echo "Expected one of: kegg_compounds_40_1000Da.tsv, kegg_compounds.tsv, testDB_sorted_uniq.tsv"
        exit 1
    fi

    # Find sample file
    SAMPLE_FILE="$DATA_DIR/processed/testdata1.asc"
    if [ ! -f "$SAMPLE_FILE" ]; then
        print_error "Error: Sample file not found: $SAMPLE_FILE"
        exit 1
    fi

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    # Get database size (number of compounds)
    local db_compounds=""
    if [ -f "$DB_FILE" ]; then
        # Count non-comment lines (skip lines starting with #)
        db_compounds=$(grep -v '^#' "$DB_FILE" 2>/dev/null | wc -l | tr -d ' ')
        # If TSV format, subtract 1 for header line (if it exists and isn't a comment)
        if [ -n "$db_compounds" ] && [ "$db_compounds" -gt 1 ]; then
            # Check if first non-comment line looks like a header
            local first_line=$(grep -v '^#' "$DB_FILE" 2>/dev/null | head -n 1)
            if [[ "$first_line" =~ ^[[:alpha:]] ]]; then
                db_compounds=$((db_compounds - 1))
            fi
        fi
    fi

    # Get sample file size (number of data lines, excluding comments)
    local sample_lines=""
    if [ -f "$SAMPLE_FILE" ]; then
        sample_lines=$(grep -v '^#' "$SAMPLE_FILE" 2>/dev/null | wc -l | tr -d ' ')
    fi

    print_success "Setup complete!"
    echo "  Data directory: $DATA_DIR"
    echo "  Database file: $DB_FILE"
    if [ -n "$db_compounds" ] && [ "$db_compounds" != "0" ]; then
        echo "    → Contains ~$db_compounds compounds"
    fi
    echo "  Sample file: $SAMPLE_FILE"
    if [ -n "$sample_lines" ] && [ "$sample_lines" != "0" ]; then
        echo "    → Contains $sample_lines lines of data"
    fi
    echo "  Output directory: $OUTPUT_DIR"
    echo ""
}

# Function to check MIMI commands
check_mimi_commands() {
    print_header "Checking MIMI command availability..."
    
    if ! command -v mimi_cache_create &> /dev/null; then
        print_error "Error: mimi_cache_create command not found"
        echo "Please ensure MIMI is properly installed and in your PATH"
        exit 1
    fi

    if ! command -v mimi_mass_analysis &> /dev/null; then
        print_error "Error: mimi_mass_analysis command not found"
        echo "Please ensure MIMI is properly installed and in your PATH"
        exit 1
    fi

    print_success "MIMI commands found!"
    echo ""
}

# Function to time a command
time_command() {
    local description="$1"
    shift
    local cmd=("$@")
    
    echo "  $description..." >&2  # Send to stderr so it doesn't interfere with return value
    printf "    Command: %s\n" "${cmd[*]}" >&2  # Show the full command
    
    local start_time=$(date +%s.%N)
    
    if "${cmd[@]}" > /dev/null 2>&1; then
        local end_time=$(date +%s.%N)
        # Use awk instead of bc for better compatibility
        local duration=$(awk "BEGIN {printf \"%.2f\", ${end_time} - ${start_time}}")
        printf "    Completed in %s seconds\n" "$duration" >&2  # Send to stderr
        echo "$duration"  # Only the numeric value goes to stdout
    else
        print_error "    Command failed!" >&2  # Send to stderr
        echo "0"  # Return 0 instead of failing, so math doesn't break
        return 1
    fi
}

# Function to demonstrate separated approach
demo_separated_approach() {
    print_header "============================================================"
    print_header "DEMONSTRATING SEPARATED APPROACH (Current MIMI Design)"
    print_header "============================================================"
    echo "Scenario: Create cache once, then analyze multiple samples"
    echo ""

    # Step 1: Create cache once
    local cache_file="$OUTPUT_DIR/demo_cache"
    local cache_pkl="${cache_file}.pkl"
    
    # Clean up any existing cache
    [ -f "$cache_pkl" ] && rm -f "$cache_pkl"

    print_header "Step 1: Create cache (one-time cost)"
    local cache_time
    cache_time=$(time_command "Creating database cache" \
        mimi_cache_create -i neg -d "$DB_FILE" -c "$cache_file")
    
    if [ $? -ne 0 ]; then
        print_error "Cache creation failed!"
        exit 1
    fi

    # Check cache file size
    if [ -f "$cache_pkl" ]; then
        local cache_size=$(du -h "$cache_pkl" | cut -f1)
        echo "    Cache file size: $cache_size"
    fi

    echo ""
    print_header "Step 2: Run multiple analyses using pre-created cache"
    
    local analysis_times=()
    local total_analysis_time="0.00"
    
    for i in {1..3}; do
        local output_file="$OUTPUT_DIR/separated_analysis_${i}.tsv"
        [ -f "$output_file" ] && rm -f "$output_file"
        
        local analysis_time
        analysis_time=$(time_command "Analysis run $i" \
            mimi_mass_analysis -p 1.0 -vp 1.0 -c "$cache_file" -s "$SAMPLE_FILE" -o "$output_file")
        local cmd_status=$?
        
        if [ $cmd_status -eq 0 ] && [ "$analysis_time" != "0" ]; then
            analysis_times+=("$analysis_time")
            total_analysis_time=$(awk "BEGIN {printf \"%.2f\", ${total_analysis_time} + ${analysis_time}}")
        else
            print_warning "    Skipping failed analysis run $i"
        fi
    done

    # Calculate statistics
    local num_analyses=${#analysis_times[@]}
    if [ $num_analyses -gt 0 ]; then
        local avg_analysis_time=$(awk "BEGIN {printf \"%.2f\", ${total_analysis_time} / ${num_analyses}}")
        local total_time=$(awk "BEGIN {printf \"%.2f\", ${cache_time} + ${total_analysis_time}}")
        
        echo ""
        print_success "Separated Approach Results:"
        printf "  Cache creation (one-time): %.2f seconds\n" "$cache_time"
        printf "  Average analysis time: %.2f seconds\n" "$avg_analysis_time"
        printf "  Total time for %d analyses: %.2f seconds\n" "$num_analyses" "$total_time"
        printf "  Analysis efficiency: %.2f seconds per sample\n" "$avg_analysis_time"
        
        # Store results for comparison
        echo "$cache_time" > "$OUTPUT_DIR/separated_cache_time.txt"
        echo "$total_analysis_time" > "$OUTPUT_DIR/separated_analysis_time.txt"
        echo "$num_analyses" > "$OUTPUT_DIR/separated_count.txt"
    else
        print_error "No successful analysis runs!"
        exit 1
    fi
}

# Function to demonstrate combined approach
demo_combined_approach() {
    print_header ""
    print_header "============================================================"
    print_header "DEMONSTRATING COMBINED APPROACH (Hypothetical Old Design)"
    print_header "============================================================"
    echo "Scenario: Create cache + analyze together each time"
    echo ""

    local combined_times=()
    local total_combined_time="0.00"
    
    for i in {1..3}; do
        print_header "Combined Run $i: Cache creation + Analysis"
        
        # Create cache
        local cache_file="$OUTPUT_DIR/combined_cache_${i}"
        local cache_pkl="${cache_file}.pkl"
        [ -f "$cache_pkl" ] && rm -f "$cache_pkl"
        
        local cache_time
        cache_time=$(time_command "Cache creation for run $i" \
            mimi_cache_create -i neg -d "$DB_FILE" -c "$cache_file")
        local cache_status=$?
        
        if [ $cache_status -ne 0 ] || [ "$cache_time" = "0" ]; then
            print_warning "    Skipping failed cache creation for run $i"
            continue
        fi

        # Run analysis immediately
        local output_file="$OUTPUT_DIR/combined_analysis_${i}.tsv"
        [ -f "$output_file" ] && rm -f "$output_file"
        
        local analysis_time
        analysis_time=$(time_command "Analysis for run $i" \
            mimi_mass_analysis -p 1.0 -vp 1.0 -c "$cache_file" -s "$SAMPLE_FILE" -o "$output_file")
        local analysis_status=$?
        
        if [ $analysis_status -eq 0 ] && [ "$analysis_time" != "0" ]; then
            local combined_time=$(awk "BEGIN {printf \"%.2f\", ${cache_time} + ${analysis_time}}")
            combined_times+=("$combined_time")
            total_combined_time=$(awk "BEGIN {printf \"%.2f\", ${total_combined_time} + ${combined_time}}")
            printf "  Combined time for run %d: %.2f seconds (cache: %.2f + analysis: %.2f)\n" \
                "$i" "$combined_time" "$cache_time" "$analysis_time"
        else
            print_warning "    Skipping failed analysis for run $i"
        fi
        echo ""
    done

    # Calculate statistics
    local num_combined=${#combined_times[@]}
    if [ $num_combined -gt 0 ]; then
        local avg_combined_time=$(awk "BEGIN {printf \"%.2f\", ${total_combined_time} / ${num_combined}}")
        
        echo ""
        print_success "Combined Approach Results:"
        printf "  Average time per combined run: %.2f seconds\n" "$avg_combined_time"
        printf "  Total time for %d analyses: %.2f seconds\n" "$num_combined" "$total_combined_time"
        printf "  Inefficiency: Cache recreated %d times\n" "$num_combined"
        
        # Store results for comparison
        echo "$total_combined_time" > "$OUTPUT_DIR/combined_total_time.txt"
        echo "$num_combined" > "$OUTPUT_DIR/combined_count.txt"
    else
        print_error "No successful combined runs!"
        exit 1
    fi
}

# Function to show comparison
show_comparison() {
    print_header ""
    print_header "============================================================"
    print_header "PERFORMANCE COMPARISON AND ANALYSIS"
    print_header "============================================================"

    # Read stored results
    if [ ! -f "$OUTPUT_DIR/separated_cache_time.txt" ] || [ ! -f "$OUTPUT_DIR/combined_total_time.txt" ]; then
        print_error "Cannot compare approaches - missing result files"
        return 1
    fi

    # Read and clean values from files
    local separated_cache_time=$(cat "$OUTPUT_DIR/separated_cache_time.txt" | tr -d '\n\r\t ' | sed 's/[^0-9.]//g')
    local separated_analysis_time=$(cat "$OUTPUT_DIR/separated_analysis_time.txt" | tr -d '\n\r\t ' | sed 's/[^0-9.]//g')
    local separated_count=$(cat "$OUTPUT_DIR/separated_count.txt" | tr -d '\n\r\t ' | sed 's/[^0-9]//g')
    local combined_total_time=$(cat "$OUTPUT_DIR/combined_total_time.txt" | tr -d '\n\r\t ' | sed 's/[^0-9.]//g')
    local combined_count=$(cat "$OUTPUT_DIR/combined_count.txt" | tr -d '\n\r\t ' | sed 's/[^0-9]//g')

    # Validate that we have numeric values
    if [[ ! "$separated_cache_time" =~ ^[0-9]+\.?[0-9]*$ ]] || [[ ! "$separated_analysis_time" =~ ^[0-9]+\.?[0-9]*$ ]] || \
       [[ ! "$separated_count" =~ ^[0-9]+$ ]] || [[ ! "$combined_total_time" =~ ^[0-9]+\.?[0-9]*$ ]] || \
       [[ ! "$combined_count" =~ ^[0-9]+$ ]]; then
        print_error "Error: Invalid numeric values in result files"
        echo "Debug values:"
        echo "  separated_cache_time: '$separated_cache_time'"
        echo "  separated_analysis_time: '$separated_analysis_time'"
        echo "  separated_count: '$separated_count'"
        echo "  combined_total_time: '$combined_total_time'"
        echo "  combined_count: '$combined_count'"
        return 1
    fi

    # Use string interpolation to avoid awk syntax issues
    local separated_total=$(awk "BEGIN {printf \"%.2f\", ${separated_cache_time} + ${separated_analysis_time}}")
    local avg_separated_analysis=$(awk "BEGIN {printf \"%.2f\", ${separated_analysis_time} / ${separated_count}}")
    local avg_combined_total=$(awk "BEGIN {printf \"%.2f\", ${combined_total_time} / ${combined_count}}")

    local time_saved=$(awk "BEGIN {printf \"%.2f\", ${combined_total_time} - ${separated_total}}")
    local efficiency_gain=$(awk "BEGIN {printf \"%.1f\", (${time_saved} / ${combined_total_time}) * 100}")
    local speedup=$(awk "BEGIN {printf \"%.1f\", ${combined_total_time} / ${separated_total}}")
    local analysis_time_diff=$(awk "BEGIN {printf \"%.2f\", ${combined_total_time} / ${combined_count} - ${separated_analysis_time} / ${separated_count}}")

    echo "Detailed Comparison:"
    printf "%-30s %-15s %-15s %-15s\n" "Metric" "Separated" "Combined" "Difference"
    echo "-----------------------------------------------------------------------"
    printf "%-30s %-15.2f %-15s %-15s\n" "Cache creation time" "$separated_cache_time" "N/A (embedded)" ""
    printf "%-30s %-15.2f %-15.2f %-15.2f\n" "Avg analysis time" "$avg_separated_analysis" "$avg_combined_total" "$analysis_time_diff"
    printf "%-30s %-15.2f %-15.2f %-15.2f\n" "Total time" "$separated_total" "$combined_total_time" "$time_saved"
    echo ""

  
}

# Main execution function
run_demo() {
    print_header "MIMI Performance Benefits Demonstration"
    print_header "============================================================"
    echo "This demo shows why separating cache creation from analysis is beneficial"
    echo "Using data from: $DATA_DIR"
    echo "Output directory: $OUTPUT_DIR"
    echo ""

    # Note: Using awk for calculations (more portable than bc)

    # Run demonstrations
    demo_separated_approach
    demo_combined_approach
    show_comparison

}

# Main script execution
main() {
    setup_demo "$@"
    check_mimi_commands
    run_demo
}

# Run main function with all arguments
main "$@"
