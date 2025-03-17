import requests
import time
from typing import List, Tuple
from tqdm import tqdm
from mimi.molecule import parse_molecular_formula
from mimi.atom import load_isotope
import argparse
import pandas as pd

def get_compounds_by_mass_range(min_mass, max_mass, chunk_size=50.0):
    """
    Get a list of KEGG compound IDs within specified mass range.
    Breaks large mass ranges into smaller chunks to handle KEGG's 10,000 result limit.
    
    Args:
        min_mass: Minimum mass in Da
        max_mass: Maximum mass in Da
        chunk_size: Size of mass range chunks in Da (default 50 Da)
        
    Returns:
        List of KEGG compound IDs
    """
    all_compounds = set()
    
    current_min = min_mass
    while current_min < max_mass:
        current_max = min(current_min + chunk_size, max_mass)
        
        print(f"Fetching compounds between {current_min:.2f}-{current_max:.2f} Da...")
        url = f'http://rest.kegg.jp/find/compound/{current_min}-{current_max}/exact_mass'
        response = requests.get(url)
        
        for line in response.text.strip().split('\n'):
            if line:
                compound_id = line.split('\t')[0].replace('cpd:', '')
                all_compounds.add(compound_id)
        
        current_min = current_max
        time.sleep(0.1)  # Be nice to KEGG server
    
    return list(all_compounds)

