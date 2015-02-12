*************
Configuration
*************

As indicated before, configuration is a dictionnary. It recursively defines the
commands configuration. The configuration of a command is a mix of keywords
between the ``argparse`` module and this module. Keywords for defining a command
are:

    * **prog** (argparse)
    * **usage** (argparse)
    * **description** (argparse)
    * **epilog** (argparse)
    * **formatter_class** (argparse)
    * **argument_default** (argparse)
    * **conflict_handler** (argparse)
    * **add_help** (argparse)
    * **allow_abbrev** (clg)
    * **anchors** (clg)
    * **options** (clg)
    * **args** (clg)
    * **groups** (clg)
    * **exclusive_groups** (clg)
    * **execute** (clg)
    * **subparsers** (clg)



prog
----
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#prog>`_

Set the name of the program. By default, it match how the program was invoked
on the command line.



usage
-----
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#usage>`_

Set the usage of the command.



description
-----------
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#description>`_

Add a description of the command in the help.



epilog
------
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#epilog>`_

Add a comment at the end of the help.



formatter_class
---------------
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#formatter-class>`_

This is the name of one of the ``argparse`` class (**HelpFormatter** by
default). For example:


.. code:: yaml

    formatter_class: RawTextHelpFormatter



argument_default
----------------
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#argument-default>`_

The global default value for arguments (default: None).



conflict_handler
----------------
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#conflict-handler>`_

Indicate how to handle conflict between options.



add_help
--------
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#add-help>`_

Indicate whether a default ``-h``/``--help`` option is added to the command-line,
allowing to print help. You may need to have a better control on this option
(for putting the option in a group, customizing the help message, removing the
short option, ...). You can manually set this option by using theses values:

.. code:: yaml

    options:
        help:
          short: h
          action: help
          default: __SUPPRESS__
          help: show this help message and exit
        ...



allow_abbrev
-------------
Boolean (default: *False*) indicating whether `abrevations
<https://docs.python.org/dev/library/argparse.html#argument-abbreviations-prefix-matching>`_
are allowed.

.. note:: The default behavior of ``argparse`` is to allow abbrevation but
    ``clg`` module disable this "feature" by default.



anchors
-------
This section has been created for YAML files. You can defined any structure in
here (like common options between commands) and use it anywhere through YAML
anchors.



.. _options:

options
-------
This section defines the options of the current command. It is a dictionnary
whose keys are the name of the option (long format beginning with two dashes in
the command-line) and values a hash with the configuration of the option. In
``argparse`` module, **dest** keyword defines the keys in the resulted
Namespace. It is not possible to overload this parameter as the name of the
option in the configuration is used as destination.

Keywords:

    * **short** (clg)
    * **help** (argparse)
    * **required** (argparse)
    * **default** (argparse)
    * **choices** (argparse)
    * **action** (argparse)
    * **nargs** (argparse)
    * **const** (argparse)
    * **metavar** (argparse)
    * **type** (argparse)
    * **need** (clg)
    * **conflict** (clg)
    * **match** (clg)

.. note:: Options with underscores and spaces in the configuration are replaced
   by dashes in the command (but not in the resulted Namespace). For example,
   an option ``my_opt`` in the configuration will be rendered as ``--my-opt`` in
   the command.

It is possible to use builtins in some options (**default**, **const**, ...).
For this, a special syntax is used. The builtin can be defined in uppercase,
prefixing and sufixing by double underscores: ``__BUILTIN__``. For example:

.. code-block:: yaml

    options:
        sum:
            action: store_const
            const: __SUM__
            default: __MAX__
            help: "sum the integers (default: find the max)"

