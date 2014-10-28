#! /usr/bin/env python

import clg
import yaml
import yamlordereddictloader

def main():
    cmd = clg.CommandLine(yaml.load(open('subparsers.yml'),
                                    Loader=yamlordereddictloader.Loader))
    print(cmd.parse())


if __name__ == '__main__':
    main()
