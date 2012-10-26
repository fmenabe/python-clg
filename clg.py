#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

class CommandLine(object):
    def __init__(self, config):
        self.config = config
        self.subparsers = {}

        self.parser = argparse.ArgumentParser()

        for parser, params in self.config.iteritems():
            self._add_parser(parser, params)


    def _format_usage(self, parser_name):
        begin = len("usage : %s %s " % (
            os.path.basename(sys.argv[0]),
            parser_name
        ))
        parser = self.config[parser_name]

        return "%s %s %s" % (sys.argv[0], parser_name, usage)


    def _add_parser(self, parser_name, params):
        if parser_name == 'main':
            parser = self.parser
        else:
            if not hasattr(self, 'parsers'):
                self.parsers = self.parser.add_subparsers(dest='subparsers')
            options = params['options'] if 'options' in params else {}
            parser = self.parsers.add_parser(
                parser_name,
                add_help=False if 'help' in options else True
            )
            self.subparsers.setdefault(parser_name, parser)
        parser._optionals.title = 'Options'
#        parser.usage = self._format_usage(parser_name)

        try:
            for option in params['order']:
                self._add_option(parser, option, params['options'][option])
        except KeyError:
            pass


    def _add_option(self, parser, option, params):
        option_params = [
            "'%s'" % params['short'] if 'short' in params else '',
            "'--%s'" % option.replace('_', '-'),
            "dest='%s'" % option,
            "help=u\"%s\"" % params['help'].strip()
        ]

        if 'default' in params:
            option_params.append("default='%s'" % params['default'])
            option_params[3] = option_params[3].replace(
                '$DEFAULT$',
                str(params['default'])
            )

        if 'type' in params:
            option_params.append({
                'bool': lambda: "action='store_true'",
                'list': lambda: "nargs= '*'"
            }.get(params['type'])())

        # Clean option params.
        while True:
            try:
                option_params.remove('')
            except ValueError:
                break

        eval("parser.add_argument(%s)" % ', '.join(option_params))


    def _check_subparser(self, parser):
        errors = []
        options = self.config[parser]['options']
        for option, params in options.iteritems():
            if 'required' in params and params['required']:
                if getattr(self.args, option) is None:
                    errors.append("option '%s' is required" % option)

        if 'groups' in self.config[parser]:
            group_options = self.config[parser]['groups']
            in_cmd = [
                True if getattr(self.args, option) is not None else False \
                for option in group_options
            ]
            nb_options = in_cmd.count(True)
            if nb_options == 0:
                errors.append("missing groups option")
            elif nb_options > 1:
                errors.append("conflict between groups options")

            for option, dependancies in group_options.iteritems():
#                print self.args
                if getattr(self.args, option) is not None \
                and dependancies is not None:
                    for opt, value in dependancies.iteritems():
                        if value and getattr(self.args, opt) is None:
                            errors.append(
                                "option '%s' is needed by group "
                                "option '%s'" % (opt, option)
                            )

        return errors


    def parse(self):
        errors = []
        self.args = self.parser.parse_args()

#        errors.extend(self._check_subparser('main'))
#        print self.args
        subparser = ''
        program = {}
        for parser, params in self.config.iteritems():
            if self.args.subparsers == parser:
                subparser = parser
                errors.extend(self._check_subparser(parser))
                program = self.config[parser]['program']

        if errors:
#            print subparser, self.subparsers
            parser = self.subparsers[subparser] \
                if subparser != 'main' \
                else self.parser
            parser.print_help()
            print "Errors:\n  * %s" % "\n  * ".join(errors)
            sys.exit(1)

#        exec('import %s as module' % program['lib'])
#        exec('module.%s(self.args.__dict__)' % program['method'])

