*****************
CLG Documentation
*****************

This module is a wrapper to the `argparse <http://docs.python.org/dev/library/argparse.html>`_
module. It aims to generate a custom and advanced command-line by defining the
configuration in a formatted dictionary. It is easy to export Python
dictionnaries to files (like YAML or JSON) so the idea is to outsource the
command-line definition to a file instead of writting dozens or hundreds lines
of code.

Almost everything possible with ``argparse`` can be done with this module. This
include:

    * parsers with both `options <configuration.html#options>`_,
      `arguments <configuration.html#args>`_ and
      `subparsers <configuration.html#subparsers>`_,
    * no limit for the arborescence of subparsers,
    * use of `groups <configuration.html#groups>`_ and `exclusive groups <configuration.html#exclusive-groups>`_,
    * use of `builtins <configuration.html#options>`_,
    * use of `custom types <configuration.html#type>`_,
    * ...

There's also additionnals features that have been implemented like post checking
the arguments (dependencies between arguments, checking the value of an argument
match a pattern, ...), the possibilty to pass arguments to a function of a python
file or module, paging help, ...

Table of content
================
.. toctree::
    :maxdepth: 3

    installation_and_usage
    configuration
    examples
