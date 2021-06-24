#! /usr/bin/env python

import clg
import os
import yaml
import yamlordereddictloader

CMD_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),'subparsers.yml'))
def main():
    cmd = clg.CommandLine(yaml.load(open(CMD_FILE),
                                    Loader=yamlordereddictloader.Loader))
    print(cmd.parse())


if __name__ == '__main__':
    main()
