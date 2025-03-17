README file for “Atomic_masses_and_isotope_compositions_NIST.txt"

Kris Gunsalus 2025-02-26

————————————————————————————————————————————————————————————

Relative atomic masses for all elements and isotopic composition of most common isotopes (any isotope with a given natural abundance)

Citation: 
Coursey, J.S., Schwab, D.J., Tsai, J.J., and Dragoset, R.A. (2015), Atomic Weights and Isotopic Compositions (version 4.1). [Online] Available: http://physics.nist.gov/Comp [Downloaded Feb 26, 2025]. National Institute of Standards and Technology, Gaithersburg, MD.

File downloaded using NIST webform (indicated in citation above) using “All Elements”, “Linearized ASCII Output”, “Most common isotopes”

Note: v4.1 was released in July 2015
See https://doi.org/10.1515/pac-2016-0402 for explanation of uncertainties in atomic weights (IUPAC Technical Report)

Uncertainties in parentheses (uncertainty in last digit or digits) and brackets [uncertainty in measurement] were ignored in generating MIMI .json file
MIMI data file generated using this data is called "natural_isotope_abundance_NIST.json" 

————————————————————————————————————————————————————————————

MIMI field correspondence:
  Atomic Number 	=> periodic_number
  Atomic Symbol 	=> element_symbol
  Mass Number   	=> nominal_mass
  Relative Atomic Mass 	=> exact_mass
  Isotopic Composition 	=> natural_abundance

Example of MIMI .json format:

  "H": [
            {
                  "periodic_number": 1,
                  "element_symbol": "H",
                  "nominal_mass": 1,
                  "exact_mass": 1.00782503223,
                  "natural_abundance": 0.999885,
                  "highest_abundance": 0.999885
            },
            {
                  "periodic_number": 1,
                  "element_symbol": "H",
                  "nominal_mass": 2,
                  "exact_mass": 2.01410177812,
                  "natural_abundance": 0.000115,
                  "highest_abundance": 0.999885
            }
      ],

————————————————————————————————————————————————————————————
