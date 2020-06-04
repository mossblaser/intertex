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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'sphinx_doc_a'
copyright = '2020, Jonathan Heathcote'
author = 'Jonathan Heathcote'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinxcontrib.intertex",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    "python": ("http://docs.python.org/3", None),
    "ast": ("https://greentreesnakes.readthedocs.io/en/latest/", None),
    "sympy": ("https://docs.sympy.org/latest/", None),
}


# -- Options for intertex ----------------------------------------------------

intertex_mapping = {
    "sphinx-doc-b": "../sphinx_doc_b/build/latex/*.aux",
    "latex-doc": "../latex_doc/*.aux",
}

# While the other modules' documentation is not published publicly online,
# we'll use Intersphinx in the HTML too.
intertex_formats = ["html", "latex"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for PDF output --------------------------------------------------

# Show page numbers in references
latex_show_pagerefs = True

# Show hyperlink URLs in footnotes
latex_show_urls = "footnote"
