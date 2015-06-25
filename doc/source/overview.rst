********
Overview
********

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

Some additionnal features have also been implemented.

.. note:: When printing the help message, order of options/arguments/commands
   may be important. ``json`` module has a parameter (``object_pairs_hook``) for
   keeping the order of keys when loading a file. For YAML, it is possible to
   use the module `yamlorderedictloader <https://pypi.python.org/pypi/yamlordereddictloader>`_
   which provide a **Loader** allowing to keep order.

Installation
============
This module is compatible with python2.7 and python3+. It is on
`PyPi <https://pypi.python.org/pypi/clg>`_ so you can use the ``pip``
command for installing it. If you use YAML for your configuration file, you need
to install the ``pyyaml`` module too (and ``yamlordereddictloader`` for ordered
configuration). ``json`` module is a standard module since python2.7.

Otherwise sources are on `github <https://github.com/fmenabe/python-clg>`_

Usage
=====
The main program is very simple. You need to import the necessaries modules
(``clg`` and the modules for loading the configuration from a file). Then, you
initialize the **CommandLine** object with the dictionary containing the
configuration. Finally, like ``argparse`` module, you call the **parse** method for
parsing the command-line. This method returns in all case the arguments of the
command-line but, if there is an `execute <configuration.html#execute>`_ section
for the command, this will be executed first. The arguments are returned in a
**Namespace** object inheriting from ``argparse``
`Namespace <https://docs.python.org/dev/library/argparse.html#argparse.Namespace>`_
object but with additionals methods for making it iterable and allowing to
access arguments with both attributes and list syntax.


With YAML
---------
*Configuration file*:

.. code-block:: yaml

    options:
        foo:
            short: f
            help: Foo help.
        bar
            short: b
            help: Bar help.

*Python program*:

.. code-block:: python

    import clg
    import yaml
    import yamlordereddictloader

    cmd_conf = yaml.load(open('cmd'), Loader=yamlordereddictloader.Loader)
    cmd = clg.CommandLine(cmd_conf)
    args = cmd.parse()

    # From here, we treat the arguments.
    print("Namespace object: %s" % args)
    print("Namespace attributes: %s" % vars(args))
    print("Iter arguments:")
    for arg, value in args:
        print("  %s: %s" % (arg, value))
    print("Access 'foo' option with attribute syntax: %s" % args.foo)
    print("Access 'foo' option with list syntax: %s" % args['foo'])

.. _exec:

*Execution*:

.. code:: bash

    # python prog.py --help
    usage: prog.py [-h] [-f FOO] [-b BAR]

    optional arguments:
      -h, --help         show this help message and exit
      -f FOO, --foo FOO  Foo help.
      -b BAR, --bar BAR  Bar help

    # python prog.py -f foo -b bar
    Print Namespace object: Namespace(bar='bar', foo='foo')
    Print Namespace attributes: {'foo': 'foo', 'bar': 'bar'}
    Iter arguments:
      foo: foo
      bar: bar
    Access 'foo' option with attribute syntax: foo
    Access 'foo' option with list syntax: foo


With JSON
----------
*Configuration file*:

.. code-block:: json

    {"options": {"foo": {"short": "f",
                         "help": "Foo help."},
                 "bar": {"short": "b",
                         "help": "Bar help."}}}


*Python program*:

.. code-block:: python

    import clg
    import json
    from collections import OrderedDict

    cmd_conf = json.load(open('cmd'), object_pairs_hook=OrderedDict)
    cmd = clg.CommandLine(cmd_conf)
    args = cmd.parse()

    # From here, we treat the arguments.
    print("Namespace object: %s" % args)
    print("Namespace attributes: %s" % vars(args))
    print("Iter arguments:")
    for arg, value in args:
        print("  %s: %s" % (arg, value))
    print("Access 'first' option with attribute syntax: %s" % args.first)
    print("Access 'first' option with list syntax: %s" % args['first'])


*Execution*:

Same as `before <#exec>`_.
