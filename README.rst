Command-line generator in python
================================

.. image:: https://img.shields.io/pypi/l/clg.svg
		   :target: https://opensource.org/licenses/MIT
		   :alt: License

.. image:: https://img.shields.io/pypi/pyversions/clg.svg
           :target: https://pypi.python.org/pypi/clg
           :alt: Versions

.. image:: https://img.shields.io/pypi/v/clg.svg
           :target: https://pypi.python.org/pypi/clg
           :alt: PyPi

.. image:: https://img.shields.io/badge/github-repo-yellow.jpg
           :target: https://github.com/fmenabe/python-clg
           :alt: Code repo

.. image:: https://readthedocs.org/projects/clg/badge/?version=latest
           :target: http://clg.readthedocs.org/en/latest/
           :alt: Documentation

.. image:: https://landscape.io/github/fmenabe/python-clg/master/landscape.svg?style=flat
           :target: https://landscape.io/github/fmenabe/python-clg/master
           :alt: Code Health

.. image:: https://img.shields.io/pypi/dm/clg.svg
           :target: https://pypi.python.org/pypi/clg
           :alt: Downloads

This module is a wrapper to **argparse** module. Its goal is to generate a
custom and advanced command-line from a formatted dictionary. As python
dictionnaries are easily exportable to configuration files (like YAML or JSON),
the idea is to outsource the command-line definition to a file instead of
writing dozens or hundreds lines of code.

Code is available on Github (http://github.com/fmenabe/python-clg).

Documentation is available on readthedocs (https://clg.readthedocs.org/en/latest/).

Releases notes
--------------
2.2.0 (2016-06-09)
~~~~~~~~~~~~~~~~~~
    * Add a ``negative_value`` parameter for parsers allowing to redefine how
      negatives values are distinguished from options
      (`4c7e7be <https://github.com/fmenabe/python-clg/commit/4c7e7be>`_).

2.1.1 (2016-05-08)
~~~~~~~~~~~~~~~~~~
    * ``print_help`` parameter is not anymore a root parameter but a per command
      parameter and simulate the use of the `--help` option if no arguments are
      supplied (`6bee4d9 <https://github.com/fmenabe/python-clg/commit/6bee4d9>`_).
      This allows flexibiliy for (sub)commands that do not require any input.

2.1.0 (2016-05-08)
~~~~~~~~~~~~~~~~~~
    * Remove empty list for default value when ``nargs`` is set to *\** or *+*
      (`4102816 <https://github.com/fmenabe/python-clg/commit/4102816>`_).
    * Allows to add custom actions by updating ``ACTIONS`` dictionnary
      (`65d7480 <https://github.com/fmenabe/python-clg/commit/65d7480>`_).
    * Add a ``page_help`` action allowing to page help
      (`818383b <https://github.com/fmenabe/python-clg/commit/818383b>`_,
      `f788f35 <https://github.com/fmenabe/python-clg/commit/f788f35>`_).
    * Add the parameter ``page_help`` at the root of the configuration allowing
      to page the help of all commands (by replacing the default ``help`` action
      by the ``page_help`` action;
      `9454f7a <https://github.com/fmenabe/python-clg/commit/9454f7a>`_).
    * Add the parameter ``print_help`` at the root of the configuration
      allowing to print help when no arguments is set (also work for subcommands;
      `5ea6fe8 <https://github.com/fmenabe/python-clg/commit/5ea6fe8>`_)

2.0.0 (2015-06-25)
~~~~~~~~~~~~~~~~~~
    * Change behaviour of groups: groups now act like parsers rather than just
      referencing previously defined options. **It breaks files used by previous
      versions**.
    * Update design and correct bugs of the ``help`` command added by the
      *add_help_cmd* keyword.
    * Improve control of abbrevations behaviour. When ``allow_abbrev`` parameter
      was activate, it was not possible to concatenate single options or split
      with an '=' long options. This is now the case.
    * Correct a bug with YAML anchors which causes loss of informations (like
      the short option).

1.1.1 (2015-02-24)
~~~~~~~~~~~~~~~~~~
  * Correct a bug when using ``version`` action.

1.1 (2015-02-17)
~~~~~~~~~~~~~~~~
  * Add a ``version`` keyword for options, allowing to use ``version`` action.
  * Allow an option ``add_help_cmd`` in the root of the configuration that
    automatically add a ``help`` command that show the arborescence of all
    commands with their descriptions.
  * Allow the use of ``argparse.SUPPRESS`` with ``__SUPPRESS__`` "builtin".
  * Replace the "builtins" __CHOICES__, __MATCH__ and __FILE__ in the help
    message by the respectives values of those keywords.
  * Add the parameter ``allow_abbrev`` in parser configuration, controlling
    abbrevations behaviour (http://bugs.python.org/issue14910).

1.0 (2014-10-28)
~~~~~~~~~~~~~~~~
  * Rewrite module for matching at best ``argparse``.
  * Allow bultins.
  * Drop compatibility to python2.6 (because of dict comprehension).

0.5 (2013-11-25)
~~~~~~~~~~~~~~~~
  * Port code to Python 3 (with compatiblity at least until Python 2.6).

0.4 (2013-11-14)
~~~~~~~~~~~~~~~~
  * Add description of parser (via *desc* keyword).

0.3 (2013-08-09)
~~~~~~~~~~~~~~~~
  * Add an iterable and accessible namespace for arguments.
  * Change behaviour of *parse* method (now return a namespace with arguments).
  * Set the default value for *list* type to an empty list.
  * Changes the behaviour of the execution of an external module. It is no
    longer a python path of a module in 'sys.path' but directly the path of a
    file. In addition, keyword 'lib' has be replaced by 'path'.
  * Replace '__FILE__' in the default value of an option by the directory of the
    program.
  * Update the license to MIT.

0.2 (2013-07-21)
~~~~~~~~~~~~~~~~
  * **CommandLine** object doesn't take anymore a JSON or YAML file but a
    dictionary.
  * Add documentation.
  * Updating setup for PyPi.
