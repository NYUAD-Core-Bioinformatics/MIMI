"""
Cache Creation Module

This module provides functionality for creating precomputed caches of molecular
mass data to speed up analysis.

Functions:
    load_mass_spectrometry_data: Load mass intensity data from mass spectrometry output
    main: Main entry point for cache creation tool
"""

# Copyright 2020 New York University. All Rights Reserved.

# A license to use and copy this software and its documentation solely for your internal non-commercial
# research and evaluation purposes, without fee and without a signed licensing agreement, is hereby granted
# upon your download of the software, through which you agree to the following: 1) the above copyright
# notice, this paragraph and the following three paragraphs will prominently appear in all internal copies
# and modifications; 2) no rights to sublicense or further distribute this software are granted; 3) no rights
# to modify this software are granted; and 4) no rights to assign this license are granted. Please contact
# the NYU Technology Opportunities and Ventures TOVcommunications@nyulangone.org for commercial
# licensing opportunities, or for further distribution, modification or license rights.

# Created by Lior Galanti & Kristin Gunsalus

# IN NO EVENT SHALL NYU, OR THEIR EMPLOYEES, OFFICERS, AGENTS OR TRUSTEES
# ("COLLECTIVELY "NYU PARTIES") BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
# INCIDENTAL, OR CONSEQUENTIAL DAMAGES OF ANY KIND, INCLUDING LOST PROFITS, ARISING
# OUT OF ANY CLAIM RESULTING FROM YOUR USE OF THIS SOFTWARE AND ITS
# DOCUMENTATION, EVEN IF ANY OF NYU PARTIES HAS BEEN ADVISED OF THE POSSIBILITY
# OF SUCH CLAIM OR DAMAGE.

# NYU SPECIFICALLY DISCLAIMS ANY WARRANTIES OF ANY KIND REGARDING THE SOFTWARE,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, OR THE ACCURACY OR USEFULNESS,
# OR COMPLETENESS OF THE SOFTWARE. THE SOFTWARE AND ACCOMPANYING DOCUMENTATION,
# IF ANY, PROVIDED HEREUNDER IS PROVIDED COMPLETELY "AS IS". NYU HAS NO OBLIGATION TO PROVIDE
# FURTHER DOCUMENTATION, MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS

from mimi.molecule import *
import pickle

from mimi.analysis import *

import json
import argparse
import sys
import datetime
import pkg_resources
import os
import tqdm  # Import tqdm for progress bar


def load_mass_spectrometry_data(asc_file):
    """Load mass intensity data from mass spectrometry output file.
    
    Reads tab-separated mass-intensity pairs from an ASC format file and returns them
    as a list of pairs.
    
    Args:
        asc_file (str): Path to ASC format mass spectrometry output file
        
    Returns:
        list: List of [mass, intensity] pairs from the spectrometry data, where each
            pair contains strings representing the mass and intensity values
    """
    mass_intensity_pair_list = [] 
    fd = open(asc_file)
    for line in fd:
        line = line.strip()
        mass_intensity_pair_list.append(line.split('\t'))
    return mass_intensity_pair_list



