import requests
import time
from tqdm import tqdm
import sys
from mimi.molecule import parse_molecular_formula
from mimi.atom import load_isotope
import argparse
import pandas as pd

def get_compounds_by_mass_range(min_mass, max_mass, chunk_size=50.0):
    """
    Get a list of KEGG compound IDs within specified mass range.
    Breaks large mass ranges into smaller chunks to handle KEGG's 10,000 result limit.
    Skips duplicates while processing.
    
    Args:
        min_mass: Minimum mass in Da
        max_mass: Maximum mass in Da
        chunk_size: Size of mass range chunks in Da (default 50 Da)
    """
    all_compounds = set()  # Using set instead of list to automatically handle duplicates
    
    # Process mass range in chunks
    current_min = min_mass
    while current_min < max_mass:
        current_max = min(current_min + chunk_size, max_mass)
        
        print(f"Fetching compounds between {current_min:.2f}-{current_max:.2f} Da...")
        url = f'http://rest.kegg.jp/find/compound/{current_min}-{current_max}/exact_mass'
        response = requests.get(url)
        
        # Process chunk results
        new_compounds = 0
        for line in response.text.strip().split('\n'):
            if line:  # Skip empty lines
                compound_id = line.split('\t')[0].replace('cpd:', '')
                if compound_id not in all_compounds:  # Only add if not already present
                    all_compounds.add(compound_id)
                    new_compounds += 1
        
        print(f"Found {new_compounds} new compounds in range {current_min:.2f}-{current_max:.2f} Da")
        
        # Move to next chunk
        current_min = current_max
        
        # Be nice to KEGG server
        time.sleep(0.1)
    
    all_compounds = list(all_compounds)  # Convert set back to list
    print(f"Total unique compounds found: {len(all_compounds)}")
    
    return all_compounds

def get_compound_info_batch(compound_ids, max_retries=3):
    """Get information for multiple compounds in one request."""
    for attempt in range(max_retries):
        try:
            # Join compound IDs with + for batch retrieval
            compounds_str = '+'.join(f'cpd:{id}' for id in compound_ids)
            # Get compound details
            url = f'http://rest.kegg.jp/get/{compounds_str}'
            response = requests.get(url)
            
            compounds_info = []
            current_compound = None
            formula = "N/A"
            name = "N/A"
            
            for line in response.text.split('\n'):
                if line.startswith('ENTRY'):
                    if current_compound:
                        compounds_info.append((formula, current_compound, name))
                    current_compound = line.split()[1]
                    formula = "N/A"
                    name = "N/A"
                elif line.startswith('FORMULA'):
                    formula = line.split()[1]
                elif line.startswith('NAME'):
                    name = line.replace('NAME', '').strip()
                    if ';' in name:
                        name = name.split(';')[0].strip()
            
            # Add the last compound
            if current_compound:
                compounds_info.append((formula, current_compound, name))
            
            return compounds_info
            
        except Exception as e:
            if attempt < max_retries - 1:  # Don't sleep on last attempt
                sleep_time = (attempt + 1) * 2  # Exponential backoff
                print(f"\nError: {str(e)}")
                print(f"Retrying batch after {sleep_time}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(sleep_time)
            else:
                print(f"\nFailed to process batch after {max_retries} attempts.")
                print(f"Error: {str(e)}")
                return []  # Return empty list on final failure

def validate_formula(formula):
    """
    Validate a chemical formula by attempting to parse it.
    
    Args:
        formula: Chemical formula string
        
    Returns:
        True if valid, False otherwise
    """
    if formula == "N/A":
        return False
        
    try:
        parse_molecular_formula(formula)
        return True
    except KeyError:
        return False

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process KEGG compounds by mass range or compound IDs')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--mass-range', nargs=2, type=float, metavar=('MIN', 'MAX'),
                      help='Mass range in Da (e.g., --mass-range 100 200)')
    group.add_argument('--compound-ids', type=str,
                      help='File containing KEGG compound IDs (one per line)')
    
    args = parser.parse_args()
    
    # Load isotope data for formula validation
    load_isotope()
    
    if args.mass_range:
        min_mass, max_mass = args.mass_range
        # Get list of compound IDs in mass range (in chunks)
        compound_ids = get_compounds_by_mass_range(min_mass, max_mass)
        print(f"Found {len(compound_ids)} compounds in mass range {min_mass}-{max_mass} Da")
        output_file = f"kegg_compounds_{min_mass:.0f}-{max_mass:.0f}Da.tsv"
    else:
        # Read compound IDs from TSV file using pandas
        df = pd.read_csv(args.compound_ids, sep='\t')
        compound_ids = df['ID'].tolist()  # Get IDs from the 'ID' column
        print(f"Loaded {len(compound_ids)} compound IDs from {args.compound_ids}")
        output_file = "kegg_compounds_from_list.tsv"
    
    # Process compounds in batches of 10
    batch_size = 10
    skipped_formulas = []
    valid_compounds = 0
    
    with open(output_file, 'w') as f:
        # Write header
        f.write("CF\tID\tName\n")
        
        # Process in batches with progress bar
        for i in tqdm(range(0, len(compound_ids), batch_size), desc="Processing compounds"):
            batch = compound_ids[i:i + batch_size]
            try:
                compounds_info = get_compound_info_batch(batch)
                if len(compounds_info) != len(batch):
                    print(f"Warning: Batch size mismatch. Expected {len(batch)}, got {len(compounds_info)} compounds")
                
                # Write batch data
                for formula, cpd_id, name in compounds_info:
                    if validate_formula(formula):
                        f.write(f"{formula}\t{cpd_id}\t{name}\n")
                        valid_compounds += 1
                    else:
                        skipped_formulas.append((formula, cpd_id, name))
                
                # Be nice to the KEGG server
                time.sleep(0.1)
                
            except Exception as e:
                print()
                print(f"\nError processing batch starting with compound {batch[0]}: {str(e)}")
                print(batch)
                print()
                continue
    
    print(f"\nCompound data saved to {output_file}")
    print(f"Total valid compounds: {valid_compounds}")
    
    if skipped_formulas:
        print(f"Skipped {len(skipped_formulas)} compounds with invalid chemical formulas:")
        for cf, cpd_id, cpd_name in skipped_formulas[:10]:  # Show first 10 examples
            print(f"  - {cpd_id} ({cpd_name}): Formula '{cf}'")
        
        if len(skipped_formulas) > 10:
            print(f"  ... and {len(skipped_formulas) - 10} more")

if __name__ == "__main__":
    main() 