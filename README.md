Command-line generator in python
================================

This module is a wrapper to **argparse** module. Its goal is to generate a
custom and advanced command-line from a formatted dictionary. The sequence of
subparsers is not limited but it is not possible to have a (sub)parser that have
both subparsers and options. The idea is really to not write dozens or hundreds
of lines of code to generate the command-line but to outsource it to a file in a
"classic" format (YAML, JSON, ...).

Code is available on [Github](http://github.com/fmenabe/python-clg).
Documentation is available on [readthedocs](https://clg.readthedocs.org/en/latest/).
