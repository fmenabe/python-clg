#!/usr/bin/env python
# coding: utf-8

import clg
import yaml

def main():
    args = clg.init(format='yaml', data='builtins.yml')
    print(args.sum(args.integers))

if __name__ == '__main__':
    main()
