#!/usr/bin/env python

import clg
import yaml
import yamlordereddictloader
from os import path

CMD_FILE = path.abspath(path.join(path.dirname(__file__), 'kvm.yml'))

# Add custom command-line types.
from commands.guests.deploy import InterfaceType, DiskType, FormatType
from commands.guests.clone import URIType
clg.TYPES.update({'Interface': InterfaceType,
                  'Disk': DiskType,
                  'Format': FormatType,
                  'URI': URIType})

def main():
    cmd = clg.CommandLine(yaml.load(open('kvm.yml'),
                                    Loader=yamlordereddictloader.Loader))
    cmd.parse()

if __name__ == '__main__':
    main()
