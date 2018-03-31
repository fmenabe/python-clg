**********************
Installation and usage
**********************

Getting started
===============

In order to simplify the usage, an ``init`` function is provided that take care of
importing the necessary modules based on the format of your configuration file and
initializing the command-line.

If no parameters are given to this function, the YAML file *cmd.yml* in the directory of
your main python program is used (the order of keys is kept using `yamlordereddictloader
<https://pypi.python.org/pypi/yamlordereddictloader>`_ module).

Therefore, to start, you just need to:

    1. install ``clg``, ``pyyaml`` and ``yamlordereddictloader`` modules,
    2. create the configuration file of the command-line *cmd.yml*,
    3. create the main program (*myprog.py* file for example).

.. note:: ``pyyaml`` and ``yamlordereddictloader`` modules are only needed if you use YAML
   files (which is the default).

Modules installation
--------------------

As there are no packages for operating systems, the installation will be done in a
virtual environment (there is a lot of literature on the web about why and how to use
them):

.. code::

    $ virtualenv --prompt '(myprog)' env/
    $ . ./env/bin/activate
    (myprog)$ pip install clg pyyaml yamlordereddictloader

Command-line configuration
--------------------------

In this example, we are just going to create a command-line with two options *foo*
and *bar*. *foo* is taking a value while *bar* is not taking any.

As mentioned previously, the command-line configuration is defined in the *cmd.yml* file:

.. code-block:: yaml
    :caption: ./cmd.yml

    help: CLG example.
    description: CLG example.
    options:
      foo:
        help: Foo option.
      bar:
        action: store_true
        help: Bar option.

Main python file
----------------

The main program is simple, you only need to import the ``clg`` module and use its
`init` method that parses the command-line and returns the arguments in a `Namespace`.

.. note:: The returned `Namespace` inherit from `argparse Namespace
    <https://docs.python.org/dev/library/argparse.html#argparse.Namespace>`_
    with additionals methods to make it iterable and accessing arguments
    with both attribute (``args.argument``) and dictionnary (``args['argument']``)
    syntax.

In this example, we just going to print the resulted `Namespace`:

.. code-block:: python
    :caption: ./myprog.py

    #!/usr/bin/env python
    # coding: utf-8

    import clg

    if __name__ == '__main__':
        args = clg.init()
        print(args)

Execution
---------

.. code::

    (myprog)$ python myprog.py --help
    usage: myprog.py [-h] [--foo FOO] [--bar]

    CLG example.

    optional arguments:
      -h, --help  show this help message and exit
      --foo FOO   Foo option.
      --bar       Bar option.

    (myprog)$ python myprog.py --foo oof --bar
    Namespace(bar=True, foo='oof')

This is all you need to start creating command-lines. You can now look at `configuration
parameters <configuration.html>`_ and `examples <examples.html>`_ or continue reading
for a better understanding of the ``init`` function.


Going further
=============

So, by default, a YAML file named *cmd.yml* is used but you may want to use another
configuration file and/or format like JSON or activate completion. The ``init`` method has
a few parameters that manage the source of the configuration, integration with
`argcomplete <http://argcomplete.readthedocs.io/en/latest/>`_ for completion or some
internals details:

    * `format` (default: *yaml*): Define the format of the configuration, it can either
      be *yaml*, *json* or *raw*.
    * `data` (default: ``os.path.join(sys.path[0], 'cmd.yml')``): For *yaml* and *json*
      formats this is the filepath of the configuration file while *raw* format expects a
      dictionary containing the configuration.

.. note:: ``os.path.join(sys.path[0], 'cmd.yml')`` is necessary for using the file
   **in** the program directory wherever we launch the program. Using a relative path is
   not a problem in a development environment but for system integration you should use
   this trick, allowing to install all files at a place (and updating $PATH for executing
   the program from everywhere), or an absolute path.

