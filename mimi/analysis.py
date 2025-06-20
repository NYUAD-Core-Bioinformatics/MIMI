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

"""Analysis module for MIMI.

.. moduleauthor:: Nabil Rahiman <nabil.rahiman@nyu.edu>
"""

from mimi.atom import *
from mimi.molecule import *
import sys
import argparse
import os
import pickle
import numpy as np
from datetime import datetime
import pkg_resources
from tqdm import tqdm


def load_molecular_mass_database(db_file):
    """Load precalculated molecular mass database from TSV file.
    
    Args:
        db_file: Path to TSV file containing molecular mass data
        
    Returns:
        List of molecular mass entries, where each entry is a list containing:
        1. Chemical Formula (CF)
        2. Compound ID
        3. Compound Name

        Other fields from the input file are ignored.
    """
    mass_ref_list = []
    try:
        fd = open(db_file, encoding="ISO-8859-1")
        skip = True
        header_indices = {'CF': 0, 'ID': 1, 'Name': 2}  # Default indices
        
        for line in fd:
            if line.startswith('#'):
                continue
            line = line.strip()
            fields = line.split('\t')
            
            if skip:
                # Process header to determine field positions
                for i, field in enumerate(fields):
                    if field == 'CF':
                        header_indices['CF'] = i
                    elif field == 'ID':
                        header_indices['ID'] = i
                    elif field == 'Name':
                        header_indices['Name'] = i
                skip = False
                continue

            # Extract fields in the correct order regardless of input order
            cf = fields[header_indices['CF']] if header_indices['CF'] < len(fields) else ""
            compound_id = fields[header_indices['ID']] if header_indices['ID'] < len(fields) else ""
            name = fields[header_indices['Name']] if header_indices['Name'] < len(fields) else ""
            
            # Add fields in the required order: CF, ID, Name
            mass_ref_list.append([cf, compound_id, name])
        fd.close()
    except FileNotFoundError:
        print(f"Error: Database file '{db_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading database file '{db_file}': {str(e)}")
        sys.exit(1)

    return mass_ref_list



def load_mass_spectrometry_data(asc_file):
    """Load mass intensity data from mass spectrometry output file.
    
    Args:
        asc_file (str): Path to ASC format mass spectrometry output file. File should contain
                       tab-separated values with three columns per line:
                       1. mass value
                       2. intensity value
                       3. error/uncertainty value
                       
                       Lines starting with '#' are treated as comments and ignored.
                       The file may or may not have a header row.
        
    Returns:
        tuple: Contains:
            - list: List of [mass, intensity, error] data rows
            - dict: Metadata about the file including:
                - file_path: Original file path
                - line_count: Number of data lines (excluding comments and headers)
    """
    mass_intensity_pair_list = []
    metadata = {
        'file_path': asc_file,
        'line_count': 0
    }
    
    try:
        fd = open(asc_file)
        first_data_line = True
        
        for line in fd:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip comment lines starting with '#'
            if line.startswith('#'):
                continue
            
            fields = line.split('\t')
            
            # Skip potential header row by checking if first field looks like a number
            if first_data_line:
                try:
                    # Try to convert first field to float to detect if it's a header
                    float(fields[0])
                    first_data_line = False
                except (ValueError, IndexError):
                    # Likely a header row, skip it
                    continue
            
            # Ensure we have at least mass and intensity columns
            if len(fields) >= 2:
                mass_intensity_pair_list.append(fields)
                metadata['line_count'] += 1
            
        fd.close()
    except FileNotFoundError:
        print(f"Error: Sample file '{asc_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading sample file '{asc_file}': {str(e)}")
        sys.exit(1)
        
    return mass_intensity_pair_list, metadata


