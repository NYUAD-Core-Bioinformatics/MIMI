"""
Molecule Processing Module

This module provides functionality for processing molecular formulas and calculating
masses for molecules and their isotopes.

:noindex:

Functions:
    calculate_nominal_mass: Calculate mass of a molecule
    calculate_mass: Calculate mass with ion adjustments
    get_isotop_variants_mass: Calculate mass variants for isotopes
    parse_molecular_formula: Parse a molecular formula string
    get_hashed_index: Create index for fast lookup
    search: Search molecular mass data within PPM tolerance
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

import sys
from itertools import groupby
from itertools import permutations
from itertools import combinations_with_replacement
from itertools import product
from mimi.atom import *
from mimi import atom
import os
import inspect

import json



def createArgObject():
    """Creates and returns an empty object instance.
    
    :noindex:
    
    Returns:
        Object: An empty object that can be used to store arbitrary attributes
    """
    class Object(object):
        pass
    return Object()




# https://chem.libretexts.org/Courses/University_of_Arkansas_Little_Rock/Chem_1402%3A_General_Chemistry_1_(Kattoum)/Text/2%3A_Atoms%2C_Molecules%2C_and_Ions/2.03%3A_Isotopic_Abundance_and_Atomic_Weight
# https://www2.chemistry.msu.edu/faculty/reusch/OrgPage/mass.htm
# https://www.youtube.com/watch?v=xk5f6txgwic&feature=emb_rel_end

def calculate_nominal_mass(molecular_expression, ion):
    """Calculate the nominal mass of a molecule.

    :noindex:

    Args:
        molecular_expression (list): List of [atom_info, count] pairs, where atom_info contains 
            isotope data and count is the number of atoms
        ion (str): Ion type - 'pos' for positive, 'neg' for negative, or 'zero' for neutral

    Returns:
        float: The calculated nominal molecular mass adjusted for ion charge

    Note:
        Calculates basic mass without considering isotope variations. For positive ions,
        adds a proton mass; for negative ions, subtracts a proton mass.
    """

    proton_mass = negative_charge = 1.007276467
    # mass_electron = 0.00054858
    molecular_mass = 0.0
    # print('molecular_expression', molecular_expression)
    for each_atom in molecular_expression:
       
        atomic_desc = each_atom[0]
        n_atoms = each_atom[1]
  
        atom = atomic_desc[0]['element_symbol']
        mass = atomic_desc[0]['exact_mass']
  

        molecular_mass += mass * n_atoms

    if 'neg' == ion:
        return molecular_mass - proton_mass
    elif 'pos' == ion:
        return molecular_mass + proton_mass
    else:
        return molecular_mass




def calculate_mass(molecular_expression, ion):
    """Calculate the exact mass of a molecule including ion adjustments.

    :noindex:

    Args:
        molecular_expression (list): List containing atom information and counts
        ion (str): Ion type - 'pos' for positive, 'neg' for negative, or 'zero' for neutral

    Returns:
        float: The calculated molecular mass adjusted for ion charge

    Raises:
        AssertionError: If ion parameter is not one of 'zero', 'neg', or 'pos'
        
    Note:
        Similar to calculate_nominal_mass but uses exact masses rather than nominal masses
    """
    assert(ion == 'neg' or ion == 'pos')

    proton_mass = negative_charge = 1.007276467

    molecular_mass = 0.0

    for each_atom in molecular_expression:

        atomic_desc = each_atom[0]

        n_atoms = each_atom[1]

        atom = atomic_desc['element_symbol']
        mass = atomic_desc['exact_mass']
      

        molecular_mass += mass * n_atoms

    if 'neg' == ion:
        return molecular_mass - proton_mass
    elif 'pos' == ion:
        return molecular_mass + proton_mass
    else:
        return molecular_mass


def get_isotop_variants_mass(molecular_expression, ion, args):
    """Calculate masses for all possible isotope combinations of a molecule.

    :noindex:

    Args:
        molecular_expression (list): List of [atom_info, count] pairs
        ion (str): Ion type - 'pos', 'neg', or 'zero'
        args: Arguments object containing debug settings and debug file pointer

    Returns:
        list: List of [mass, abundance, isotope_name] tuples for each valid isotope combination,
            sorted by mass. Only includes combinations with abundance ratio > 0.000001

    Note:
        Uses combinations_with_replacement to generate all possible isotope combinations
        while filtering out extremely low abundance variants
    """

    ll = []
    for each_element in molecular_expression:
        l = []
        n_atoms = each_element[1]
        isotop_list = each_element[0]
        #total_isotopes = len(isotop_list)
        # 1 groups = [(isotop_list[0], n_atoms, n_atoms)]
        # 1 l.append(groups)

        comb = combinations_with_replacement(isotop_list, n_atoms)
        comb_list = list(comb)

        for c in comb_list:
            groups = []
            skip = False
            for key_isotop, key_list in groupby(c):
                n_atoms = len(list(key_list))

                abundance_ratio = (
                    key_isotop['abundance']/key_isotop['highest_abundance']) ** n_atoms
                if abundance_ratio < 1.0/args.noise_cutoff:
                    skip = True
                    break

                groups.append((key_isotop, n_atoms))

            if not skip:
                l.append(groups)
        ll.append(l)


    product_list = list(product(*ll))

    # print(product_list)
    mass_list = []
    debug_output_list = []
    for molecular_pattern in product_list:
        m = []
        debug_output = ''
        molecular_abundance = 1.0
        isotop_name = ''
        for i in range(len(molecular_pattern)):
            element = molecular_pattern[i]
            # each elements [(isotop1, istop1_count, number_of_atoms),
            # (isotop1, istop1_count, number_of_atoms), ...]
            # Every element has the information about total
            # elements(periticular atom) in molecular expression.
            factor = number_of_atoms = element[0][1]
            hfactor = 0
            
            for j in range(len(element)):
                hfactor += element[j][1]
            
            # print('-------------')
            for j in range(len(element)):
                isotop = element[j][0]
                factor = isotop_count = element[j][1]
   
                m.append([isotop, isotop_count])

                assert(factor != 0)

                if isotop['highest_abundance'] != isotop['abundance']:
                    # hfactor -= factor
                    molecular_abundance *= (
                    (isotop['abundance'] / isotop['highest_abundance'])  ** factor) * (hfactor)
                    
                  
                    
                    if molecular_abundance > 1:
                        assert(molecular_abundance > 1)

                debug_output += '[' + str(isotop['nominal_mass']) + ']' + str(
                    isotop['element_symbol']) + str(isotop_count) + ' '

        # molecular_abundance = float("%0.8f" % molecular_abundance)

        if molecular_abundance < 0.000001:
            continue

        isotop_name += debug_output

        molecular_mass = calculate_mass(m, ion)
        # molecular_mass = float("%0.4f" % molecular_mass)
        #molecular_abundance = float("%0.4f" % molecular_abundance)
        mass_list.append([molecular_mass,  molecular_abundance, isotop_name])
        debug_output = debug_output.strip()
        debug_output += ',' + \
            str(float("%0.6f" % molecular_mass)) + \
            ',' + str(float("%0.6f" % molecular_abundance))
        
        debug_output_list.append([molecular_abundance, debug_output])
   
   
    debug_output_list = [debug_output_list[0]]  +   sorted(debug_output_list[1:], key=lambda e: e[0], reverse=True)
    # print(debug_output_list[0])
    
    # Update debug logging to work with both direct debug_fp and write_log function
    if args.debug:
        debug_output_list = list(map(lambda e: e[1], debug_output_list))
        if hasattr(args, 'debug_fp') and args.debug_fp:
            # Write directly to debug file pointer if available
            args.debug_fp.write('\n'.join(debug_output_list) + '\n')
        elif hasattr(args, 'write_log'):
            # Use write_log function if available
            for line in debug_output_list:
                args.write_log(line, is_debug=True)
    
    mass_list = [mass_list[0]]  +   sorted(mass_list[1:], key=lambda molecule: molecule[1], reverse=True)
    
    return mass_list


def parse_molecular_formula(molecular_expression):
    """Parse a molecular formula string into its atomic components.

    :noindex:

    Args:
        molecular_expression (str): Chemical formula string (e.g., 'C6H12O6')

    Returns:
        list: List of [atom_info, count] pairs where:
            - atom_info contains isotope data for the element
            - count is the number of atoms of that element

    Note:
        Handles both single letter elements (H, C, N) and two letter elements (Fe, Na)
        Supports numbers after elements but not complex formulas with parentheses
    """
   

    

    exp = []
    atom = ''
    count = ''
    for c in molecular_expression:
        if c.isdigit():
            if atom != '':
                exp.append([get_atom(atom), 1])
                atom = ''

            count += c
        else:
            if count != '':
                exp[-1][1] = int(count)

            if c.isupper() and atom != '':
                exp.append([get_atom(atom), 1])
                atom = ''

            count = ''
            atom += c

    if atom != '':
        exp.append([get_atom(atom), 1])
    if count != '':
        exp[-1][1] = int(count)

    return exp


def get_hashed_index(mi_pair_list):
    """Create a hash-based index for efficient mass lookup.

    :noindex:

    Args:
        mi_pair_list (list): List of [mass, intensity] pairs, sorted by mass

    Returns:
        list: Index structure where each element contains start/end indices for
            masses falling into that integer mass bin

    Note:
        Creates an auxiliary data structure to enable fast binary search within
        a smaller range when looking up masses
    """

    aux_index_list = [None] * int(float(mi_pair_list[-1][0]) + 1.0)
    index = 0
    for i in mi_pair_list:
        num = int(float(i[0]))
        if num not in aux_index_list:
            aux_index_list[num] = {}
        if('start' not in aux_index_list[num]):
            if index == 0:
                aux_index_list[num]['start'] = 0
            else:
                aux_index_list[num]['start'] = index - 1

        index += 1
        aux_index_list[num]['end'] = index

    return aux_index_list


def search(mi_pair_list, preculated_mass, aux_index_list, ppm):
    """Search for masses within a PPM tolerance range.

    :noindex:

    Args:
        mi_pair_list (list): List of [mass, intensity] pairs sorted by mass
        preculated_mass (float): Target mass to search for
        aux_index_list (list): Index structure from get_hashed_index()
        ppm (float): Parts per million tolerance for matching

    Returns:
        list: Indices of all masses in mi_pair_list that fall within the PPM
            tolerance range of the target mass

    Note:
        Uses the auxiliary index to narrow the search range before doing
        detailed PPM tolerance comparisons
    """
    # eps = preculated_mass * 0.000001
    # eps = preculated_mass * 0.0000005
    eps = preculated_mass * ppm
    # https://www.as.uky.edu/sites/default/files/jeolelemental.pdf

    hash_value = float(preculated_mass)
    start_hash = int(hash_value - 1.0)
    end_hash = int(hash_value + 1.0)

    if start_hash >= len(aux_index_list):
        return []

    if end_hash >= len(aux_index_list):
        end_hash = len(aux_index_list)

    # Search start index
    start = 0
    while True:
        # print(start_hash, end_hash, len(aux_index_list), preculated_mass)
        if aux_index_list[start_hash] == None:
            start_hash -= 1
        else:
            start = aux_index_list[start_hash]['start']
            break

        if start_hash == 0:
            break

    # Search end index
    end = len(mi_pair_list)
    while True:
        if end_hash == len(aux_index_list):
            break
        if aux_index_list[end_hash] == None:
            end_hash += 1
        else:
            end = aux_index_list[end_hash]['end']
            break

    # max_intensity = -1
    # max_index = -1
    index_list = []
    for index in range(start, end):
   
        mass = float(mi_pair_list[index][0])

        if preculated_mass < (mass + eps) and preculated_mass > (mass - eps):
            index_list.append(index)

    return index_list
