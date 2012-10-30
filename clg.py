#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

class CommandLine(object):
    def __init__(self, config):
        self.config = config
        self.subparsers = {}

        add_help = False \
            if 'main' in self.config and 'help' in self.config['main']['order'] \
            else True
        self.parser = argparse.ArgumentParser(add_help=add_help)

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
            # Main parser
            parser = self.parser
        else:
            if not hasattr(self, 'parsers'):
                self.parsers = self.parser.add_subparsers(dest='subparser')
            options = params['options'] if 'options' in params else {}
            parser = self.parsers.add_parser(
                parser_name,
                add_help=False if 'help' in options else True
            )
            # Memorise subparser.
            self.subparsers.setdefault(parser_name, parser)
        parser._optionals.title = 'Options'
#        parser.usage = self._format_usage(parser_name)

        try:
            for option in params['order']:
                self._add_option(parser, option, params['options'][option])
        except KeyError:
            pass


    def _add_option(self, parser, option, params):
        option_help = params['help'].strip()

        option_str = option.replace('_', '-')
        action = None
        if 'type' in params and params['type'] == 'bool':
            action = 'store_true'
        if option == 'help':
            action = 'help'
        if 'short' in params:
            option = parser.add_argument(
                params['short'], '--%s' % option_str, dest=option, action=action
            )
        else:
            option = parser.add_argument(
                '--%s' % option_str, dest=option, action=action
            )

        if 'type' in params and params['type'] != bool:
            type = params['type']
            if type == 'list':
                option.nargs = '*'
                option.default = []
            else:
                option.type = eval(type)

        if 'default' in params:
            option.default = params['default']
            option_help = option_help.replace(
                '$DEFAULT$',
                str(params['default'])
            )

        if 'choices' in params:
            option.choices = params['choices']
            option_help = option_help.replace(
                '$CHOICES$',
                params['choices'].__str__()[1:-1]
            )

        if 'required' in params:
            option.required = True

        option.help = option_help


    def _error(self, parser, msg):
        print self.cur_parser.format_usage()
        print "%s: error: %s" % (self.cur_parser.prog, msg)
        sys.exit(1)


    def _option_str(self, parser, option):
        option_config = self.config[parser]['options'][option]
        option_str = ['--%s' % option.replace('_', '-')]
        if 'short' in option_config:
            option_str.insert(0, option_config['short'])
        return "'%s'" % '/'.join(option_str)


    def _check(self):
        parser = self.cur_parser_name
        options = self.config[parser]['options']
        parser_config = self.config[parser]
        options = parser_config['options']

        # Check conflicting options.
        if 'groups' in parser_config:
            groups = parser_config['groups']
            for group, config in groups.iteritems():
                group_options = config['options']
                options_str = ', '.join(
                    [self._option_str(parser, option) for option in group_options]
                )
                nb_options = sum(
                    [1 for option in config['options'] if self.args[option] is not None]
                )
                if nb_options > 1:
                    self._error(
                        parser,
                        "conflicting options: %s" % options_str
                    )
                if 'required' in config and config['required'] and nb_options == 0:
                    self._error(
                        parser,
                        "missing one of theses options: %s" % options_str
                    )

        # Check dependances between options.
        for option, config in options.iteritems():
            if not self.args[option]:
                continue
            if 'necessary' not in config:
                continue
            for opt in config['necessary']:
                if not self.args[opt]:
                    self._error(parser, "argument %s: missing dependance %s" % (
                        self._option_str(parser, option),
                        self._option_str(parser, opt)
                    ))

        for option, config in options.iteritems():
            if not self.args[option]:
                continue
            if 'conflicts' not in config:
                continue
            for opt in config['conflicts']:
                if self.args[opt]:
                    self._error(parser, "argument %s: option %s in conflict" % (
                        self._option_str(parser, option),
                        self._option_str(parser, opt)
                    ))


    def parse(self):
        # Get args in dictionnary (not Namespace)
        self.args = self.parser.parse_args().__dict__

        self.cur_parser_name = 'main' \
            if 'subparser' not in self.args or self.args['subparser'] is None \
            else self.args['subparser']
        self.cur_parser = self.parser \
            if self.cur_parser_name == 'main' \
            else self.subparsers[self.cur_parser_name]

        self._check()

        parser_config = self.config[self.cur_parser_name]
        if 'program' in parser_config and parser_config['program'] is not None:
            program_config = parser_config['program']
            if 'execute' in program_config:
                # Execute code defining.
                pass
            elif 'module' in program_config:
                program = program_config['module']
                if 'path' in program:
                    sys.path.append(program['path'])
                exec('import %s as module' % program['lib'])
                exec('module.%s(self.args)' % program['main'])

