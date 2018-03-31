#!/usr/bin/env python

import clg

def main():
    args = clg.init(format='yaml', data='exclusive_groups.yml')
    print(args)

if __name__ == '__main__':
    main()