def create_mass_hash_index(compounds):
    """Create a hash index of compounds by integer mass for faster lookup.
    
    Args:
        compounds (dict): Dictionary of compound data
        
    Returns:
        dict: Mass-based index where keys are integer masses and values are
              lists of compounds with masses in that range. Each compound is
              also added to adjacent integer mass bins to handle boundary cases.
    """
    mass_index = {}
    for co in compounds:
        mass = compounds[co]['mass']
        mass_float = float(mass)
        mass_int = int(mass_float)
        
        # Add compound to its primary mass bin and adjacent bins
        for m in [mass_int - 1, mass_int, mass_int + 1]:
            if m not in mass_index:
                mass_index[m] = []
            mass_index[m].append(co)
            
    return mass_index


def get_atom_counts(exp):
    """Extract atom counts from molecular expression.
    
    Args:
        exp: List of atom expressions containing element symbols and counts
        
    Returns:
        tuple: Counts for (C, H, N, O, P, S) as strings
    """
    counts = {'C': '0', 'H': '0', 'N': '0', 'O': '0', 'P': '0', 'S': '0'}
    for each_atom in exp:
        symbol = each_atom[0][0]['element_symbol']
        if symbol in counts:
            counts[symbol] = str(each_atom[1])
    return (counts['C'], counts['H'], counts['N'], counts['O'], counts['P'], counts['S'])


def calculate_formula_mass(chemical_formula):
    """Calculate molecular mass from a chemical formula string.
    
    Args:
        chemical_formula (str): Chemical formula string (e.g., 'C6H12O6')
        
    Returns:
        float: Calculated molecular mass, or None if formula cannot be parsed
    """
    try:
        molecular_expression = parse_molecular_formula(chemical_formula)
        mass = calculate_nominal_mass(molecular_expression, 'zero')
        return mass
    except (KeyError, ValueError, AttributeError) as e:
        # Return None if formula cannot be parsed
        return None


def create_logger(log_fp, debug_fp, args):
    """Create a logger function with access to file handles and args.
    
    Args:
        out_fp: Output file handle
        log_fp: Log file handle
        debug_fp: Debug file handle
        args: Command line arguments
    
    Returns:
        Function that writes log messages to appropriate output
    """
    def write_log(message, is_debug=False):
        """Write log message to appropriate output.
        
        Args:
            message: Message to write
            is_debug: Whether this is a debug message
        """
        # Add newline to message if not present
        if not message.endswith('\n'):
            message += '\n'
            
        try:
            if is_debug:
                debug_fp.write(message)
            else:
                log_fp.write(message)
                
        except IOError as e:
            print(f"Error writing to log: {e}")
    
    return write_log


