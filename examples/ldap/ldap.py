#!/usr/bin/env python

import os
import clg
import yaml
import yamlordereddictloader
from pprint import pprint

CMD_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cmd.yml'))

def main():
    cmd = clg.CommandLine(yaml.load(open('cmd.yml'), Loader=yamlordereddictloader.Loader))
    args = cmd.parse()
    pprint(vars(args))

if __name__ == '__main__':
    main()