|

    * `completion` (default: *False*): Activate Bash/Zsh completion using ``argcomplete``.
    * `subcommands_keyword` (default: *command*): For being able internally to retrieve
      the configuration of subcommands, we need to know the chain of commands used. For
      that, the `dest` parameter of ``argparse.ArgumentParser.add_subparsers`` method is
      used. It adds in the resulted `Namespace` an entry which key is the value of `dest`
      and the value the command used. `dest` value is generated from this parameter,
      incremented at each level of the arborescence:

        |   ``$ python prog.py list users``
        |   ``Namespace(command0='list', command1='users')``

    * `deepcopy` (default: *True*): When using YAML anchors, parts of configuration are
      just references to other parts. As internally the module manipulate and delete part
      of the configuration that have been parsed, the result is the loss of informations
      when using anchors. This parameter allows to replace YAML references by a copy
      of data and thus preventing loss of informations.

Using a JSON file
-----------------

Python has a core module for loading JSON files, so there is no need to install
dependencies. As for YAML files, keys order is kept when loading the JSON file.

The previous example, but using a JSON configuration file named *cmd_conf.json* in the
program directory looks like:

.. code-block:: json
    :caption: ./cmd_conf.json

    {
      "help": "CLG example.",
      "description": "CLG example.",
      "options": {
        "foo": {
          "help": "Foo option."
        },
        "bar": {
          "action": "store_true",
          "help": "Bar option."
        }
      }
    }

.. code-block:: python
    :caption: ./myprog.py

    #!/usr/bin/env python
    # coding: utf-8

    import os
    import sys
    import clg

    if __name__ == '__main__':
        conf_path = os.path.join(sys.path[0], 'cmd_conf.json')
        args = clg.init(format='json', data=conf_path)
        print(args)


No configuration file
---------------------
For not being dependent of a configuration file (which may need to be packaged and
deployed at the right place), you can define the configuration directly in the python
program. I often still use YAML but you could also remove modules dependencies by just
using a dictionary to define the configuration:

.. code-block:: python
    :caption: ./myprog.py

    #!/usr/bin/env python
    # coding: utf-8

    import clg
    import yaml
    import yamlordereddictloader

    CMD_CONFIG = """
    help: CLG example.
    description: CLG example.
    options:
      foo:
        help: Foo option.
      bar:
        action: store_true
        help: Bar option.
    """

    if __name__ == '__main__':
        cmd_conf = yaml.load(CMD_CONFIG, Loader=yamlordereddictloader.Loader)
        args = clg.init(format='raw', data=cmd_conf)
        print(args)

Using completion
----------------
Completion is managed using the awesome `argcomplete
<http://argcomplete.readthedocs.io/en/latest/>`_ project so you first need to install this
module in your virtual environment:

.. code::

    (myprog)$ pip install argcomplete

Then, you need to register the command:

.. code::

    (myprog)$ chmod u+x myprog.py
    (myprog)$ eval "$(./env/bin/register-python-argcomplete ./myprog.py)"

Finally, update your python program for activating completion:

.. code::

    if __name__ == '__main__':
        args = clg.init(..., completion=True)

Now the usage of ``./myprog.py`` should have completion:

.. code::

    (myprog)$ ./myprog.py -<TAB>
    --bar   --foo   -h      --help

.. note:: The registering part can be put in your shell rc file so you don't have to do it
    each time. As this is done in a virtualenv, the binary in the virtualenv is used for
    registering which is not pratical. I personally also install argcomplete at the system
    level so I don't have to use the virtualenv program and instead put this in my
    *bashrc* file:

    .. code::

      eval "$(register-python-argcomplete ./myprog.py)"

If needed, you can define `custom argcomplete completers <configuration.html#completer>`_.


Going back a bit
================
The ``init`` function facilitate the usage by managing imports, loading the configuration
file and managing completion. But it was not its primary goal and was needed for allowing
the creation of `plugins <plugins.html>`_ as some data, like the command-line
configuration, are dynamically set at the module level when the function is used (ie: once
initialized, ``clg.config`` returns the command-line configuration for example).

You can of course still initialize the `CommandLine` object manually (using a YAML
configuration file and completion):

.. code-block:: python
    :caption: ./myprog.py

    #!/usr/bin/env python
    # coding: utf-8

    import clg
    import yaml
    import yamlordereddictloader
    import argcomplete

    def main():
        with open('cmd.yml') as fhandler:
            cmd_conf = yaml.load(
                fhandler,
                Loader=yamlordereddictloader.Loader
            )
        cmd = clg.CommandLine(cmd_conf)
        argcomplete.autocomplete(cmd.parser)
        args = cmd.parse()
        print(args)

    if __name__ == '__main__':
        main()
