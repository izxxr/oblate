# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../../'))

# See comment in oblate/config.py (GlobalConfig.__set__)
os.environ['SPHINX_BUILD'] = '1'

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Oblate'
copyright = '2023, Izhar Ahmad (izxxr)'
author = 'Izhar Ahmad (izxxr)'
release = '1.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']

html_theme_options = {
    "github_url": "https://github.com/izxxr/oblate",
    "show_toc_level": 4,
}

# Autodoc
autodoc_typehints = 'none'
autodoc_member_order = 'bysource'
autodoc_inherit_docstrings = False
