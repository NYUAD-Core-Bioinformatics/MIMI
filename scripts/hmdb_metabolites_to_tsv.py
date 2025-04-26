import xml.etree.ElementTree as ET

# Function to extract metabolite information
def parse_hmdb_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Define the namespace
    ns = {'hmdb': 'http://www.hmdb.ca'}
    
    metabolites = []
    
    # Iterate through each metabolite entry, using namespace
    for metabolite in root.findall("hmdb:metabolite", ns):
        # Extract ID
        accession = metabolite.find("hmdb:accession", ns)
        metabolite_id = accession.text if accession is not None else "N/A"

        # Extract Name
        name_element = metabolite.find("hmdb:name", ns)
        name = name_element.text if name_element is not None else "N/A"
        
        # Extract Chemical Formula
        formula_element = metabolite.find("hmdb:chemical_formula", ns)
        chemical_formula = formula_element.text if formula_element is not None else "N/A"
        
        # Append to list
        metabolites.append((chemical_formula, metabolite_id, name))
    
    return metabolites

# Input XML file path
xml_file = "/Users/nr83/Downloads/hmdb_metabolites.xml"  # Update with actual file path

# Parse the XML and get metabolite data
metabolite_data = parse_hmdb_xml(xml_file)

# Print output in tab-separated format
print("CF\tID\tName")
for cf, met_id, met_name in metabolite_data:
    print(f"{cf}\t{met_id}\t{met_name}")

# Save to a file (optional)
output_file = "metabolites.tsv"
with open(output_file, "w") as f:
    f.write("CF\tID\tName\n")
    for cf, met_id, met_name in metabolite_data:
        f.write(f"{cf}\t{met_id}\t{met_name}\n")

print(f"Extracted data saved to {output_file}")
