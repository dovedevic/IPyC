# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys

sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('extensions'))

# -- Project information -----------------------------------------------------

project = 'IPyC'
copyright = '2020-present, dovedevic'
author = 'dovedevic'

# The full version, including alpha/beta/rc tags
release = 'v1.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
  'resourcelinks',
  'sphinx.ext.autodoc',
  'sphinx.ext.extlinks',
  'sphinx.ext.intersphinx',
  'sphinx.ext.napoleon',
  'sphinx_rtd_theme'
]

# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None)
}

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

resource_links = {
  'issues': 'https://github.com/dovedevic/IPyC/issues',
  'examples': 'https://github.com/dovedevic/IPyC/tree/master/examples',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