def main():
    """Main entry point for the cache creation tool.
    
    Creates a precomputed cache of molecular mass data to speed up later analysis.
    For each compound in the input database(s), this function:
    1. Parses its molecular formula
    2. Calculates its nominal mass based on ionization mode
    3. Computes isotope variant masses
    4. Stores results in a dictionary
    5. Saves the cache to a pickle file
    
    Command line arguments:
        -i, --ion: Ionisation mode (pos/neg/)
        -l, --label: Path to JSON file containing labeled atoms configuration
        -g, --debug: Enable debug output
        -d, --dbfile: Input database TSV file(s) with compound information (can specify multiple)
        -c, --cache: Output path for the binary cache file (.pkl extension will be added)
    """
    ap = argparse.ArgumentParser(
        description="Molecular Isotope Mass Identifier",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Debug mode
    ap.add_argument("-g", '--debug', dest="debug",
                    action='store_true', default=False, help=argparse.SUPPRESS)
    
    # Input configuration
    ap.add_argument("-l", "--label", dest="jsonfile",
                    help="Labeled atoms", metavar="JSON")
    ap.add_argument("-d", "--dbfile", dest="dbfile", nargs='+',
                    help="File(s) with list of compounds", metavar="DBTSV", required=True)
    
    ap.add_argument("-n", "--noise", dest="noise_cutoff", type=float, default=1e5, metavar="CUTOFF",
                    help="Noise cutoff threshold (default: 1e5). Ignores isotope variants with relative abundance below 1/CUTOFF", required=False)
    
    # Processing options
    ap.add_argument("-i", '--ion', dest="ion",
                    help="Ionisation mode", choices=['pos','neg'], required=True)
    
    # Output
    ap.add_argument("-c", "--cache", dest="cache",
                    help="Binary DB output file (if not specified, will use base name from JSON file)", metavar="DBBINARY")

    args = ap.parse_args()

    # If cache not specified, derive it from JSON file
    if not args.cache:
        if not args.jsonfile:
            print("Error: Either -c/--cache must be specified or -l/--label must be provided to derive cache name", file=sys.stderr)
            sys.exit(1)
        args.cache = os.path.splitext(os.path.basename(args.jsonfile))[0]
    else:
        base_name = os.path.splitext(os.path.basename(args.cache))[0]
        if base_name == '':
            args.cache = os.path.join(args.cache, os.path.splitext(os.path.basename(args.jsonfile))[0])
            

    # Create log directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), 'log')
    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Failed to create log directory '{log_dir}': {str(e)}")
        sys.exit(1)

    # Setup debug log file if debug mode is enabled
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    debug_file = os.path.join(log_dir, f"{base_name}_{timestamp}.debug") if args.debug else None
    log_file = os.path.join(log_dir, f"{base_name}_{timestamp}.log") if args.debug else None

    # Update metadata to include computation method
    metadata = {
        'command_line': {
            'ionization_mode': args.ion,
            'labeled_atoms_file': args.jsonfile if args.jsonfile else None,
            'compound_db_files': args.dbfile,
            'cache_output_file': args.cache + '.pkl',
            'isotope_data_file': 'mimi/data/natural_isotope_abundance_NIST.json',
            'full_command': ' '.join(sys.argv)
        },
        'creation_date': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'mimi_version': pkg_resources.get_distribution('mimi').version
    }

    # Open debug file if in debug mode and attach to args object
    if args.debug:
        try:
            args.debug_fp = open(debug_file, 'w')
        except IOError as e:
            print(f"Error: Failed to create debug file '{debug_file}': {str(e)}")
            sys.exit(1)
    else:
        args.debug_fp = None

    # Use default isotope file path
    atom.load_isotope()

    if args.jsonfile:
        try:
            atom.load_labelled_atoms(args.jsonfile)
        except ValueError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    


    compound_list = []
    for dbfile in args.dbfile:
        try:
            compound_list.extend(load_molecular_mass_database(dbfile))
        except FileNotFoundError:
            print(f"Error: Database file not found: '{dbfile}'", file=sys.stderr)
            sys.exit(1)


   
    ion = args.ion
    compound_precompute = {
        'metadata': metadata,  # Add metadata to cache
        'compounds': {}       # Store compounds in nested dict
    }

    skipped_compounds = []  # Track skipped compounds
    
    # Add progress bar
    progress_bar = tqdm.tqdm(compound_list, desc="Processing compounds", unit="compound")
    for cf, co, cname in progress_bar:
        try:
            if args.debug:
                args.debug_fp.write(f"\nProcessing compound: {cf} ({co})\n")
                args.debug_fp.write("-" * 50 + "\n")
            
            # Update progress bar description with current compound
            progress_bar.set_description(f"Processing {co}")

            exp = parse_molecular_formula(cf)  # First parse the formula
            
            if args.debug:
                args.debug_fp.write(f"Calculating nominal mass for {ion} mode...\n")

            nominal_mass = calculate_nominal_mass(exp, ion)

            if args.debug:
                args.debug_fp.write(f"Nominal mass: {nominal_mass}\n")
                args.debug_fp.write("Calculating isotope variants...\n")

            isotope_variants = get_isotop_variants_mass(exp, ion, args)


            compound_precompute['compounds'][co] = {
                'cf': cf,
                'cname': cname,
                'exp': exp,
                'mass': nominal_mass,
                'isotope_mass_list': isotope_variants
            }

        except KeyError as e:
            # Log unsupported formula to debug file and continue
            if args.debug:
                args.debug_fp.write(f"ERROR: Unsupported molecular formula format: {cf}\n")
                args.debug_fp.write(f"Exception: {str(e)}\n")
            skipped_compounds.append(cf)
            continue

    if skipped_compounds and args.debug:
        args.debug_fp.write("\nSummary of skipped compounds:\n")
        args.debug_fp.write("-" * 30 + "\n")
        for cf in skipped_compounds:
            args.debug_fp.write(f"- {cf}\n")
        args.debug_fp.write(f"\nTotal skipped: {len(skipped_compounds)}\n")

    # Close debug file if it was opened
    if args.debug_fp:
        args.debug_fp.close()

    try:
        # Create cache directory if it doesn't exist
        cache_dir = os.path.dirname(args.cache)
        if cache_dir and not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir)
                print(f"Created cache directory: {cache_dir}")
            except OSError as e:
                print(f"Error: Failed to create cache directory '{cache_dir}': {str(e)}")
                sys.exit(1)

        with open(args.cache + '.pkl','wb') as f:
            pickle.dump(compound_precompute, f)
    except IOError as e:
        print(f"Error: Failed to write cache file '{args.cache}.pkl': {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()