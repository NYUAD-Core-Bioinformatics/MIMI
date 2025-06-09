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

import xml.etree.ElementTree as ET
from typing import List, Tuple
import os
import sys
import argparse
from mimi.molecule import parse_molecular_formula
from mimi.atom import load_isotope
from datetime import datetime


def parse_hmdb_xml(xml_file, min_mass=None, max_mass=None):
    """
    Parse HMDB metabolites XML file and extract relevant information.
    
    Args:
        xml_file: Path to the HMDB metabolites XML file
        min_mass: Minimum molecular weight to include (optional)
        max_mass: Maximum molecular weight to include (optional)
        
    Returns:
        Tuple containing:
        - List of tuples (chemical_formula, metabolite_id, name)
        - Number of skipped metabolites
        - Total number of processed metabolites
    """
    # Define the namespace
    ns = {'hmdb': 'http://www.hmdb.ca'}
    
    metabolites = []
    skipped_count = 0
    incomplete_count = 0
    
    try:
        # Use iterparse to process the XML file incrementally
        context = ET.iterparse(xml_file, events=('end',))
        
        # Track current metabolite data
        metabolite_id = None
        name = None
        chemical_formula = None
        mol_weight = None
        
        # Setup progress tracking
        processed_count = 0
        print("Parsing metabolites...")
        
        for event, elem in context:
            # Check if this is a metabolite element
            if elem.tag == f"{{{ns['hmdb']}}}metabolite":
                # Process the complete metabolite
                processed_count += 1
                
                if not all(x is not None for x in [metabolite_id, name, chemical_formula, mol_weight]):
                    incomplete_count += 1
                else:
                    # Check mass range if filtering is enabled
                    if min_mass is not None or max_mass is not None:
                        if mol_weight is None or \
                           (min_mass is not None and mol_weight < min_mass) or \
                           (max_mass is not None and mol_weight > max_mass):
                            skipped_count += 1
                        else:
                            # Only include if formula can be parsed successfully
                            try:
                                # Attempt to parse the formula
                                parse_molecular_formula(chemical_formula)
                                
                                # If successful, add to metabolites list
                                metabolites.append((chemical_formula, metabolite_id, name))
                            except KeyError:
                                skipped_count += 1
                    else:
                        # No mass filtering, just check formula
                        try:
                            parse_molecular_formula(chemical_formula)
                            metabolites.append((chemical_formula, metabolite_id, name))
                        except KeyError:
                            skipped_count += 1
                
                # Update progress
                if processed_count % 100 == 0:
                    print(f"\rProcessed metabolites in HMDB file...{processed_count}", end="", flush=True)
                
                # Reset for next metabolite
                metabolite_id = None
                name = None
                chemical_formula = None
                mol_weight = None
                
                # Clear the element to free memory
                elem.clear()
                
            elif elem.tag == f"{{{ns['hmdb']}}}accession" and elem.text:
                metabolite_id = elem.text
            elif elem.tag == f"{{{ns['hmdb']}}}name" and elem.text:
                name = elem.text
            elif elem.tag == f"{{{ns['hmdb']}}}chemical_formula" and elem.text:
                chemical_formula = elem.text
            elif elem.tag == f"{{{ns['hmdb']}}}average_molecular_weight" and elem.text:
                try:
                    mol_weight = float(elem.text)
                except ValueError:
                    mol_weight = None
        
        # Print newline after progress bar completes
        print()
        
        # Add incomplete count to skipped count for total
        skipped_count += incomplete_count
        
        return metabolites, skipped_count, processed_count
        
    except FileNotFoundError:
        print(f"Error: File '{xml_file}' not found.")
        sys.exit(1)


def get_hmdb_info(xml_file):
    """
    Get HMDB version and creation date from the XML file.
    
    Args:
        xml_file: Path to the HMDB metabolites XML file
        
    Returns:
        tuple: (version, creation_date, update_date) or None if not found
    """
    try:
        # Define namespace
        ns = {'hmdb': 'http://www.hmdb.ca'}
        
        # Use iterparse to get just the first metabolite
        context = ET.iterparse(xml_file, events=('end',))
        
        # Track metadata fields
        version = None
        creation_date = None
        update_date = None
        
        for event, elem in context:
            if elem.tag == f"{{{ns['hmdb']}}}version":
                version = elem.text
            elif elem.tag == f"{{{ns['hmdb']}}}creation_date":
                creation_date = elem.text
            elif elem.tag == f"{{{ns['hmdb']}}}update_date":
                update_date = elem.text
            elif elem.tag == f"{{{ns['hmdb']}}}metabolite":
                # We've processed one complete metabolite, we can stop
                break
            
            # Clear element to free memory
            elem.clear()
        
        # Check each field and log if missing
        missing_fields = []
        if not version:
            missing_fields.append("version")
        if not creation_date:
            missing_fields.append("creation_date")
        if not update_date:
            missing_fields.append("update_date")
        
        if missing_fields:
            print(f"Warning: Missing HMDB metadata fields: {', '.join(missing_fields)}")
        
        return (version or "Unknown",
                creation_date or "Unknown",
                update_date or "Unknown")
        
    except Exception as e:
        print(f"Warning: Could not extract HMDB version info: {str(e)}")
        return None


