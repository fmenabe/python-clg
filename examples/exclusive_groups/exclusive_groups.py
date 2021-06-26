#!/usr/bin/env python

import clg
import os
import yaml

CMD_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'exclusive_groups.yml'))
def main():
    with open(CMD_FILE) as o_f:
        cmd = clg.CommandLine(yaml.load(o_f, Loader=yaml.SafeLoader))
    print(cmd.parse())

if __name__ == '__main__':
    main()
