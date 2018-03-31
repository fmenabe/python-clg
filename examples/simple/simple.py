#!/usr/bin/env python

import clg

def main():
    args = clg.init(format='json', data='simple.json')
    #args = clg.init(data='simple.yml')

    print("Print Namespace object: %s" % args)
    print("Print Namespace attributes: %s" % vars(args))
    print("Iter arguments:")
    for arg, value in args:
        print("  %s: %s" % (arg, value))
    print("Access 'foo' option with attribute syntax: %s" % args.foo)
    print("Access 'foo' option with list syntax: %s" % args['foo'])

if __name__ == '__main__':
    main()
