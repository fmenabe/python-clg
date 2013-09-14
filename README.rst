Command-line generator in python
================================

This module is a wrapper to **argparse** module. Its goal is to generate a
custom and advanced command-line from a formatted dictionary. The sequence of
subparsers is not limited but it is not possible to have a (sub)parser that have
both subparsers and options. The idea is really to not write dozens or hundreds
of lines of code to generate the command-line but to outsource it to a file in a
"classic" format (YAML, JSON, ...).

Code is available on Github (http://github.com/fmenabe/python-clg).

Documentation is available on readthedocs (https://clg.readthedocs.org/en/latest/).

Releases notes
--------------
0.4
~~~
  * Add description of parser (via *desc* keyword).

0.3
~~~
  * Add an iterable and accessible namespace for arguments.
  * Change behaviour of *parse* method (now return a namespace with arguments).
  * Set default value for *list* type to empty list.
  * Change behaviour of the execution of an external module. It is no longer a
    python path of a module in 'sys.path' but directly the path of a file.
    In addition, keyword 'lib' has be replaced by 'path'.
  * Replace '__FILE__' in default value of an option by the directory of the
    program.
  * Update the licence to MIT.

0.2
~~~
  * **CommandLine** object doesn't take anymore a JSON or YAML file but a
    dictionary.
  * Add documentation.
  * Updating setup for PyPi.
