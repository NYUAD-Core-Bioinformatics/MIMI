Installation
============

Requirements
------------    
MIMI requires:

* Python >= 3.11.11
* numpy
* pandas
* json5
* urllib3
* tqdm
* requests

Installation Methods
--------------------

Using conda (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~
The easiest way to install MIMI is through conda::

    conda  install -c bioconda  mimi

This will automatically install all required dependencies.

From source
~~~~~~~~~~~~
If you prefer to install from source, follow these steps:

1. Clone the repository::

    git clone https://github.com/NYUAD-Core-Bioinformatics/MIMI.git
    cd MIMI

2. Install the package::

    pip install .

This will install MIMI and all its dependencies. If you encounter any issues, make sure you have all the required dependencies installed first.

Verification
------------
To verify your installation, you can run::

    mimi --version

This should display the installed version of MIMI.

