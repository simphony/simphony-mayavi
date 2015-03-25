# -*- coding: utf-8 -*-
#
# SimPhoNy-Mayavi documentation build configuration file
#


def mock_modules():
    import sys

    from mock import MagicMock

    try:
        import numpy  # noqa
    except ImportError:
        MOCK_MODULES = ['numpy']
    else:
        MOCK_MODULES = []

    try:
        import simphony  # noqa
    except ImportError:
        MOCK_MODULES.append('simphony')

    try:
        import mayavi  # noqa
    except ImportError:
        MOCK_MODULES.append('mayavi')

    class Mock(MagicMock):

        @classmethod
        def __getattr__(cls, name):
            return Mock()

        def __call__(self, *args, **kwards):
            return Mock()

    sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)
    print 'mocking {}'.format(MOCK_MODULES)


# -- General configuration ------------------------------------------------

# check and mock missing modules
mock_modules()

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'trait_documenter',
    'sectiondoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'SimPhoNy'
copyright = u'2015, SimPhoNy FP7 Collaboration'
version = '0.1.0'
release = '0.1.0.dev0'
pygments_style = 'sphinx'
# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'http://docs.python.org/': None}

# -- Options for HTML output ----------------------------------------------

html_theme = 'default'
html_logo = '_static/simphony_logo.png'
html_static_path = ['_static']
htmlhelp_basename = 'SimPhoNy-MayaviDoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}
latex_documents = [(
    'index', 'SimPhoNy-Mayavi.tex', u'SimPhoNy-Mayavi Documentation',
    u'SimPhoNy FP7 Collaboration', 'manual')]
latex_logo = '_static/simphony_logo.png'

# -- Options for manual page output ---------------------------------------

man_pages = [(
    'index', 'simphony', u'SimPhoNy-Mayavi Documentation',
    [u'SimPhoNy FP7 Collaboration'], 1)]

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [(
    'index', 'SimPhoNy', u'SimPhoNy-Mayavi Documentation',
    u'SimPhoNy FP7 Collaboration', 'SimPhoNy-Mayavi', 'Visualisation tools',
    'Miscellaneous'),
]

# -- Options for Epub output ----------------------------------------------

epub_title = u'SimPhoNy'
epub_author = u'SimPhoNy FP7 Collaboration'
epub_publisher = u'SimPhoNy FP7 Collaboration'
epub_copyright = u'2015, SimPhoNy FP7 Collaboration'
epub_exclude_files = ['search.html']
