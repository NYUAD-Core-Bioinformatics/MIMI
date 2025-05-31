"""
Atom Processing Module

This module handles atomic data and isotope information for mass spectrometry
calculations.

Functions:
    load_labelled_atoms: Load labeled atom data from JSON
    load_isotope: Load isotope data
    get_atom: Get atom information by symbol
    get_exact_mass: Get exact mass for specific isotope
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

import json5
import pkg_resources
import os
from pathlib import Path

# Define default data file paths


# Initialize global dictionary for atom data
atom_dic = {}

def validate_isotope_data(isotope_data):
    """Validate that isotope natural abundance values sum to approximately 1.0 for each element.
    
    Args:
        isotope_data (dict): Dictionary of isotope data by element
        
    Returns:
        tuple: (is_valid, issues) where is_valid is a boolean and issues is a list of problem elements
    """
    issues = []
    
    # Check each element
    for element, isotopes in isotope_data.items():
        total_abundance = sum(isotope["abundance"] for isotope in isotopes)
        
        # Allow for small rounding errors (within 0.5%)
        if not  abs(total_abundance - 1.0) == 0.000:
            issues.append({
                "element": element,
                "total_abundance": total_abundance,
                "difference": total_abundance - 1.0,
                "isotopes": len(isotopes)
            })
    
    return len(issues) == 0, issues

def validate_isotope_order_and_consistency(isotope_data):
    """Validate isotope ordering and consistency of highest_abundance values.
    
    Args:
        isotope_data (dict): Dictionary of isotope data by element
        
    Returns:
        tuple: (is_valid, order_issues, consistency_issues) where is_valid is a boolean 
        and issues are lists of problem elements
    """
    order_issues = []
    consistency_issues = []
    
    for element, isotopes in isotope_data.items():
        if not isotopes:  # Skip empty lists
            continue
        
        # Get the highest abundance from the list
        highest_abundance = max(isotope["abundance"] for isotope in isotopes)
        
        # Check if first entry has the highest abundance
        if isotopes[0]["abundance"] != highest_abundance:
            order_issues.append(element)
        
        # Check if all isotopes have the same highest_abundance value
        for isotope in isotopes:
            if "highest_abundance" not in isotope or isotope["highest_abundance"] != highest_abundance:
                consistency_issues.append(element)
                break
    
    return len(order_issues) == 0 and len(consistency_issues) == 0, order_issues, consistency_issues

def load_labelled_atoms(jsonfile):
    """Load labeled atom data from JSON file.

    :param jsonfile: Path to JSON file containing labeled atom data
    :type jsonfile: str
    :returns: None
    :rtype: None
    :raises ValueError: If isotope data is invalid
    """
    global atom_dic
    try:
        with open(jsonfile, 'r', encoding='utf-8') as f:
            try:
                new_data = json5.loads(f.read())
            except Exception as json_err:
                raise ValueError(f"Invalid JSON format in {jsonfile}: {str(json_err)}")
        
        # Sort isotopes by abundance and add highest_abundance for each element
        sorted_data = {}
        for element, isotopes in new_data.items():
            if isotopes:
                # Rename isotope_abundance to abundance
                for isotope in isotopes:
                    isotope["abundance"] = isotope.pop("isotope_abundance")
                highest_abundance = max(isotope["abundance"] for isotope in isotopes)
                sorted_data[element] = sorted(
                    [dict(isotope, highest_abundance=highest_abundance) 
                     for isotope in isotopes],
                    key=lambda x: x['abundance'],
                    reverse=True
                )
         
        # Validate the isotope data
        is_valid, issues = validate_isotope_data(sorted_data)
        if not is_valid:
            error_msg = f"Invalid isotope data in {jsonfile}. Found {len(issues)} elements with natural abundance values that don't sum to 1.0:\n"
            for issue in issues:
                error_msg += f"  {issue['element']}: sum = {issue['total_abundance']:.6f} " \
                             f"(diff: {issue['difference']:.6f}, isotopes: {issue['isotopes']})\n"
            raise ValueError(error_msg)
        
        # Validate ordering and consistency
        is_valid, order_issues, consistency_issues = validate_isotope_order_and_consistency(sorted_data)
        if not is_valid:
            error_msg = ""
            if order_issues:
                error_msg += f"Found {len(order_issues)} elements where first isotope is not highest abundance:\n"
                error_msg += "  " + ", ".join(order_issues) + "\n"
            if consistency_issues:
                error_msg += f"Found {len(consistency_issues)} elements with inconsistent highest_abundance values:\n"
                error_msg += "  " + ", ".join(consistency_issues)
            raise ValueError(error_msg)
            
        atom_dic.update(sorted_data)
    except ValueError as ve:
        raise
    except FileNotFoundError:
        raise ValueError(f"File not found: {jsonfile}")
    except Exception as e:
        raise ValueError(f"Error loading atom data from {jsonfile}: {str(e)}")

def load_isotope():
    """Load isotope data from JSON file."""
    global atom_dic
    DEFAULT_ISOTOPE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),'mimi', 'data', 'natural_isotope_abundance_NIST.json')
    with open(DEFAULT_ISOTOPE_FILE, 'r', encoding='utf-8') as f:
        data = json5.loads(f.read())
    
    # Sort isotopes and add highest_abundance for each element
    for element, isotopes in data.items():
        if isotopes:
            # Rename isotope_abundance to abundance
            for isotope in isotopes:
                isotope["abundance"] = isotope.pop("isotope_abundance")
            highest_abundance = max(isotope["abundance"] for isotope in isotopes)
            data[element] = sorted(
                [dict(isotope, highest_abundance=highest_abundance) 
                 for isotope in isotopes],
                key=lambda x: x['abundance'],
                reverse=True
            )
    
    # Validate ordering and consistency
    is_valid, order_issues, consistency_issues = validate_isotope_order_and_consistency(data)
    if not is_valid:
        error_msg = ""
        if order_issues:
            error_msg += f"Found {len(order_issues)} elements where first isotope is not highest abundance:\n"
            error_msg += "  " + ", ".join(order_issues) + "\n"
        if consistency_issues:
            error_msg += f"Found {len(consistency_issues)} elements with inconsistent highest_abundance values:\n"
            error_msg += "  " + ", ".join(consistency_issues)
        raise ValueError(error_msg)
    
    atom_dic = data

 


def get_atom(atom):
    """Get atom information by symbol.

    :param atom: Chemical symbol of the atom
    :type atom: str
    :returns: Dictionary containing atom isotope information
    :rtype: dict
    """
    global atom_dic
    
    # return atom
    return(atom_dic[atom])


def get_exact_mass(atom, nominal_mass):
    """Get exact mass for specific isotope.

    :param atom: Chemical symbol of the atom
    :type atom: str
    :param nominal_mass: Nominal mass of the isotope
    :type nominal_mass: int
    :returns: Exact mass of the specified isotope
    :rtype: float
    :raises AssertionError: If no matching isotope is found
    """
    global atom_dic
    isotopes = atom_dic[atom]

    for isotope in isotopes:
        if isotope['nominal_mass'] == nominal_mass:
            return isotope['exact_mass']

    assert(0)
