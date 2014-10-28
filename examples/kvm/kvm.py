#!/usr/bin/env python

import clg
import yaml
import yamlordereddictloader

def main():
    cmd = clg.CommandLine(yaml.load(open('kvm.yml'),
                                    Loader=yamlordereddictloader.Loader))
    cmd.parse()

if __name__ == '__main__':
    main()
