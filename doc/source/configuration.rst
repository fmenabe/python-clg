*************
Configuration
*************

The configuration of the command-line is done with a dictionnary that recursively
defines commands. Each command is a mix of keywords from ``argparse`` and this
module. Keywords for a command are:

    * **prog** (``argparse``)
    * **usage** (``argparse``)
    * **description** (``argparse``)
    * **epilog** (``argparse``)
    * **formatter_class** (``argparse``)
    * **argument_default** (``argparse``)
    * **conflict_handler** (``argparse``)
    * **add_help** (``argparse``)
    * **add_help_cmd** (``clg``)
    * **allow_abbrev** (``clg``)
    * **anchors** (``clg``)
    * **options** (``clg``)
    * **args** (``clg``)
    * **groups** (``clg``)
    * **exclusive_groups** (``clg``)
    * **subparsers** (``clg``)
    * **execute** (``clg``)



prog
----
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#prog>`_

Set the name of the program (default: ``sys.argv[0]``).



usage
-----
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#usage>`_

The string describing the program usage (default: generated from arguments added
to parser).



description
-----------
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#description>`_

Text to display before the argument help (default: none).



epilog
------
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#epilog>`_

Text to display after the argument help (default: none).



formatter_class
---------------
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#formatter-class>`_

A class for customizing the help output. It takes the name of one of the class
defining in ``argparse``:

.. code:: yaml

    formatter_class: RawTextHelpFormatter



argument_default
----------------
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#argument-default>`_

The global default value for arguments (default: *None*).



conflict_handler
----------------
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#conflict-handler>`_

The strategy for resolving conflicting optionals (usually unnecessary).



add_help
--------
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#add-help>`_

Add a ``-h``/``–help`` option to the parser (default: *True*) that allows to
print the help. You may need to have a better control on this option (for
putting the option in a group, customizing the help message, removing the short
option, ...). You can manually set this option by using theses values:

.. code:: yaml

    options:
        help:
          short: h
          action: help
          default: __SUPPRESS__
          help: My help message.
        ...



add_help_cmd
------------
Add a ``help`` subcommand at the root of the parser that print the arborsence of
commands with their description.


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
whose keys are the name of the option and values a hash with the configuration of
the option. In ``argparse`` module, **dest** keyword defines the keys in the
resulted Namespace. It is not possible to overload this parameter as the name of
the option in the configuration is used as destination.

Keywords:

    * **short** (``clg``)
    * **help** (``argparse``)
    * **required** (``argparse``)
    * **default** (``argparse``)
    * **choices** (``argparse``)
    * **action** (``argparse``)
    * **version** (``argparse``)
    * **nargs** (``argparse``)
    * **const** (``argparse``)
    * **metavar** (``argparse``)
    * **type** (``argparse``)
    * **need** (``clg``)
    * **conflict** (``clg``)
    * **match** (``clg``)

.. note:: Options with underscores and spaces in the configuration are replaced
   by dashes in the command (but not in the resulted Namespace). For example,
   an option ``my_opt`` in the configuration will be rendered as ``--my-opt`` in
   the command.

Some options (like **default**, **const**, ...) can use builtins values. For
managing it, a special syntax is used: the builtin can be defined in uppercase,
prefixed and sufixed by double underscores (``__BUILTIN__``). For example:

.. code-block:: yaml

    options:
        sum:
            action: store_const
            const: __SUM__
            default: __MAX__
            help: "sum the integers (default: find the max)"

In the same way, there are specials "builtins":
    * ``__DEFAULT__``: this is replaced in the help message by the value of the
      **default** option.
    * ``__MATCH__``: this is replaced in the help message by the value of the
      **match** option.
    * ``__CHOICES__``: this is replace in the help message by the value of the
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
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#help>`_

A brief description of what the argument does.


required
~~~~~~~~
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#required>`_

Whether or not the command-line option may be omitted.


type
~~~~
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#type>`_

The type to which the command-line argument should be converted. As this is
necessarily a builtin, this is not necessary to use the ``__BULTIN__`` syntax.

In some case, you may need to create custom types. For this, you just have to
add your new type to the variable ``clg.TYPES``. A type is just a function that
takes the value of the option in parameter and returns what you want. For
example, to add a custom ``Date`` type based on french date format (DD/MM/YYYY) and
returning a ``datetime`` object:

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
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#default>`_

The value produced if the argument is absent from the command line.


choices
~~~~~~~
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#choices>`_

A container of the allowable values for the argument.


action
~~~~~~
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#action>`_

The basic type of action to be taken when this argument is encountered at the
command line.


