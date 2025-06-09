# Copyright 2025 New York University. All Rights Reserved.

# A license to use and copy this software and its documentation solely for your internal non-commercial
# research and evaluation purposes, without fee and without a signed licensing agreement, is hereby granted
# upon your download of the software, through which you agree to the following: 1) the above copyright
# notice, this paragraph and the following three paragraphs will prominently appear in all internal copies
# and modifications; 2) no rights to sublicense or further distribute this software are granted; 3) no rights
# to modify this software are granted; and 4) no rights to assign this license are granted. Please contact
# the NYU Technology Opportunities and Ventures TOVcommunications@nyulangone.org for commercial
# licensing opportunities, or for further distribution, modification or license rights.

# Created by Nabil Rahiman & Kristin Gunsalus

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

"""
Cache Dump Module

This module provides functionality for dumping the contents of a MIMI cache file
to TSV format for inspection.
"""

# Copyright 2025 New York University. All Rights Reserved.
# ... [License text skipped for brevity] ...

import argparse
import pickle
import sys
from itertools import islice
from mimi import atom

def format_cf_with_masses(cf):
    """Format chemical formula with nominal masses in square brackets.
    
    Args:
        cf (str): Original chemical formula (e.g., 'C6H12O6')
        
    Returns:
        str: Formatted formula with masses (e.g., '[12]C6[1]H12[16]O6')
    """
    formatted = ''
    atom_name = ''
    count = ''
    
    i = 0
    while i < len(cf):
        c = cf[i]
        
        # Handle numbers
        if c.isdigit():
            count += c
            i += 1
            continue
            
        # If we have a lowercase letter, it's part of a two-letter element
        if c.islower() and atom_name:
            atom_name += c
            i += 1
            continue
            
        # If we have an existing atom_name, process it before starting new one
        if atom_name:
            atom_data = atom.get_atom(atom_name)
            nominal_mass = atom_data[0]['nominal_mass']
            formatted += f'[{nominal_mass}]{atom_name}'
            if count:
                formatted += count
                count = ''
            atom_name = ''
        
        # Start new atom
        if c.isupper():
            atom_name = c
            
        i += 1
    
    # Handle the last atom
    if atom_name:
        atom_data = atom.get_atom(atom_name)
        nominal_mass = atom_data[0]['nominal_mass']
        formatted += f'[{nominal_mass}]{atom_name}'
        if count:
            formatted += count
    
    return formatted

def dump_cache(cache_file, num_compounds=None, output_file=None, num_isotopes=None):
    """Dump contents of a MIMI cache file to TSV format.
    
    Args:
        cache_file (str): Path to the .pkl cache file
        num_compounds (int, optional): Number of compounds to output. If None, outputs all.
        output_file (str, optional): Path to output file. If None, prints to stdout.
        num_isotopes (int, optional): Number of isotopes per compound to output. If None, outputs all.
    """
    # Load isotope data with default isotope file
    atom.load_isotope()
    
    # Load cache data
    with open(cache_file, 'rb') as f:
        cache_data = pickle.load(f)
        
    # Handle metadata if present (newer cache format)
    compounds = cache_data.get('compounds', cache_data)
    metadata = cache_data.get('metadata', {})
    
    # Prepare output file handle
    out = open(output_file, 'w') if output_file else sys.stdout
    
    try:
        # Print metadata if available
        if metadata:
            print("# Cache Metadata:", file=out)
            # Print creation info
            print(f"# Creation Date: {metadata.get('creation_date', 'Unknown')}", file=out)
            print(f"# MIMI Version: {metadata.get('mimi_version', 'Unknown')}", file=out)
            
            # Print command line parameters
            cmd_line = metadata.get('command_line', {})
            if cmd_line:
                print("\n# Creation Parameters:", file=out)
                print(f"# Full Command: {cmd_line.get('full_command', 'Unknown')}", file=out)
                print(f"# Ionization Mode: {cmd_line.get('ionization_mode', 'Unknown')}", file=out)
                print(f"# Labeled Atoms File: {cmd_line.get('labeled_atoms_file', 'None')}", file=out)
                print(f"# Compound DB Files: {', '.join(cmd_line.get('compound_db_files', ['Unknown']))}", file=out)
                print(f"# Cache Output File: {cmd_line.get('cache_output_file', 'Unknown')}", file=out)
                print(f"# Isotope Data File: {cmd_line.get('isotope_data_file', 'Unknown')}", file=out)
            
            print(file=out)
        
        # Get compounds to process
        compounds_iter = compounds.items()
        if num_compounds:
            compounds_iter = islice(compounds_iter, num_compounds)
            
        # Print compound data with improved formatting
        for compound_id, data in compounds_iter:
            # Print main compound entry (mono-isotopic mass)
            formatted_cf = format_cf_with_masses(data['cf'])
            
            print("=" * 60, file=out)
            print(f"Compound ID:      {compound_id}", file=out)
            print(f"Name:             {data['cname']}", file=out)
            print(f"Formula:          {formatted_cf}", file=out)
            print(f"Mono-isotopic:    Yes (most abundant isotope)", file=out)
            print(f"Mass:             {data['mass']:.6f}", file=out)
            print(f"Relative Abund:   1.000000 (reference)", file=out)
            print("-" * 60, file=out)
            
            # Print isotope variants
            isotopes = data['isotope_mass_list'][1:]  # Skip first entry (main compound)
            if num_isotopes:
                isotopes = isotopes[:num_isotopes]
            
            if isotopes:
                print("ISOTOPE VARIANTS:", file=out)
                
            for i, (mass, abundance, isotope_formula) in enumerate(isotopes, 1):
                print(f"  Variant #{i}:", file=out)
                print(f"  Formula:        {isotope_formula.strip()}", file=out)
                print(f"  Mono-isotopic:  No (isotope variant)", file=out)
                print(f"  Mass:           {mass:.6f}", file=out)
                print(f"  Relative Abund: {abundance:.6f} (expected)", file=out)
                print("-" * 60, file=out)
            
            print(file=out)  # Add extra line between compounds
            
    finally:
        if output_file:
            out.close()

def main():
    """Main entry point for the cache dump tool."""
    ap = argparse.ArgumentParser(description="MIMI Cache Dump Tool")
    
    ap.add_argument("cache_file", help="Input cache file (.pkl)")
    ap.add_argument("-n", "--num-compounds", type=int,
                    help="Number of compounds to output (default: all)")
    ap.add_argument("-i", "--num-isotopes", type=int,
                    help="Number of isotopes per compound to output (default: all)")
    ap.add_argument("-o", "--output", help="Output file (default: stdout)")
    
    
    args = ap.parse_args()
    
    try:
        dump_cache(args.cache_file, args.num_compounds, args.output, args.num_isotopes)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 