In the same way, there are specials "builtins":
    * ``__DEFAULT__``: this is replaced in the help message by the value of
      **default** option.
    * ``__MATCH__``: this is replaced in the help message by the value of
      **match** option.
    * ``__CHOICES__``: this is replace in the help message by the value of
      **choices** option (choices are separated by commas).
    * ``__FILE__``: this "builtin" is replaced by the path of the main program
      (**sys.path[0]**). This allow to define file relatively to the main
      program (ex: *__FILE__/conf/someconf.yml*, *__FILE__/logs/*).
    * ``__SUPPRESS__``: identical to ``argparse.SUPPRESS`` (no attribute is
      added to the resulted Namespace if the command-line argument is not
      present).


short
~~~~~
This section must contain a single letter defining the short name (beginning
with a single dash) of the current option.


help
~~~~
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#help>`_

Description of the option.


required
~~~~~~~~
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#required>`_

Boolean indicating whether the option is necessary.


type
~~~~
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#type>`_

This option indicate the type of the option. As this is necessarily a builtin,
this is not necessary to use the ``__BULTIN__`` syntax.

It is possible to add custom types. For this, you must define a function
that check the given value for the option and add this function to
``clg.TYPES``. For example, to add a custom ``Date`` type based on french date
format (DD/MM/YYYY) and returning a ``datetime`` object:

*Python program*:

.. code-block:: python

    import clg
    import yaml

    def Date(value):
        from datetime import datetime
        try:
            return datetime.strptime(value, '%d/%m/%Y')
        except Exception as err:
            raise clg.argparse.ArgumentTypeError(err)
    clg.TYPES['Date'] = Date

    command = clg.CommandLine(yaml.load(open('cmd.yml'))
    args = command.parse()

*YAML configuration*:

.. code-block:: yaml

    ...
    options:
        date:
            short: d
            type: Date
            help: Date.
    ...


default
~~~~~~~
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#default>`_

Set a default value for the option.


choices
~~~~~~~
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#choices>`_

This is a list indicating the possible values for the option.


action
~~~~~~
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#action>`_

This indicate what to do with the value.


nargs
~~~~~
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#nargs>`_

This allow to define the number of values of an option (by default, an option
look for only one argument).


const
~~~~~
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#const>`_

Value in the Namespace if the option is not set in the command-line (*None* by
default).

.. note:: If **nargs** is defined for the option, the default value will be an
   empty list.


metavar
~~~~~~~
**argparse link**: `<http://docs.python.org/dev/library/argparse.html#metavar>`_

Representation in the help of the value of an option.


need
~~~~
This is a list of options needed with the current option.


conflict
~~~~~~~~
This is a list of options that must not be used with the current option.


match
~~~~~
This is a regular expression that the option's value must match.



args
----
This section define arguments of the current command. It is identical as the
`options`_ section at the exception of the **short** and **version** keywords
which are not available.



groups
------
This section is a list of groups. Each
`group <https://docs.python.org/dev/library/argparse.html#argument-groups>`_
can have theses keywords:

    * **title** (argparse)
    * **description** (argparse)
    * **options** (clg)

.. note:: All ``argparse`` examples set ``add_help`` to *False*. If this is set,
   ``help`` option is put in *optional arguments*. If you want to put the
   ``help`` option in a group, you need to set the help option
   `manually <configuration.html#add_help>`_.


title
~~~~~
Customize help with a title.


description
~~~~~~~~~~~
Customize help with a description


options
~~~~~~~
List with the options of the group. Theses options must be defined in the
`options`_ section.



exclusive groups
----------------
This section is a list of
`exclusive groups <https://docs.python.org/dev/library/argparse.html#mutual-exclusion>`_.
Each group can have theses keywords:

    * **required** (argparse)
    * **options** (clg)


required
~~~~~~~~
Boolean indicating if at least one of the arguments is required.


options
~~~~~~~
List with the options of the group. Theses options must be defined in the
`options`_ section.



execute
-------
This section indicate what must be done after the command is parsed. It
allow to import a file or a module and launch a function in it. This function
only take one argument which is the **Namespace** containing arguments.

Keywords:
    * **module**
    * **file**
    * **function**

.. note:: **module** and **file** keywords can't be used simultaneously.

file
~~~~
This is a string indicating the path of a python file.


module
~~~~~~
This is a string indicating the module to load (ex: package.subpackage.module).
This recursively load all intermediary packages until the module. As the
directory of the main program is automatically in ``sys.path``, that allows to
import modules relatively to the main program.

For example, the directory structure of your program could be like this:

.. code:: bash

    .
    ├── prog.py                 => Main program intializing clg
    ├── conf/cmd.yml            => Command-line configuration
    └── commands/               => commands package directory
        ├── __init__.py
        └── list                => commands.list subpackage directory
            ├── __init__.py
            └── users.py        => users module in commands.list subpackage

.. _subparsers_yaml:

And the configuration syntax is:

.. code-block:: yaml

    subparsers:
        list:
            subparsers:
                users:
                    execute:
                        module: commands.list.users

This will execute the ``main`` function if the file *commands/list/users.py*.


function
~~~~~~~~
This is the function in the loaded file or module that will be executed
(default: ``main``).



subparsers
----------
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#argparse.ArgumentParser.add_subparsers>`_

This allow to add subcommands to the current command.

Keywords:
    * **help** (argparse)
    * **title** (argparse)
    * **description** (argparse)
    * **prog** (argparse)
    * **help** (argparse)
    * **metavar** (argparse)
    * **parsers** (clg)
    * **required** (clg)

.. note:: It is possible to directly set parsers configurations (the content of
   **parsers** subsection) in this section. The module check for the presence
   of **parsers** section and, if not present, consider this is subcommands
   configurations.

When using subparsers and for being able to retrieves configuration of
the used (sub)command, **dest** argument of ``add_subparsers`` method is used.
It add in the resulted **Namespace** an entry whose key is the value of **dest**
and the value the used subparser. The key is generated from the **keyword**
argument (default: *command*) of the **CommandLine** object, incremented at each
level of the arborescence. From the `previous example <#subparsers_yaml>`_ the
resulted **Namespace** is:

.. code:: bash

    # python prog.py list users
    Namespace(command0='list', command1='users')


title
~~~~~
Customize the help with a title.


description
~~~~~~~~~~~
Customize the help with a description


help
~~~~
Additional help message.


prog
~~~~
Customize usage in help.


help
~~~~
Help for sub-parser group in help output.


metavar
~~~~~~~
String presenting available sub-commands in help


parsers
~~~~~~~
This is a hash whose keys are the name of subcommands and values the
configuration of the command.


required
~~~~~~~~
Indicate whether a subcommand is required.
