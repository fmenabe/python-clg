#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import sys
import yaml
import clg
#from collections import OrderedDict


BASH_SCRIPT = """declare -a choices
declare -a options
declare -a subcommands

parse_command () {{
    choices=(${{options[@]}} ${{subcommands[@]}})
    choices=`echo ${{choices[@]}}`
    for index in `seq $2 $COMP_CWORD`; do
        word=${{COMP_WORDS[$index]}}
        for subcommand in ${{subcommands[@]}}; do
            if [[ $subcommand = $word ]]; then
                index=$((index+1))
                "$1_$subcommand" $index
            fi
        done
        COMPREPLY=($(compgen -W "$choices" -- ${{COMP_WORDS[COMP_CWORD]}}))
    done
}}
{functions}

complete -F _main {prog}
"""

ZSH_SCRIPT = """#compdef ldapuds
local state ret=1
local -a options
typeset -A opt_args

parse_command () {{
    choices=($subcommands{ext} $options{ext})

    for index in {{$2..${{#words}}}}; do
        word=$words[$index]
        for subcommand in $subcommands; do
            if [[ $subcommand = $word ]]; then
                ((index=$index+1))
                "$1_$subcommand" $index
            fi
        done
        {command}
    done
}}
{functions}

_main
return ret
"""

SIMPLE_COMMAND = '_arguments "*: :($choices)" && ret=0'
MENU_COMMAND = "_describe -t desc '$1' choices && ret=0"

CMD="""
anchors: &OPTIONS
    prog:
        short: p
        help: Program name.
        required: True
    conf_file:
        short: c
        help: Configuration file of the command .
        required: True
    format:
        short: f
        help: Format of configuration file.
        choices:
            - yaml
            - json
        required: True
    output_file:
        short: o
        help: Output file
        required: True
    ignore_options:
        short: i
        help: >
            When there are subcommands, don't complete options. With
            simple completion, completion is generate alphabetically but
            ignoring dashes of options which can generate an "ugly""
            result.
        action: store_true

subparsers:
    bash:
        options:
            <<: *OPTIONS
    zsh:
        options:
            <<: *OPTIONS
            simple:
                short: s
                help: >
                    Generate completion without printing the descriptions of
                    options and subcommands.
                action: store_true
"""

def main():
    cmd = clg.CommandLine(yaml.load(CMD, Loader=clg.YAMLOrderedDictLoader))
    global args
    args = cmd.parse()
    global shell
    shell = args.command0

    if args.format == 'yaml':
        config = yaml.load(open(args.conf_file), Loader=clg.YAMLOrderedDictLoader)
    elif args.format == 'json':
        import simplejson as json
        config = json.loads(open('command.json'), object_pairs_hook=OrderedDict)

    functions = '\n'.join(
        parse_config(shell, '_main', config, [], args.ignore_options))
    script = {
        'bash': lambda: BASH_SCRIPT.format(prog=args.prog, functions=functions),
        'zsh': lambda: ZSH_SCRIPT.format(prog=args.prog, functions=functions,
            command=SIMPLE_COMMAND if args.simple else MENU_COMMAND,
            ext='' if args.simple else '_desc')
    }[shell]()

    with open(args.output_file, 'w') as fhandler:
        fhandler.write(script)


def parse_config(shell, name, config, functions=[], ignore_opts=False):
    functions.append('')
    functions.append('%s () {' % name)

    # Get subparsers config.
    subparsers_config = config.get('subparsers', {})
    if 'parsers' in subparsers_config:
        subparsers_config = subparsers_config['parsers']
    subparsers = list(subparsers_config.keys())
    subparsers_desc = [
        '"%s:%s"' % (subparser, subparser_conf.get('description', 'No description.'))
        for subparser, subparser_conf in subparsers_config.items()]

    # Get options and args
    options = ['--%s' % clg.format_optname(opt)
        for opt in config.get('options', {}).keys()]
    options_desc = [
        '"--%s:%s"' % ( clg.format_optname(opt),
            opt_conf.get('help', 'No description'))
        for opt, opt_conf in config.get('options', {}).items()]
    if config.get('add_help', True):
        options.append('--help')
        options_desc.append('"--help:Show this help message and exit."')
    if ignore_opts and subparsers:
        options = []
        options_desc = []
    arguments = list(config.get('args', {}).keys())

    # Generate command function.
    functions.append('    options=(%s)' % ' '.join(options))
    functions.append('    args=(%s)' % ' '.join(
        clg.format_optname(arg) for arg in arguments))
    functions.append('    subcommands=(%s)' % ' '.join(subparsers))
    if shell == 'zsh' and not args.simple:
        functions.append('    options_desc=(%s)' % '\n'.join(options_desc))
        functions.append('    subcommands_desc=(%s)' % '\n'.join(subparsers_desc))

    # Add parse_command execution
    functions.append('    parse_command %s %s' % (name,
        {'bash': 1, 'zsh': 2}[shell] if name == '_main' else '$1'))
    functions.append('}')

    for subparser, config in subparsers_config.items():
        functions = parse_config(
            shell, '%s_%s' % (name, subparser), config, functions, ignore_opts)

    return functions


if __name__ == '__main__':
    main()
