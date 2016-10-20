#!/usr/bin/env python

import sys
sys.path.append('../..')
import clg
import requests
import argparse
import argcomplete
from pprint import pprint

CMD = {'options':
    {
        'organization': {'help': 'Github organization'},
        'member': {
            'help': 'Github member',
            'completer': 'github_org_members'
        }
    }
}

def github_org_members(prefix, parsed_args, **kwargs):
    resource = "https://api.github.com/orgs/{org}/members".format(org=parsed_args.organization)
    return (member['login'] for member in requests.get(resource).json() if member['login'].startswith(prefix))
clg.COMPLETERS.update(github_org_members=github_org_members)

cmd = clg.CommandLine(CMD)
argcomplete.autocomplete(cmd.parser)
args = cmd.parse()

pprint(requests.get("https://api.github.com/users/{m}".format(m=args.member)).json())