def main():
    """Main entry point for analysis tool."""
    ap = argparse.ArgumentParser(description="Molecular Isotope Mass Identifier")

    ap.add_argument("-p", "--ppm", dest="ppm", type=float,
                    help="Parts per million for the mono isotopic mass of chemical formula",  required=True)
    ap.add_argument("-vp", dest="vppm", type=float,
                    help="Parts per million for verification of isotopes",  required=True)
    ap.add_argument("-g", '--debug', dest="debug", action='store_true', help=argparse.SUPPRESS, default=False)

    ap.add_argument("-c", "--cache", dest="cache_files", help="Binary DB input file(s)",
                    metavar="DBBINARY", nargs='+', required=True)
    ap.add_argument("-s", "--sample", dest="samples", help="Input sample file",
                    metavar="SAMPLE", nargs='+',  required=True)

    ap.add_argument("-o", "--output", dest="out", required=True,
                    help="Output file", metavar="OUTPUT")
    
    args = ap.parse_args()

    full_command = ' '.join([os.path.basename(sys.argv[0])] + sys.argv[1:])

    # Create log directory if it doesn't exist and we're not logging to report
    log_dir = os.path.join(os.getcwd(), 'log')
    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Failed to create log directory '{log_dir}': {str(e)}")
        sys.exit(1)

    # Setup log files if not logging to report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_output = os.path.splitext(os.path.basename(args.out))[0]
    log_file = os.path.join(log_dir, f"{base_output}_{timestamp}.log")
    debug_file = os.path.join(log_dir, f"{base_output}_{timestamp}.debug")

    # Open log files if not logging to report
    try:
        log_fp = open(log_file, 'w') if log_file else None
        debug_fp = open(debug_file, 'w') if debug_file else None
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(args.out)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            except OSError as e:
                print(f"Error: Failed to create output directory '{output_dir}': {str(e)}")
                sys.exit(1)
                
        out_fp = open(args.out, 'w')
    except FileNotFoundError as e:
        print(f"Error: Could not open output file: {str(e)}")
        sys.exit(1)
    except IOError as e:
        print(f"Error opening output files: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        sys.exit(1)
    
    # Function to process a match between sample and database
    def process_match(co, mass_idx, sample_idx, precomputed_chem, mi_pair_list, 
                     aux_index_list, final_report, precomputed_chem_idx, data_sets,
                     computation_methods):
        """Process a matching mass between sample and database."""
        entry = [precomputed_chem[co]['cf'], co, precomputed_chem[co]['cname']]
        exp = precomputed_chem[co]['exp']
        mass = precomputed_chem[co]['mass']
        isotope_mass_list = precomputed_chem[co]['isotope_mass_list']

        # Get atom counts
        C_count, H_count, N_count, O_count, P_count, S_count = get_atom_counts(exp)

        # Initialize or get existing report entry
        if entry[1] not in final_report:
            output = [entry[0], entry[1], entry[2], 
                     C_count, H_count, N_count, O_count, P_count, S_count] + ['NO_MAPPED_ID'] * len(computation_methods)
            output[9 + precomputed_chem_idx] = str(mass)
            output = output + ['', '', '', ''] * len(data_sets) * len(computation_methods)
            final_report[entry[1]] = output
        else:
            output = final_report[entry[1]]
            output[9 + precomputed_chem_idx] = str(mass)

        # Validate isotope patterns
        first_intensity = float(mi_pair_list[mass_idx][1])
        matched_isotop_count = 0
        valid_isotop_count = 0

        if args.debug:
            write_log('-' * 80, is_debug=True)

        for each_mass in isotope_mass_list[1:]:
            molecular_mass = each_mass[0]
            molecular_abundance = each_mass[1]
            
            isotops_hits_index = search(mi_pair_list, molecular_mass, aux_index_list, args.vppm)

            if len(isotops_hits_index) > 0:
                matched_isotop_count += 1

            found_valid_isotop = False
            for each_isotop_hit_index in isotops_hits_index:
                intensity = float(mi_pair_list[each_isotop_hit_index][1])
                ms_isotopic_ratio = intensity / first_intensity
                error_rate = abs(molecular_abundance - ms_isotopic_ratio) / abs(molecular_abundance)

                if args.debug:
                    write_log('Hit ' + str(matched_isotop_count) + ':', is_debug=True)
                    write_log(f'{each_mass[2]} : {each_mass[0]}', is_debug=True)
                    write_log('molecular_abundance: ' + str(molecular_abundance), is_debug=True)
                    write_log('intensity: ' + str(intensity), is_debug=True)
                    write_log('first_intensity: ' + str(first_intensity), is_debug=True)
                    write_log('Formula for ms_isotopic_ratio = intensity / first_intensity', is_debug=True)
                    write_log('ms_isotopic_ratio = ' + f'{intensity} / {first_intensity} = {ms_isotopic_ratio}', is_debug=True)
                    write_log('Formula for error_rate = |molecular_abundance - ms_isotopic_ratio| / |molecular_abundance|', is_debug=True)
                    write_log('error_rate = ' + f'|{molecular_abundance} - {ms_isotopic_ratio}| / |{molecular_abundance}| = {error_rate}', is_debug=True)

                if error_rate < 0.3:
                    found_valid_isotop = True
                    if args.debug:
                        write_log('Valid hit(error_rate < 0.3)', is_debug=True)
                    break
                else:
                    if args.debug:
                        write_log('Invalid hit(error_rate >= 0.3)', is_debug=True)

                if args.debug:
                    write_log('-' * 80, is_debug=True)

            if found_valid_isotop:
                valid_isotop_count += 1

        # Record results
        base_idx = 9 + len(computation_methods)
        entry_idx = base_idx + (sample_idx * 4 * len(computation_methods))
        entry_idx = entry_idx + 4 * precomputed_chem_idx
        
        output[entry_idx] = mi_pair_list[mass_idx][0]
        error = ((float(mass) - float(mi_pair_list[mass_idx][0]))/(float(mass))) * 1000000
        output[entry_idx + 1] = str(error)
        output[entry_idx + 2] = mi_pair_list[mass_idx][1]
        output[entry_idx + 3] = str(matched_isotop_count)

        # print()
        # print('hello')
        # print(len(output))
        # print(len(computation_methods))
        # print(len(data_sets))
        # print(output)

        # sys.exit()
        # output[entry_idx + 4] = str(valid_isotop_count)
    
    # Load and display cache metadata
    precomputed_chem_files = []
    computation_methods = []
    cache_metadata = []

    write_log = create_logger(log_fp, debug_fp, args)
    cf_conflict_count = 0  # Track number of CF_CONFLICT cases

    for cache in args.cache_files:
        # method_name = cache.split('_')
        method_name = os.path.basename(cache)
        computation_methods.append(method_name)
        try:
            with open(cache + '.pkl', 'rb') as file:
                cache_data = pickle.load(file)
                cache_metadata.append(cache_data['metadata'])
                precomputed_chem_files.append(cache_data['compounds'])
        except FileNotFoundError:
            print(f"Error: Cache file '{cache}.pkl' not found.")
            if log_fp:
                log_fp.close()
            if debug_fp:
                debug_fp.close()
            if out_fp:
                out_fp.close()
            sys.exit(1)
        except Exception as e:
            print(f"Error loading cache file '{cache}.pkl': {str(e)}")
            if log_fp:
                log_fp.close()
            if debug_fp:
                debug_fp.close()
            if out_fp:
                out_fp.close()
            sys.exit(1)

    # Load  sample metadata
   
    data_sets = []
    for each_asc_file in args.samples:
        mi_pair_list, sample_metadata = load_mass_spectrometry_data(each_asc_file)
        mi_pair_list = sorted(mi_pair_list, key=lambda i: float(i[0]))
        aux_index_list = get_hashed_index(mi_pair_list)
        data_sets.append([mi_pair_list, aux_index_list, sample_metadata])
        

    args.ppm = args.ppm/1000000
    args.vppm = args.vppm/1000000
   
    atom.load_isotope()

    field_names = ['CF', 'ID', 'Name', 'C', 'H', 'N', 'O', 'P', 'S'] +  [method + '_mass' for method in computation_methods]
    
    # Write analysis metadata to log
    write_log("MIMI Mass Analysis Run Information:")
    write_log("=" * 80)
    write_log(f"Full Command: {full_command}")

    write_log(f"Date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")
    mimi_version = pkg_resources.get_distribution('mimi').version
    write_log(f"MIMI Version: {mimi_version}")
    write_log(f"PPM Tolerance: {args.ppm * 1000000}")
    write_log(f"Verification PPM: {args.vppm * 1000000}")

    
    write_log("-" * 80)

    # Write cache information to log
    write_log("\nCache Information:")
    write_log("=" * 80)
    for idx, cache in enumerate(args.cache_files):
        method_name = computation_methods[idx]
        metadata = cache_metadata[idx]
        cmd_line = metadata.get('command_line', {})
        write_log(f"Cache {idx + 1}:{cache}")
        write_log(f"Full Command: {cmd_line.get('full_command') or 'Unknown'}")
        write_log(f"Creation Date: {metadata.get('creation_date') or 'Unknown'}")
        write_log(f"MIMI Version: {metadata.get('mimi_version') or 'Unknown'}")
        write_log(f"Compounds: {len(precomputed_chem_files[idx])}")
        write_log(f"Ionization Mode: {cmd_line.get('ionization_mode') or 'Unknown'}")
        write_log(f"Labeled Atoms File: {cmd_line.get('labeled_atoms_file') or 'None'}")
        db_files = cmd_line.get('compound_db_files') if cmd_line else []
        if db_files:
            write_log(f"Compound DB Files: " + " ".join(str(x or 'Unknown') for x in db_files))
        else:
            write_log("Compound DB Files: None")
        write_log("-" * 80)
    # Write sample information to log
    write_log("\nSample Information:")
    write_log("=" * 80)
    for idx, sample_data in enumerate(data_sets):
        metadata = sample_data[2]
        write_log(f"\nSample {idx + 1}:{args.samples[idx]}")
        write_log(f"Data points: {metadata['line_count']}")
        write_log("-" * 80)
    # Write blank line before data
    write_log("\n")


    
    first_row = [''] * len(field_names)
    second_row = [''] * len(field_names)
    # first_row[4] = 'Reference Mass'

    field_per_sample = []
    for each_sample in args.samples:
        field_per_sample.append('mass_measured')
        field_per_sample.append('error_ppm')
        field_per_sample.append('intensity')
        field_per_sample.append('iso_count')
        # field_per_sample.append('iso_valid')
        first_row = first_row + [each_sample] + ['', '', ''] + ['', '', '', ''] * (len(computation_methods) - 1)
        l =  [[computation_methods[i],'', '', ''] for i in range(len(computation_methods)) ]
        second_row = second_row + [x for sublist in l for x in  sublist]

    field_names = field_names + field_per_sample * len(computation_methods)
    
    # Add log file path at the top of the report
    out_fp.write(f"Log file\t{log_file}\n")
    
    out_fp.write('\t'.join(first_row))
    out_fp.write('\n')
    if len(computation_methods) > 1:
        out_fp.write('\t'.join(second_row))
        out_fp.write('\n')
    out_fp.write('\t'.join(field_names))
    out_fp.write('\n')

    final_report = {}

    # Create mass-based indices for efficient compound lookup
    mass_indices = []
    for precomputed_chem in precomputed_chem_files:
        mass_indices.append(create_mass_hash_index(precomputed_chem))

    # Determine search strategy based on relative sizes
    for precomputed_chem_idx, precomputed_chem in enumerate(precomputed_chem_files):
        db_size = len(precomputed_chem)
        sample_sizes = [len(data[0]) for data in data_sets]
        avg_sample_size = sum(sample_sizes) / len(sample_sizes)
        
        mass_index = mass_indices[precomputed_chem_idx]
        
        if db_size > 10 * avg_sample_size:
            # Database much larger than samples - search from samples
            ordered_matches = []  # Store matches in order of database appearance
            compound_matches = set()  # Track which compounds have been matched
            
            # First pass - find all matches
            for sample_idx, data_set in enumerate(data_sets):
                mi_pair_list = data_set[0]
                aux_index_list = data_set[1]
                
                # Add progress bar for sample processing
                sample_desc = f"Processing sample {sample_idx+1}/{len(data_sets)}"
                for mass_idx, mass_intensity in enumerate(tqdm(mi_pair_list, desc=sample_desc)):
                    mass = float(mass_intensity[0])
                    mass_int = int(mass)
                    
                    if args.debug:
                        write_log('*' * 80, is_debug=True)
                        write_log(f"Searching mass {mass} in sample {sample_idx}", is_debug=True)
                    
                    # Check compounds with similar integer mass
                    candidate_compounds = []
                    for m in range(mass_int - 1, mass_int + 2):
                        if m in mass_index:
                            candidate_compounds.extend(mass_index[m])
                    
                    # Check each candidate within PPM tolerance
                    for co in candidate_compounds:
                        if co not in compound_matches:  # Only process new matches
                            compound_mass = precomputed_chem[co]['mass']
                            if abs(mass - compound_mass) <= (compound_mass * args.ppm):
                                compound_matches.add(co)
                                ordered_matches.append((co, mass_idx, sample_idx))
                                if args.debug:
                                    write_log('-' * 80, is_debug=True)
                                    write_log(f"Found match: {precomputed_chem[co]['cf']}", is_debug=True)
            
            # Second pass - process matches in database order
            match_desc = f"Processing matches for database {precomputed_chem_idx+1}/{len(precomputed_chem_files)}"
            for co in tqdm(precomputed_chem, desc=match_desc):
                entry = [precomputed_chem[co]['cf'], co, precomputed_chem[co]['cname']]
                
                if entry[1] not in final_report:
                    exp = precomputed_chem[co]['exp']
                    mass = precomputed_chem[co]['mass']
                    C_count, H_count, N_count, O_count, P_count, S_count = get_atom_counts(exp)
                    output = [entry[0], entry[1], entry[2], 
                            C_count, H_count, N_count, O_count, P_count, S_count] + ['NO_MAPPED_ID'] * len(computation_methods)
                    output[9 + precomputed_chem_idx] = str(mass)
                    output = output + ['', '', '', ''] * len(data_sets) * len(computation_methods)
                    final_report[entry[1]] = output
                    
                
                output = final_report[entry[1]]
                output[9 + precomputed_chem_idx] = 'NO_MASS_MATCH'

                if output[0] != precomputed_chem[co]['cf']:
                    # Calculate masses to determine if this is a real conflict
                    current_formula = precomputed_chem[co]['cf']
                    existing_formula = output[0]
                    current_mass = calculate_formula_mass(current_formula)
                    existing_mass = calculate_formula_mass(existing_formula)
                    
                    # Only flag as CF_CONFLICT if masses are actually different
                    if current_mass is None or existing_mass is None or abs(current_mass - existing_mass) > 1e-6:
                        # Log CF_CONFLICT with detailed reason
                        cf_conflict_count += 1
                        write_log(f"CF_CONFLICT detected for compound ID: {co}")
                        write_log(f"  Database {precomputed_chem_idx+1} ({computation_methods[precomputed_chem_idx]}): {current_formula} (mass: {current_mass:.6f})")
                        write_log(f"  Existing entry: {existing_formula} (mass: {existing_mass:.6f})")
                        write_log(f"  Compound name: {precomputed_chem[co]['cname']}")
                        write_log(f"  Reason: Same compound ID found with different chemical formulas and masses across databases")
                        output[9 + precomputed_chem_idx] = 'CF_CONFLICT'
                    else:
                        # Same mass, just different formula representation - log as info but don't flag conflict
                        write_log(f"INFO: Formula representation difference for compound ID: {co}")
                        write_log(f"  Database {precomputed_chem_idx+1} ({computation_methods[precomputed_chem_idx]}): {current_formula}")
                        write_log(f"  Existing entry: {existing_formula}")
                        write_log(f"  Both have same mass: {current_mass:.6f} - treating as equivalent formulas")

                final_report[entry[1]] = output
                
                if co in compound_matches:
                    # Find all instances where this compound matched
                    matches = [(m_idx, s_idx) for (c, m_idx, s_idx) in ordered_matches if c == co]
                    for mass_idx, sample_idx in matches:
                        process_match(co, mass_idx, sample_idx, precomputed_chem,
                                   data_sets[sample_idx][0], data_sets[sample_idx][1], 
                                   final_report, precomputed_chem_idx, data_sets, computation_methods)

                

        else:
            # Database smaller or comparable to samples - search from database 
            db_desc = f"Processing database {precomputed_chem_idx+1}/{len(precomputed_chem_files)}"
            for co in tqdm(precomputed_chem, desc=db_desc):
                entry = [precomputed_chem[co]['cf'], co, precomputed_chem[co]['cname']]
                
                if args.debug:
                    write_log('*' * 80, is_debug=True)
                    write_log(entry[0], is_debug=True)
            
                exp = precomputed_chem[co]['exp']
                mass = precomputed_chem[co]['mass']
                isotope_mass_list = precomputed_chem[co]['isotope_mass_list']


                if entry[1] not in final_report:
                    exp = precomputed_chem[co]['exp']
                    mass = precomputed_chem[co]['mass']
                    C_count, H_count, N_count, O_count, P_count, S_count = get_atom_counts(exp)
                    output = [entry[0], entry[1], entry[2], 
                            C_count, H_count, N_count, O_count, P_count, S_count] + ['NO_MAPPED_ID'] * len(computation_methods)
                    output[9 + precomputed_chem_idx] = str(mass)
                    output = output + ['', '', '', ''] * len(data_sets) * len(computation_methods)
                    final_report[entry[1]] = output
                
                output = final_report[entry[1]]
                output[9 + precomputed_chem_idx] = 'NO_MASS_MATCH'

                if output[0] != precomputed_chem[co]['cf']:
                    # Calculate masses to determine if this is a real conflict
                    current_formula = precomputed_chem[co]['cf']
                    existing_formula = output[0]
                    current_mass = calculate_formula_mass(current_formula)
                    existing_mass = calculate_formula_mass(existing_formula)
                    
                    # Only flag as CF_CONFLICT if masses are actually different
                    if current_mass is None or existing_mass is None or abs(current_mass - existing_mass) > 1e-6:
                        # Log CF_CONFLICT with detailed reason
                        cf_conflict_count += 1
                        write_log(f"CF_CONFLICT detected for compound ID: {co}")
                        write_log(f"  Database {precomputed_chem_idx+1} ({computation_methods[precomputed_chem_idx]}): {current_formula} (mass: {current_mass:.6f})")
                        write_log(f"  Existing entry: {existing_formula} (mass: {existing_mass:.6f})")
                        write_log(f"  Compound name: {precomputed_chem[co]['cname']}")
                        write_log(f"  Reason: Same compound ID found with different chemical formulas and masses across databases")
                        output[9 + precomputed_chem_idx] = 'CF_CONFLICT'
                    else:
                        # Same mass, just different formula representation - log as info but don't flag conflict
                        write_log(f"INFO: Formula representation difference for compound ID: {co}")
                        write_log(f"  Database {precomputed_chem_idx+1} ({computation_methods[precomputed_chem_idx]}): {current_formula}")
                        write_log(f"  Existing entry: {existing_formula}")
                        write_log(f"  Both have same mass: {current_mass:.6f} - treating as equivalent formulas")

                final_report[entry[1]] = output
                
                sample_idx = -1
                for data_set in data_sets:
                    mi_pair_list = data_set[0]
                    aux_index_list = data_set[1]
                    sample_idx += 1
                    if args.debug:
                        write_log('Searching in sample ' + str(sample_idx), is_debug=True)
                    natural_hits_index = search(
                        mi_pair_list, mass, aux_index_list, args.ppm)
                    if len(natural_hits_index) > 0:
                        process_match(co, natural_hits_index[0], sample_idx, precomputed_chem,
                                   mi_pair_list, aux_index_list, final_report, 
                                   precomputed_chem_idx, data_sets, computation_methods)

                
             
                

                
    # Write results to output file with progress bar
    write_log("Writing results to output file...")
    result_desc = "Writing results"
    try:
        for molecule in tqdm(final_report, desc=result_desc):

            if all(x == 'NO_MAPPED_ID' or x == 'NO_MASS_MATCH' or x == 'CF_CONFLICT' for x in final_report[molecule][9:9+len(computation_methods)]):
                continue

            out_fp.write('\t'.join(final_report[molecule]))
            out_fp.write('\n')
    except IOError as e:
        print(f"Error: Failed to write to output file: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred while writing results: {str(e)}")
        sys.exit(1)
    
    # Print CF_CONFLICT summary if any were detected
    if cf_conflict_count > 0:
        print(f"\nWARNING: {cf_conflict_count} CF_CONFLICT(s) were detected during analysis.")
        print("This indicates compounds with the same ID but different chemical formulas across databases.")
        print(f"For detailed information about these conflicts, please check the log file: {log_file}")
        print("Consider reviewing your compound databases for data consistency.\n")
    
    # Close files
    if log_fp:
        log_fp.close()
    if debug_fp:
        debug_fp.close()
    out_fp.close()


if __name__ == '__main__':
    main()
