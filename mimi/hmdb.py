import xml.etree.ElementTree as ET
from typing import List, Tuple
import os
import sys
import argparse
from mimi.molecule import parse_molecular_formula
from mimi.atom import load_isotope


def parse_hmdb_xml(xml_file, min_mass=None, max_mass=None):
    """
    Parse HMDB metabolites XML file and extract relevant information.
    
    Args:
        xml_file: Path to the HMDB metabolites XML file
        min_mass: Minimum molecular weight to include (optional)
        max_mass: Maximum molecular weight to include (optional)
        
    Returns:
        List of tuples containing (chemical_formula, metabolite_id, name)
        Only includes entries with valid chemical formulas that can be parsed.
        If mass range is specified, only includes metabolites within that range.
    """
    # Define the namespace
    ns = {'hmdb': 'http://www.hmdb.ca'}
    
    
    # Count total number of metabolites first
    total_metabolites = 0
   

    metabolites = []
    skipped_formulas = []
    skipped_mass_range = 0
    
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
                if all(x is not None for x in [metabolite_id, name, chemical_formula]):
                    # Check mass range if filtering is enabled
                    if min_mass is not None or max_mass is not None:
                        if mol_weight is None or \
                           (min_mass is not None and mol_weight < min_mass) or \
                           (max_mass is not None and mol_weight > max_mass):
                            skipped_mass_range += 1
                        else:
                            # Only include if formula can be parsed successfully
                            try:
                                # Attempt to parse the formula
                                parse_molecular_formula(chemical_formula)
                                
                                # If successful, add to metabolites list
                                metabolites.append((chemical_formula, metabolite_id, name))
                            except KeyError as e:                   
                                # Log the failed formula
                                skipped_formulas.append((chemical_formula, metabolite_id, name, str(e)))
                    else:
                        # No mass filtering, just check formula
                        try:
                            parse_molecular_formula(chemical_formula)
                            metabolites.append((chemical_formula, metabolite_id, name))
                        except KeyError as e:
                           
                           
                            skipped_formulas.append((chemical_formula, metabolite_id, name, str(e)))
                
                # Update progress
                processed_count += 1
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
                mol_weight = float(elem.text)
            else:
                mol_weight = None
        
        # Print newline after progress bar completes
        print()
        
        # Print summary of skipped formulas
        if skipped_formulas:
            print(f"\nSkipped {len(skipped_formulas)} metabolites with unparseable chemical formulas:")
            for cf, met_id, met_name, error in skipped_formulas:
                print(f"  - {met_id} ({met_name}): Formula '{cf}' - Error: {error}")
        
        # Print summary of mass range filtering
        if min_mass is not None or max_mass is not None:
            mass_range_str = f"{min_mass if min_mass is not None else 'any'} to {max_mass if max_mass is not None else 'any'}"
            print(f"\nSkipped {skipped_mass_range} metabolites outside mass range ({mass_range_str})")
        
        # Print total metabolites extracted
        print(f"\nTotal metabolites successfully extracted: {len(metabolites)}")
        
        return metabolites
    except FileNotFoundError:
        print(f"Error: File '{xml_file}' not found.")
        sys.exit(1)


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
        metabolite_data = parse_hmdb_xml(xml_file, min_mass, max_mass)
        
        with open(output_file, "w", encoding='utf-8') as f:
            f.write("CF\tID\tname\n")
            for cf, met_id, met_name in metabolite_data:
                f.write(f"{cf}\t{met_id}\t{met_name}\n")
    except FileNotFoundError as e:
        print(f"Error: {e}")
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