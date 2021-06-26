#!/usr/bin/env python

import clg
import json
import os
from collections import OrderedDict
#import yaml
#import yamlordereddictloader

CMD_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'simple.json'))
# CMD_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'simple.yml'))

def main():
    cmd_conf = json.load(open(CMD_FILE), object_pairs_hook=OrderedDict)
#    cmd_conf = yaml.load(open('simple.yml'), Loader=yamlordereddictloader.Loader)
    cmd = clg.CommandLine(cmd_conf)
    args = cmd.parse()
    print("Print Namespace object: %s" % args)
    print("Print Namespace attributes: %s" % vars(args))
    print("Iter arguments:")
    for arg, value in args:
        print("  %s: %s" % (arg, value))
    print("Access 'foo' option with attribute syntax: %s" % args.foo)
    print("Access 'foo' option with list syntax: %s" % args['foo'])

if __name__ == '__main__':
    main()
