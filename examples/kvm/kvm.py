#!/usr/bin/env python

import clg

# Add custom command-line types.
from commands.deploy import InterfaceType, DiskType, FormatType
clg.TYPES.update({'Interface': InterfaceType, 'Disk': DiskType, 'Format': FormatType})

if __name__ == '__main__':
    clg.init()
