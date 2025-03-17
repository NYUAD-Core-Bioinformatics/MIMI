# -*- coding: utf-8 -*-

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


import os
from setuptools import setup, find_packages
import sys
from urllib.request import urlretrieve

# Package metadata
DISTNAME = 'mimi'
VERSION_FILE = os.path.join(os.path.dirname(__file__), 'mimi', 'VERSION')
README_FILE = os.path.join(os.path.dirname(__file__), 'README.md')

# Read version and README
with open(VERSION_FILE, encoding='utf-8') as version_fp:
    VERSION = version_fp.read().strip()

with open(README_FILE, 'r', encoding='utf-8') as readme_fp:
    LONG_DESCRIPTION = readme_fp.read().strip()

# Package configuration
MAINTAINER = 'Nabil Rahiman'
MAINTAINER_EMAIL = 'nabil.rahiman@nyu.edu'
LICENSE = 'MIT'
DESCRIPTION = "Molecular Isotope Mass Identifier"
INSTALL_REQUIRES = [
    'numpy',
    'pandas',
    'json5',
    'urllib3',
    'tqdm',
]
PYTHON_REQUIRES = '>=3.11.11'

CLASSIFIERS = [
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: >3',
    'Topic :: Scientific/Biology',
    'Topic :: Scientific/Bioinformatics',
    'Topic :: Scientific/Biology :: Information Analysis',
    'Topic :: Scientific/Biology :: Mass Spectrometry'
]

setup(
    name=DISTNAME,
    version=VERSION,
    author=MAINTAINER,
    author_email=MAINTAINER_EMAIL,
    packages=find_packages(include=['mimi', 'mimi.*']),
    package_data={
        'mimi': ['data/*.json', 'data/*.txt'],
    },
    entry_points={
        'console_scripts': [
            'mimi_mass_analysis=mimi.analysis:main',
            'mimi_cache_create=mimi.create_cache:main',
            'mimi_hmdb_extract=mimi.hmdb:main',
            'mimi_cache_dump=mimi.dump_cache:main',
            'mimi_kegg_extract=mimi.kegg:main'
        ],
    },
    url='https://github.com/GunsalusPiano/mass_spectrometry_tool',
    license=LICENSE,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    python_requires=PYTHON_REQUIRES,
)