********
Overview
********

This module is a wrapper to `argparse <http://docs.python.org/dev/library/argparse.html>`_
module . Its goal is to generate a custom and advanced command-line from a
formatted dictionary. As python dictionnaries are easily exportable to a file
like YAML or JSON, the idea is to outsource the command-line definition to a
file instead of writing dozens or hundreds lines of code. As it may be nice to
have the list of parsers/options/arguments ordered when printing the help, it
may be better to use an **OrderedDict** (from the ``collection`` module). JSON
module has an option (``object_pairs_hook``) allowing to keep order. For YAML,
you can use the module
`yamlorderedictloader <https://pypi.python.org/pypi/yamlordereddictloader>`_.

Almost everything available with ``argparse`` module is possible with this
module. This include:

    * use of builtins,
    * parsers with both options, arguments and subparsers,
    * no limit for the arborescence of subparsers,
    * use of groups and exclusive groups,
    * ...

For some complex behaviour, some additional checks have been implemented. This
module also provide a script for generating **bash** and **zsh** completion
scripts for a better integration with the system.

Installation
============
This module is not anymore compatible with python 2.6 (essentially because of
dict comprehension) but is compatible with python 2.7 and python 3. The module
is on `PyPi <https://pypi.python.org/pypi/clg>`_ so you can use the ``pip``
command for installing it. If you use YAML for your configuration file, you need
to install ``pyyaml`` module too (and ``yamlordereddictloader`` for ordered
configuration). ``json`` module is a standard module since python2.7.

For example, to use ``clg`` with YAML in a virtualenv:

.. code:: bash

   $ virtualenv env/ --prompt "(myprog)"
   $ . ./env/bin/activate
   (myprog) $ pip install pyyaml yamlordereddictloader clg


.. note:: The version of python in the virtualenv depend of your system. Some
   systems like archlinux have two commands (``virtualenv`` for python3 and
   ``virtualenv2`` for python2), others only have one command. In all case using
   the `-p` option for indicating the python executable must work (but,
   evidently, the python version you want must be installed in the system):

     ``virtualenv -p /usr/bin/python3.3 env/ --prompt "(myprog)"``


Otherwise sources are on `github <https://github.com/fmenabe/python-clg>`_

Usage
=====
The main program is very simple. You need to import the necessaries modules
(``clg`` and modules for loading configuration from a file) and to initialize
the **CommandLine** object, passing as arguments the dictionnary containing the
configuration. Then, using the *parse* method for parsing the command. This
method return in all case the arguments of the command-line but, if there is an
`execute <configuration.html#execute>`_ section for the command, this will be
executed first. The arguments are returned in a **Namespace** object inheriting
from `argparse <http://docs.python.org/dev/library/argparse.html#argparse.Namespace>`_
object but with additionals methods (*__getitem__*, *__setitem__* and *__iter__*)
for making it iterable and access arguments both with attributes or list syntax.


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
    print("Namespace object: %s" % args)
    print("Namespace attributes: %s" % vars(args))
    print("Iter arguments:")
    for arg, value in args:
        print("  %s: %s" % (arg, value))
    print("Access 'first' option with attribute syntax: %s" % args.first)
    print("Access 'first' option with list syntax: %s" % args['first'])


*Execution*:

Same as `before <#exec>`_.
