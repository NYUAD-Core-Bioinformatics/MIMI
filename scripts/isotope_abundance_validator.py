import json5
import sys

def verify_abundance():
    # Load the isotope data
    with open('data/processed/C13_95.json', 'r') as f:
        isotope_data = json5.load(f)
    
    # Track elements with issues
    issues = []
    sorting_issues = []
    order_issues = []
    
    # Check each element
    for element, isotopes in isotope_data.items():
        # Check abundance sum
        total_abundance = sum(isotope["abundance"] for isotope in isotopes)
        
        # Allow for small rounding errors (within 0.5%)
        if abs(total_abundance - 1.0) != 0.000000:
            issues.append({
                "element": element,
                "total_abundance": total_abundance,
                "difference": total_abundance - 1.0,
                "isotopes": len(isotopes)
            })
        
        # Check if isotopes are sorted by abundance in descending order
        abundances = [isotope["abundance"] for isotope in isotopes]
        if abundances != sorted(abundances, reverse=True):
            sorting_issues.append(element)
        
        # Check if highest abundance isotope is first
        highest_abundance = max(abundances)
        if abundances[0] != highest_abundance:
            order_issues.append(element)
    
    # Print results
    if not issues and not sorting_issues and not order_issues:
        print("All elements have correct natural abundance values, sorting, and highest abundance first")
        return 0
    else:
        if issues:
            print(f"Found {len(issues)} elements with natural abundance values that don't sum to 1.0:")
            for issue in issues:
                print(f"  {issue['element']}: sum = {issue['total_abundance']:.6f} " 
                      f"(diff: {issue['difference']:.6f}, isotopes: {issue['isotopes']})")
        
        if sorting_issues:
            print(f"\nFound {len(sorting_issues)} elements with unsorted isotopes:")
            print("  " + ", ".join(sorting_issues))
        
        if order_issues:
            print(f"\nFound {len(order_issues)} elements where highest abundance is not first:")
            print("  " + ", ".join(order_issues))
        
        return 1

if __name__ == "__main__":
    sys.exit(verify_abundance())