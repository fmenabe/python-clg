Command-line generator in python
================================

This module is a wrapper to **argparse** module. Its goal is to generate a
custom and advanced command-line from a formatted dictionary. As python
dictionnaries are easily exportable to configuration files (like YAML or JSON),
the idea is to outsource the command-line definition to a file instead of
writing dozens or hundreds lines of code.

Code is available on Github (http://github.com/fmenabe/python-clg).

Documentation is available on readthedocs (https://clg.readthedocs.org/en/latest/).

Releases notes
--------------
2.0.0 (unreleased)
~~~~~~~~~~~~~~~~~~
    * Change behaviour of groups: groups now act like parsers rather than just
      referencing previously defined options. **It breaks files used by previous
      versions.**
    * Update design of the 'help' command added by the 'add_help_cmd' keyword.

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
