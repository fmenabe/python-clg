#!/usr/bin/env python

import clg
import requests
import argcomplete
from pprint import pprint

CMD = {
    'options': {
        'org': {
            'required': True,
            'help': 'Github organization'
        },
        'member': {
            'required': True,
            'completer': 'github_org_members',
            'help': 'Github member'
        }
    }
}

def github_org_members(prefix, parsed_args, **kwargs):
    resource = "https://api.github.com/orgs/{org}/members".format(org=parsed_args.org)
    return (member['login']
            for member in requests.get(resource).json()
            if member['login'].startswith(prefix))
clg.COMPLETERS.update(github_org_members=github_org_members)

def main():
    args = clg.init(format='raw', data=CMD, completion=True)
    pprint(requests.get("https://api.github.com/users/{m}".format(m=args.member)).json())

if __name__ == '__main__':
    main()