version
~~~~~~~
When using the ``version`` action, this argument is expected. ``version`` action
allows to print the version information and exits.

The ``argparse`` example look like this:

.. code:: python

    >>> import argparse
    >>> parser = argparse.ArgumentParser(prog='PROG')
    >>> parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    >>> parser.parse_args(['--version'])
    PROG 2.0

And the ``clg`` equivalent (in YAML) is this:

.. code:: python

    options:
        version:
            action: version
            version: "%(prog)s 2.0"

.. note:: Like the ``--help`` option , a default help message is set. But, like
   any other option, you can define the help you want with the **help** keyword.


nargs
~~~~~
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#nargs>`_

The number of command-line arguments that should be consumed.


const
~~~~~
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#const>`_

Value in the resulted **Namespace** if the option is not set in the command-line
(*None* by default).

.. note:: If **nargs** is defined for the option, the default value will be an
   empty list.


metavar
~~~~~~~
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#metavar>`_

A name for the argument in usage messages.


need
~~~~
List of options needed with the current option.


conflict
~~~~~~~~
List of options that must not be used with the current option.


match
~~~~~
Regular expression that the option's value must match.



args
----
This section define arguments of the current command. It is identical as the
`options`_ section at the exception of the **short** and **version** keywords
which are not available.



groups
------
This section is a list of groups. Groups are essentially used for organizing
options and arguments in the help message. Each
`group <https://docs.python.org/dev/library/argparse.html#argument-groups>`_
can have theses keywords:

    * **title** (``argparse``)
    * **description** (``argparse``)
    * **options** (``clg``)
    * **args** (``clg``)
    * **exclusive_groups** (``clg``)

.. note:: All ``argparse`` examples set ``add_help`` to *False*. If this is set,
   ``help`` option is put in *optional arguments*. If you want to put the
   ``help`` option in a group, you need to set the help option
   `manually <configuration.html#add-help>`_.

.. note:: Behaviour of groups have changed. The previous versions (1.*) just
   references previously defined options. Now, this section act like a parser,
   and *options* and *arguments* sections defines options and arguments of the
   group. **This break compatibility with previous versions.**

title
~~~~~
Customize the help with a title.


description
~~~~~~~~~~~
Customize the help with a description.


options
~~~~~~~
Options in the group. This section is identical to the
`options section <configuration.html#options>`_.


args
~~~~
Arguments in the groups. This section is identical to the
`args section <configuration.html#args>`_.


exclusive groups (of a group)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Exclusive groups in the group. This section is identical to the
`exclusive groups section <configuration.html#exclusive-groups>`_.




exclusive groups
----------------
This section is a list of
`exclusive groups <https://docs.python.org/dev/library/argparse.html#mutual-exclusion>`_.
Each group can have theses keywords:

    * **required** (``argparse``)
    * **options** (``clg``)


required
~~~~~~~~
Boolean indicating if at least one of the arguments is required.


options
~~~~~~~
List with the options of the group. This section is identical to the
`options section <configuration.html#options>`_.



subparsers
----------
**argparse link**: `<https://docs.python.org/dev/library/argparse.html#argparse.ArgumentParser.add_subparsers>`_

This allow to add subcommands to the current command.

Keywords:
    * **help** (``argparse``)
    * **title** (``argparse``)
    * **description** (``argparse``)
    * **prog** (``argparse``)
    * **help** (``argparse``)
    * **metavar** (``argparse``)
    * **parsers** (``clg``)
    * **required** (``clg``)

.. note:: It is possible to directly set parsers configurations (the content of
   **parsers** subsection) in this section. The module check for the presence
   of **parsers** section and, if not present, consider this is subcommands
   configurations.

.. note:: When using subparsers and for being able to retrieves configuration of
   the used (sub)command, **dest** argument of ``add_subparsers`` method is used.
   It add in the resulted **Namespace** an entry which key is the value of **dest**
   and the value the used subparser. The key is generated from the **keyword**
   argument (default: *command*) of the **CommandLine** object, incremented at each
   level of the arborescence. For example:

   .. code:: bash

       $ python prog.py list users
       Namespace(command0='list', command1='users')


title
~~~~~
Customize the help with a title.


description
~~~~~~~~~~~
Customize the help with a description.


help
~~~~
Additional help message.


prog
~~~~
Customize usage in help.


help
~~~~
Help for subparser group in help output.


metavar
~~~~~~~
String presenting available sub-commands in help


parsers
~~~~~~~
This is a hash whose keys are the name of subcommands and values the
configuration of the command.


required
~~~~~~~~
Indicate whether a subcommand is required (default: *True*).



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
This is a string indicating the module to load (ex: *package.subpackage.module*).
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
