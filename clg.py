# -*- coding: utf-8 -*-

from pprint import pprint
import os.path
import sys
import copy
import argparse
import yaml
import yaml.constructor
from collections import OrderedDict

PARSER_KEYWORDS = (
    'usage', 'subparsers', 'options', 'args', 'groups',
    'exclusive_groups', 'execute'
)
OPTION_KEYWORDS = (
    'help', 'type', 'default', 'required', 'choices',
    'metavar', 'dest', 'short', 'need', 'conflict'
)
POST_KEYWORDS = ('need', 'conflict')

NEED_ERROR = "{prog}: error: argument {arg}: need {arg2} argument"
CONFLICT_ERROR = "{prog}: error: argument {arg}: conflict with {arg2} argument"


class YAMLOrderedDictLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    (http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-
    mappings-as-ordereddicts)
    """
    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(
            u'tag:yaml.org,2002:map', type(self).construct_yaml_map
        )
        self.add_constructor(
            u'tag:yaml.org,2002:omap', type(self).construct_yaml_map
        )


    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)


    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(
                None,
                None,
                'expected a mapping node, but found %s' % node.id,
                node.start_mark
            )

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError(
                    'while constructing a mapping',
                    node.start_mark,
                    'found unacceptable key (%s)' % exc,
                    key_node.start_mark
                )
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


class CLGError(Exception):
    """Exception raised when there are errors."""
    pass


class CommandLine(object):
    """Command line"""
    def __init__(self, config, keyword='command'):
        """Initialize the command from a YAML or a JSON file."""
        self.config = config
        self.keyword = keyword
        self.args = None
        self.parser = None

        self.__add_parser([])


    def __opt_name(self, option):
        """Format option name."""
        return option.replace('_', '-')


    def __opt_display(self, option, option_config):
        """Format option display."""
        return ('-%s/--%s' % (option_config['short'], self.__opt_name(option))
            if 'short' in option_config
            else '--%s' % self.__opt_name(option)
        )


    def __usage(self, program, usage):
        """Format usage."""
        spaces = ''.join([' ' for _ in "usage: "])
        usage_elts = [program]
        usage_elts.extend(
            ["%s  %s" % (spaces, elt) for elt in usage.split('\n')[:-1]]
        )
        return '\n'.join(usage_elts)


    def __get_config(self, path):
        """Get the configuration of a given path."""
        config = self.config
        for elt in path:
            config = config[elt]
        return config


    def __add_option(self, parser, name, config, isarg=False):
        if config is None:
            raise CLGError("option '%s' has no config" % name)

        option_args = []
        option_kwargs = {}

        # Get option or arg args.
        if not isarg:
            if 'short' in config:
                option_args.append(config['short'])
                del(config['short'])
            option_args.append('--%s' % self.__opt_name(name))
            option_kwargs.setdefault('dest', name)
        else:
            option_args.append(name)

        # Manage type of the option.
        if 'type' in config:
            {
                'bool':
                    lambda: option_kwargs.setdefault('action', 'store_true'),
                'list':
                    lambda: option_kwargs.setdefault('nargs', '*'),
                'path':
                    lambda: None
            }.get(
                config['type'],
                lambda: option_kwargs.setdefault('type', eval(config['type']))
            )()
            del(config['type'])

        # Get other parameters.
        for param, value in config.iteritems():
            # Check for invalid parameters.
            if param not in OPTION_KEYWORDS:
                raise CLGError("invalid parameter '%s'" % param)

            # Ignore parameters used in post checks but check configuration.
            if param in POST_KEYWORDS:
                continue

            value = {
                'type': lambda: eval(value),
                'help': lambda: (
                    value.replace('$DEFAULT', str(config['default']))
                        if "$DEFAULT" in str(value)
                        else value
                )
            }.get(param, lambda: value)()
            option_kwargs.setdefault(param, value)

        # Add option with args and parameters.
        parser.add_argument(*option_args, **option_kwargs)


    def __add_groups(self, parser, groups, options, exclusive=False):
        for index, group_config in enumerate(groups):
            group_options = group_config.get('options', '')
            if not group_options:
                raise CLGError('group #%d has no options' % index)

            # Add group or exclusive to parser according to group configuration.
            if exclusive:
                group = parser.add_mutually_exclusive_group(
                    required=group_config.get('required', False)
                )
            else:
                group_kwargs = dict([
                    group_config[param]
                        for param in ('title', 'description')
                        if param in group_config
                ])
                group = parser.add_argument_group(**group_kwargs)

            # Add options.
            for option in group_options:
                try:
                    self.__add_option(group, option, options[option])
                    del(options[option]) # del option from options list.
                except KeyError:
                    raise CLGError(
                        "group #%d as the unknown option '%s'" % (index, option)
                    )


    def __check_parser_conf(self, config_path, config):
        # Check for invalid sections.
        for keyword in config:
            if keyword not in PARSER_KEYWORDS:
                raise CLGError(
                    "/%s: unknown section '%s'" % (
                        '/'.join(config_path), keyword)
                )

        # Check 'subparsers' section is alone.
        if 'subparsers' in config and len(config) > 1:
            raise CLGError(
                "/%s: 'subparsers' section is in conflict with '%s'" % (
                    '/'.join(config_path), keyword
                )
            )


    def __add_parser(self, config_path, parent=None):
        # Get configuration elements from config_path.
        config = self.__get_config(config_path)

        self.__check_parser_conf(config_path, config)

        # Init main parser.
        if parent is None:
            self.parser = argparse.ArgumentParser(add_help=True)
            parent = self.parser
        # We may need to access to the parser object later (for printing usage
        # by example) so save it to __parsers attibute.
        self.__parsers.setdefault('/'.join(config_path), parent)

        # Add subparser.
        if config.get('subparsers'):
            subparsers_config = config.get('subparsers', {})
            subparser_dest = '%s%d' % (self.keyword, len(config_path) / 2)
            subparsers = parent.add_subparsers(dest=subparser_dest)
            for subparser_name, subparser_conf in subparsers_config.iteritems():
                subparser_path = list(config_path)
                subparser_path.extend(['subparsers', subparser_name])
                subparser = subparsers.add_parser(subparser_name, add_help=True)
                subparser.name = subparser_name
                self.__add_parser(subparser_path, subparser)
        else:
            # For options, use a deep copy for not altering initial
            # configuration when change must be done.
            options_config = copy.deepcopy(config.get('options', {}))
            args_config = OrderedDict(config.get('args', {}))

            if 'usage' in config:
                parent.usage = self.__usage(parent.prog, config['usage'])

            try:
                # Add groups.
                for group_type in 'groups', 'exclusive_groups':
                    if config.get(group_type, {}):
                        self.__add_groups(
                            parent, config.get(group_type), options_config,
                            True if group_type == 'exclusive_groups' else False
                        )

                # Add options.
                for option, option_config in options_config.iteritems():
                    self.__add_option(parent, option, option_config)

                # Add args:
                for arg, arg_config in args_config.iteritems():
                    self.__add_option(parent, arg, arg_config, True)
            except CLGError as err:
                raise CLGError('/%s: %s' % ('/'.join(config_path), err))


    def __check_dependency(self, config, option, dependency=False):
        """
        dependency is True = check for needed options
        dependency is False = check for confict options
        """
        parser = config['parser']
        options = config['options']
        keyword = 'need' if dependency else 'conflict'

        for opt in options[option][keyword]:
            if (
              (dependency and not self.args[opt])
              or (not dependency and self.args[opt])
            ):
                parser.print_usage()
                kwargs = {
                    'prog': parser.prog,
                    'arg':  self.__opt_display(option, options[option]),
                    'arg2': self.__opt_display(opt, options[opt])
                }
                print(NEED_ERROR.format(**kwargs)
                    if dependency
                    else CONFLICT_ERROR.format(**kwargs)
                )
                sys.exit(1)


    def __execute(self, exec_config):
        if 'module' in exec_config:
            module_config = exec_config['module']
            exec('import %s as module' % module_config['lib'])
            exec('module.%s(self.args)' % module_config['function'])


    def parse(self):
        # Parse arguments.
        self.args = self.parser.parse_args().__dict__

        # Get subparser configuration.
        path = []
        for arg, value in sorted(self.args.iteritems()):
            if arg.startswith(self.keyword):
                path.extend([value, 'subparsers'])
        if path:
            path = ['subparsers'] + path[:-1]
        config = self.__get_config(path)

        # Post checks.
        for option, option_config in config['options'].iteritems():
            if self.args[option] is None:
                continue

            for keyword in POST_KEYWORDS:
                if keyword in option_config:
                    {
                        'need': lambda:
                            self.__check_dependency(config, option, True),
                        'conflict': lambda:
                            self.__check_dependency(config, option, False)
                    }.get(keyword)()

            if 'type' in option_config and option_config['type'] == 'path':
                self.args[option] = os.path.abspath(
                    self.args[option].replace(
                        '__FILE__', os.path.dirname(self.conf_file)
                    )
                )

        # Execute.
        if 'execute' in config:
            self.__execute(config['execute'])

