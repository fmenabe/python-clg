#!/usr/bin/env python

import clg
import yaml
import yamlordereddictloader
from pprint import pprint

def Date(value):
    try:
        return datetime.strptime(value, '%d/%m/%Y')
    except Exception as err:
        raise clg.argparse.ArgumentTypeError(err)
clg.TYPES['Date'] = Date

def main():
    conf = yaml.load(open('cmd.yml'), Loader=yamlordereddictloader.Loader)
    cmd = clg.CommandLine(conf)
    args = cmd.parse()
    pprint(vars(args))

if __name__ == '__main__':
    main()
