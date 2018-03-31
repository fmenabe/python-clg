# -*- coding: utf-8 -*-


# -- General configuration -----------------------------------------------------

# General project informations.
from datetime import date
project = u'clg'
description = 'Simple way to generate command-lines from configuration'
version = '3.0'
release = '3.0.0'
year = date.today().year
author = u'François Ménabé'
copyright = u'{:d}, {:s}'.format(year, author)

# Sphinx configuration.
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = []
# The reST default role (used for this markup: `text`) to use for all documents.
default_role = 'py:obj'
pygments_style = 'sphinx'

# Sphinx default extensions.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode'
]


# -- Options for HTML output ---------------------------------------------------

html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'

# Custom CSS for code caption. 
def setup(app):
    app.add_stylesheet('css/code_caption.css')


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'clg.tex', u'clg Documentation',
   u'François Ménabé', 'manual'),
]


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'clg', u'clg Documentation',
     [u'François Ménabé'], 1)
]


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'clg', u'clg Documentation',
   u'François Ménabé', 'clg', 'One line description of project.',
   'Miscellaneous'),
]


# -- Options for Epub output ---------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = u'clg'
epub_author = u'François Ménabé'
epub_publisher = u'François Ménabé'
epub_copyright = u'{:d}, François Ménabé'.format(year)
