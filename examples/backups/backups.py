#!/usr/bin/env python

import os
import datetime
import clg
import yaml
import yamlordereddictloader
from pprint import pprint

CMD_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cmd.yml'))

def Date(value):
    try:
        return datetime.strptime(value, '%d/%m/%Y')
    except Exception as err:
        raise clg.argparse.ArgumentTypeError(err)
clg.TYPES['Date'] = Date

def main():
    conf = yaml.load(open(CMD_FILE), Loader=yamlordereddictloader.Loader)
    cmd = clg.CommandLine(conf)
    args = cmd.parse()
    pprint(vars(args))

if __name__ == '__main__':
    main()