def get_compound_info_batch(compound_ids, max_retries=5):
    """
    Get information for multiple compounds in one request.
    
    Args:
        compound_ids: List of KEGG compound IDs
        max_retries: Number of retry attempts for failed requests
        
    Returns:
        List of tuples containing (chemical_formula, compound_id, name)
    """
    for attempt in range(max_retries):
        try:
            compounds_str = '+'.join(f'cpd:{id}' for id in compound_ids)
            url = f'http://rest.kegg.jp/get/{compounds_str}'
            response = requests.get(url)
            
            compounds_info = []
            current_compound = None
            formula = "N/A"
            name = "N/A"
            exact_mass = "0.0"
            
            for line in response.text.split('\n'):
                if line.startswith('ENTRY'):
                    if current_compound:
                        compounds_info.append((formula, current_compound, name, exact_mass))
                    current_compound = line.split()[1]
                    formula = "N/A"
                    name = "N/A"
                elif line.startswith('FORMULA'):
                    formula = line.split()[1]
                elif line.startswith('NAME'):
                    name = line.replace('NAME', '').strip()
                    if ';' in name:
                        name = name.split(';')[0].strip()
                elif line.startswith('EXACT_MASS'):
                    exact_mass = line.split()[1]
                
            
            if current_compound:
                compounds_info.append((formula, current_compound, name, exact_mass))
            
            return compounds_info
            
        except Exception as e:
            if attempt < max_retries - 1:
                sleep_time = (attempt + 1) * 2
                print(f"\nError: {str(e)}")
                print(f"Retrying batch after {sleep_time}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(sleep_time)
            else:
                print(f"\nFailed to process batch after {max_retries} attempts.")
                print(f"Error: {str(e)}")
                return []

def export_compounds_to_tsv(output_file, compound_ids=None, mass_range=None, batch_size=10):
    """
    Export KEGG compound information to TSV file.
    
    Args:
        output_file: Path to output TSV file
        compound_ids: List of KEGG compound IDs (optional)
        mass_range: Tuple of (min_mass, max_mass) in Da (optional)
        batch_size: Number of compounds to process in each batch
    """
    if mass_range:
        min_mass, max_mass = mass_range
        compound_ids = get_compounds_by_mass_range(min_mass, max_mass)
        print(f"Found {len(compound_ids)} compounds in mass range {min_mass}-{max_mass} Da")
    
    skipped_formulas = []
    valid_compounds = 0
    
    with open(output_file, 'w') as f:
        f.write("CF\tID\tname\n")
        
        for i in tqdm(range(0, len(compound_ids), batch_size), desc="Processing compounds"):
            batch = compound_ids[i:i + batch_size]
            compounds_info = get_compound_info_batch(batch)
            
            if len(compounds_info) != len(batch):
                print(f"Warning: Batch size mismatch. Expected {len(batch)}, got {len(compounds_info)} compounds")
            
            for formula, cpd_id, name, exact_mass in compounds_info:
                try:
                    if formula != "N/A":
                        parse_molecular_formula(formula)
                        f.write(f"{formula}\t{cpd_id}\t{name}\n")
                        valid_compounds += 1
                    else:
                        skipped_formulas.append((formula, cpd_id, name))
                except KeyError:
                    skipped_formulas.append((formula, cpd_id, name))
            
            time.sleep(0.1)
    
    print(f"\nCompound data saved to {output_file}")
    print(f"Total valid compounds: {valid_compounds}")
    
    if skipped_formulas:
        print(f"Skipped {len(skipped_formulas)} compounds with invalid chemical formulas:")
        for cf, cpd_id, cpd_name in skipped_formulas[:10]:
            print(f"  - {cpd_id} ({cpd_name}): Formula '{cf}'")
        if len(skipped_formulas) > 10:
            print(f"  ... and {len(skipped_formulas) - 10} more")

def main():
    parser = argparse.ArgumentParser(description='Extract compound information from KEGG')
    parser.add_argument('-l', '--min-mass', type=float,
                      help='Lower bound of molecular weight in Da')
    parser.add_argument('-u', '--max-mass', type=float,
                      help='Upper bound of molecular weight in Da')
    parser.add_argument('-i', '--input', dest='compound_ids', type=str,
                      help='Input TSV file containing KEGG compound IDs')
    parser.add_argument('-o', '--output', default='kegg_compounds.tsv',
                      help='Output TSV file path (default: kegg_compounds.tsv)')
    
    args = parser.parse_args()
    
    load_isotope()
    
    # Validate arguments
    if not args.compound_ids and (args.min_mass is None or args.max_mass is None):
        print("Error: When not using --compound-ids, both --min-mass and --max-mass are required")
        exit(1)
    
    if args.compound_ids:
        try:
            # Load compound IDs from file
            df = pd.read_csv(args.compound_ids, sep='\t')
            compound_ids = df['ID'].tolist()
            print(f"Loaded {len(compound_ids)} compound IDs from {args.compound_ids}")
            
            # Get compound info
            print("Fetching compound information...")
            all_compounds_info = []
            batch_size = 10
            
            # Configure tqdm to avoid progress bar issues
            with tqdm(total=len(compound_ids), desc="Processing compounds", 
                     ncols=100, leave=True) as pbar:
                for i in range(0, len(compound_ids), batch_size):
                    batch = compound_ids[i:i + batch_size]
                    compounds_info = get_compound_info_batch(batch)
                    all_compounds_info.extend(compounds_info)
                    pbar.update(len(batch))
            
            # Filter by mass range if specified
            if args.min_mass is not None or args.max_mass is not None:
                min_mass = args.min_mass if args.min_mass is not None else float('-inf')
                max_mass = args.max_mass if args.max_mass is not None else float('inf')
                filtered_compounds = []
                
                for formula, cpd_id, name, exact_mass in all_compounds_info:
                    try:
                        mass = float(exact_mass)
                        if min_mass <= mass <= max_mass:
                            filtered_compounds.append(cpd_id)
                    except ValueError:
                        continue
                
                print(f"\nFound {len(filtered_compounds)} compounds from the input list within mass range {min_mass}-{max_mass} Da")
                compound_ids = filtered_compounds
            
            export_compounds_to_tsv(args.output, compound_ids=compound_ids)
            
        except FileNotFoundError:
            print(f"Error: Input file '{args.compound_ids}' not found")
            exit(1)
        except pd.errors.EmptyDataError:
            print(f"Error: Input file '{args.compound_ids}' is empty")
            exit(1)
        except KeyError:
            print(f"Error: Input file must contain a column named 'ID'")
            exit(1)
    else:
        # If no compound IDs provided, search KEGG by mass range
        mass_range = (args.min_mass, args.max_mass)
        export_compounds_to_tsv(args.output, mass_range=mass_range)

if __name__ == "__main__":
    main() 