#!/usr/bin/env python

import sys
sys.path.append('../..')
import clg
import yaml
import yamlordereddictloader
from os import path

CMD_FILE = path.abspath(path.join(path.dirname(__file__), 'cmd.yml'))

# Add custom command-line types.
from commands.deploy import InterfaceType, DiskType, FormatType
clg.TYPES.update({'Interface': InterfaceType, 'Disk': DiskType, 'Format': FormatType})

def main():
    cmd = clg.CommandLine(yaml.load(open(CMD_FILE), Loader=yamlordereddictloader.Loader))
    cmd.parse()

if __name__ == '__main__':
    main()
