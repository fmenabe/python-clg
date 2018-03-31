***
CLG
***

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

This module aims to simplify the creation of command-line interface (CLI) by using
configuration instead of writing Python code. The configuration is a predefined structure
represented by a dictionary and therefore can easily be moved into YAML or JSON files.

It wraps the standard `argparse <http://docs.python.org/dev/library/argparse.html>`_
module and almost everything possible with it can be done:

    * commands with options and arguments,
    * nested commands,
    * use of groups and exclusive groups,
    * use of builtins,
    * use of custom types, actions, ...
    * ...

There are also additionnals features like:

    * automatically execute a function in a Python file or module that takes the
      command-line arguments,
    * post checking arguments (dependencies between arguments, pattern matching on
      arguments values, ...),
    * cosmetics things like paginate the help or add a root *help* command that shows
      the tree of commands with theirs descriptions
    * integration with `argcomplete <http://argcomplete.readthedocs.io/en/latest/>`_ for
      Bash and Zsh completion

.. toctree::
    :hidden:
    :maxdepth: 3

    installation_and_usage
    configuration
    examples