def export_metabolites_to_tsv(xml_file, output_file, min_mass=None, max_mass=None):
    """
    Parse HMDB metabolites and export to TSV format.
    
    Args:
        xml_file: Path to the HMDB metabolites XML file
        output_file: Path where the TSV file should be saved
        min_mass: Minimum molecular weight to include (optional)
        max_mass: Maximum molecular weight to include (optional)
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            except OSError as e:
                print(f"Error: Failed to create output directory '{output_dir}': {str(e)}")
                sys.exit(1)

        # Get HMDB version info before parsing all metabolites
        hmdb_info = get_hmdb_info(xml_file)
        
        try:
            with open(output_file, "w", encoding='utf-8') as f:
                # Write run date
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"# Run Date: {current_time}\n")
                
                # Write command line arguments - use just the command name
                cmd_name = os.path.basename(sys.argv[0])
                cmd_args = [cmd_name] + sys.argv[1:]
                f.write(f"# Command: {' '.join(cmd_args)}\n")



                
                # Reserve space for metabolite counts with placeholder
                counts_pos = f.tell()
                placeholder = "# Number of metabolites: {:<10}\n"
                f.write(placeholder.format("", ""))
                
                # Write HMDB info
                f.write("# HMDB Metabolites Database\n")
                if hmdb_info:
                    version, creation_date, update_date = hmdb_info
                    if version != "Unknown":
                        f.write(f"# Version: {version}\n")
                    if creation_date != "Unknown":
                        f.write(f"# HMDB XML Database Creation: {creation_date}\n")
                    if update_date != "Unknown":
                        f.write(f"# HMDB XML Database Last Update: {update_date}\n")
                else:
                    f.write("# Database version information not found in XML file\n")
                
                if min_mass is not None or max_mass is not None:
                    mass_range_str = f"{min_mass if min_mass is not None else 'any'} to {max_mass if max_mass is not None else 'any'}"
                    f.write(f"# Mass range: {mass_range_str} Da\n")
                f.write("#\n")
                
                f.write("CF\tID\tName\n")
                
                # Parse and write metabolites
                metabolite_data, skipped_count, processed_count = parse_hmdb_xml(xml_file, min_mass, max_mass)
                for cf, met_id, met_name in metabolite_data:
                    f.write(f"{cf}\t{met_id}\t{met_name}\n")
                
                # Count valid metabolites
                valid_count = len(metabolite_data)
                
            # Reopen file to update the counts
            with open(output_file, 'r+') as f:
                f.seek(counts_pos)
                f.write( placeholder.format(str(valid_count)))
            
            print(f"\nMetabolite data saved to {output_file}")
            print(f"Total valid metabolites: {valid_count}")
            print(f"Total skipped metabolites: {skipped_count}")
            
        except IOError as e:
            print(f"Error: Failed to write to output file '{output_file}': {str(e)}")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        sys.exit(1)


def main():
    """Command line interface for HMDB metabolites extraction."""
    parser = argparse.ArgumentParser(description='Extract metabolite information from HMDB XML file')
    parser.add_argument('-x', '--xml', required=True,
                      help='Path to HMDB metabolites XML file')
    parser.add_argument('-l', '--min-mass', type=float,
                      help='Lower bound of molecular weight in Da')
    parser.add_argument('-u', '--max-mass', type=float,
                      help='Upper bound of molecular weight in Da')
    parser.add_argument('-o', '--output', default='metabolites.tsv',
                      help='Output TSV file path (default: metabolites.tsv)')
    
    args = parser.parse_args()
    
    load_isotope()
    export_metabolites_to_tsv(args.xml, args.output, args.min_mass, args.max_mass)
    print(f"Extracted data saved to {args.output}")


if __name__ == '__main__':
    main() 