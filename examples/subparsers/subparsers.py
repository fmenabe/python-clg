#!/usr/bin/env python

import clg
import yaml

def main():
    args = clg.init(format='yaml', data='subparsers.yml')
    print(args)

if __name__ == '__main__':
    main()
