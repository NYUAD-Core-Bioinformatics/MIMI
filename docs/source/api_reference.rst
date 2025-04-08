API Reference
==============

This section provides detailed information about MIMI's Python API.

mimi.analysis
-------------
.. automodule:: mimi.analysis
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

Core analysis functions for processing mass spectrometry data, including:

* ``load_molecular_mass_database``: Load compound data from TSV files
* ``load_mass_spectrometry_data``: Load mass intensity data from ASC files
* ``create_mass_hash_index``: Create efficient lookup index for masses
* ``get_atom_counts``: Count atoms in molecular formulas
* ``create_logger``: Setup logging for analysis runs
* ``main``: Main entry point for analysis tool
* ``process_match``: Process matching compounds

mimi.atom
---------
.. automodule:: mimi.atom
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

Functions for handling atomic data and isotope information:

* ``load_labelled_atoms``: Load labeled atom data from JSON
* ``load_isotope``: Load isotope data from default file
* ``get_atom``: Get atom information by symbol
* ``get_exact_mass``: Get exact mass for specific isotope
* ``validate_isotope_data``: Validate isotope abundance values
* ``validate_isotope_order_and_consistency``: Validate isotope ordering

mimi.molecule
-------------
.. automodule:: mimi.molecule
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

Functions for processing molecular formulas and calculating masses:

* ``calculate_nominal_mass``: Calculate mass of a molecule
* ``calculate_mass``: Calculate mass with ion adjustments
* ``get_isotop_variants_mass``: Calculate mass variants for isotopes
* ``parse_molecular_formula``: Parse a molecular formula string
* ``get_hashed_index``: Create index for fast lookup
* ``search``: Search molecular mass data within PPM tolerance

mimi.create_cache
-----------------
.. automodule:: mimi.create_cache
   :members:
   :undoc-members:
   :show-inheritance:

Functions for creating precomputed caches:

* ``load_mass_spectrometry_data``: Load mass intensity data
* ``main``: Main entry point for cache creation tool

mimi.dump_cache
---------------
.. automodule:: mimi.dump_cache
   :members:
   :undoc-members:
   :show-inheritance:

Functions for dumping cache contents:

* ``format_cf_with_masses``: Format chemical formula with masses
* ``dump_cache``: Dump cache contents to TSV
* ``main``: Main entry point for cache dump tool

mimi.hmdb
---------
.. automodule:: mimi.hmdb
   :members:
   :undoc-members:
   :show-inheritance:

Functions for HMDB database extraction:

* ``parse_hmdb_xml``: Parse HMDB metabolites XML file
* ``export_metabolites_to_tsv``: Export metabolites to TSV format
* ``main``: Main entry point for HMDB extraction tool

mimi.kegg
---------
.. automodule:: mimi.kegg
   :members:
   :undoc-members:
   :show-inheritance:

Functions for KEGG database extraction:

* ``get_compounds_by_mass_range``: Get KEGG compounds by mass range
* ``get_compound_info_batch``: Get information for multiple compounds
* ``export_compounds_to_tsv``: Export compounds to TSV format
* ``main``: Main entry point for KEGG extraction tool 