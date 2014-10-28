#!/usr/bin/env python

import clg
import yaml

def main():
    cmd = clg.CommandLine(yaml.load(open('exclusive_groups.yml')))
    print(cmd.parse())

if __name__ == '__main__':
    main()
