Command-line generator in python
================================

This module is a wrapper to **argparse** module. Its goal is to generate a
custom and advanced command-line from a formatted dictionary. As python
dictionnaries are easily exportable to a file like YAML or JSON, the idea is to
outsource the command-line definition to a file instead of writing dozens or
hundreds lines of code.

Code is available on Github (http://github.com/fmenabe/python-clg).

Documentation is available on readthedocs (https://clg.readthedocs.org/en/latest/).

Releases notes
--------------
1.0
~~~
  * Rewrite module for matching at best ``argparse``
  * Allow bultins
  * Remove compatibility to python2.6 (because of dict comprehension)

0.5
~~~
  * Port code to Python 3 (with compatiblity at least until Python 2.6)

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
  * Update the license to MIT.

0.2
~~~
  * **CommandLine** object doesn't take anymore a JSON or YAML file but a
    dictionary.
  * Add documentation.
  * Updating setup for PyPi.
