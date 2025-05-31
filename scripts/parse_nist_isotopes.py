import json
from collections import defaultdict

def parse_nist_data(nist_file):
    isotopes = defaultdict(list)
    atomic_number_map = {}  # Maps atomic numbers to their first symbol
    current_isotope = {}
    
    # First pass to establish atomic number to symbol mapping
    with open(nist_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
                
            if '=' in line:
                key, value = [x.strip() for x in line.split('=', 1)]
                
                if key == 'Atomic Number':
                    current_number = int(value)
                elif key == 'Atomic Symbol' and current_number:
                    # Only store the first symbol encountered for each atomic number
                    if current_number not in atomic_number_map:
                        atomic_number_map[current_number] = value

    # Second pass to parse isotopes using the established mapping
    with open(nist_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            if not line or line.startswith('//'):
                continue
                
            if '=' in line:
                key, value = [x.strip() for x in line.split('=', 1)]
                
                if key == 'Atomic Number':
                    if current_isotope:
                        # Store previous isotope
                        atomic_num = current_isotope.get('periodic_number')
                        if atomic_num:
                            primary_symbol = atomic_number_map[atomic_num]
                            isotopes[primary_symbol].append(current_isotope.copy())
                    current_isotope = {'periodic_number': int(value)}
                    
                elif key == 'Atomic Symbol':
                    atomic_num = current_isotope.get('periodic_number')
                    if atomic_num:
                        # Always use the primary symbol for grouping isotopes
                        current_isotope['element_symbol'] = atomic_number_map[atomic_num]
                       
                elif key == 'Mass Number':
                    current_isotope['nominal_mass'] = int(value)
                elif key == 'Relative Atomic Mass':
                    mass = value.split('(')[0]
                    current_isotope['exact_mass'] = float(mass)
                elif key == 'Isotopic Composition':
                    if value:  # Only store if there's a value
                        abundance = value.split('(')[0]
                        current_isotope['abundance'] = float(abundance)

    # Add final isotope
    if current_isotope:
        atomic_num = current_isotope.get('periodic_number')
        if atomic_num:
            primary_symbol = atomic_number_map[atomic_num]
            isotopes[primary_symbol].append(current_isotope.copy())

    # Calculate highest abundance for each element
    # for element in isotopes:
    #     isotopes_with_abundance = [iso for iso in isotopes[element] if 'isotope_abundance' in iso]
    #     if isotopes_with_abundance:
    #         highest_abundance = max(iso['isotope_abundance'] for iso in isotopes_with_abundance)
    #         for isotope in isotopes[element]:
    #             isotope['highest_abundance'] = highest_abundance

    return dict(isotopes)

def update_iupac_json(nist_data, output_file):
    # Convert to the format matching the original JSON
    formatted_data = {}
    
    for element, isotopes in nist_data.items():
        # Only include isotopes with natural abundance
        natural_isotopes = [iso for iso in isotopes if 'isotope_abundance' in iso]
        if natural_isotopes:
            formatted_data[element] = sorted(natural_isotopes, 
                                          key=lambda x: x['isotope_abundance'],
                                          reverse=True)

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(formatted_data, f, indent=6)

def main():
    nist_file = 'data/raw/Atomic_masses_and_isotopic_composition_NIST.txt'
    output_file = 'data/processed/natural_isotope_abundance_NIST.json'
    
    nist_data = parse_nist_data(nist_file)
    update_iupac_json(nist_data, output_file)

if __name__ == '__main__':
    main() 