# -*- coding : utf-8 -*-

from pprint import pprint
import os
import re
import sys
import yaml
import copy
import argparse
from collections import OrderedDict

# Keywords (argparse and clg).
KEYWORDS = {
    'parser': {
        'argparse': ['prog', 'usage', 'description', 'epilog',
                    'formatter_class', 'argument_default', 'conflict_handler',
                    'add_help'],
        'clg': ['anchors', 'subparsers', 'options', 'args', 'groups',
                'exclusive_groups', 'execute']
    },
    'subparser': {
        'argparse': ['title', 'description', 'prog', 'help', 'metavar'],
        'clg': ['required', 'parsers']
    },
    'group': {
        'argparse': ['title', 'description', 'options'], 'clg': ['options']},
    'exclusive_group': {'argparse': ['required'], 'clg': ['options']},
    'option': {
        'argparse': ['action', 'nargs', 'const', 'default', 'choices',
                    'required', 'help', 'metavar', 'type'],
        'clg': ['short'],
        'post': ['need', 'conflict']
    },
    'argument': {
        'argparse': ['action', 'nargs', 'const', 'default', 'choices',
                    'required', 'help', 'metavar', 'type'],
        'clg': ['short']
    },
}

# Errors messages.
INVALID_SECTION = '(%s) this section is not a %s'
EMPTY_CONF = 'configuration is empty'
UNKNOWN_KEYWORD = "(%s) unknown keyword '%s'"
NEED_ERROR = '%s: error: argument %s: need %s argument'
CONFLICT_ERROR = '%s: error: argument %s: conflict with %s argument'


class YAMLOrderedDictLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    (http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-
    mappings-as-ordereddicts)
    """
    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)
        self.add_constructor(
            'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(
            'tag:yaml.org,2002:omap', type(self).construct_yaml_map)


    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)


    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructError(None, None,
                'expected a mapping node, but found %s' % node.id,
                node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as err:
                raise yaml.constructor.ConstructError(
                    'while constructing a mapping', node.start_mark,
                    'found unacceptable key (%s)' % err, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


class CLGError(Exception):
    def __init__(self, path, msg):
        self.path = path
        self.msg = msg


    def __str__(self):
        return "/%s: %s" % ('/'.join(self.path), self.msg)


class Namespace(argparse.Namespace):
    def __init__(self, args):
        argparse.Namespace.__init__(self)
        self.__dict__.update(args)


    def __getitem__(self, key):
        return self.__dict__[key]


    def __setitem__(self, key, value):
        if key not in self.__dict__:
            raise KeyError(key)
        self.__dict__[key] = value


    def __iter__(self):
        return ((key, value) for key, value in self.__dict__.items())


def format_usage(prog, usage):
    """Format usage."""
    spaces = ''.join([' ' for _ in "usage: "])
    usage_elts = [prog]
    usage_elts.extend(
        ["%s  %s" % (spaces, elt) for elt in usage.split('\n')[:-1]])
    return '\n'.join(usage_elts)


def format_optname(value):
    return value.replace('_', '-').replace(' ', '-')


def format_optdisplay(value, config):
    return ('-%s/--%s' % (config['short'], format_optname(value))
        if 'short' in config else '--%s' % format_optname(value))


def _check_conf(path, config, section, comment=''):
        section_str = ' '.join((section, comment)).strip()
        if not isinstance(config, dict):
            raise CLGError(path, INVALID_SECTION % (section_str, 'dict'))
        valid_keywords = [keyword
            for keywords in KEYWORDS[section].values() for keyword in keywords]
        for keyword in config:
            if keyword not in valid_keywords:
                raise CLGError(path, UNKNOWN_KEYWORD % (section_str, keyword))
            if config[keyword] is None:
                raise CLGError(path + [keyword], EMPTY_CONF)


class CommandLine(object):
    def __get_config(self, path, ignore=True):
        config = self.config
        for index, elt in enumerate(path):
            config = (config['parsers'][elt]
                if (not ignore
                    and path[index-1] == 'subparsers' and 'parsers' in config)
                else config[elt])
        return config


    def __init__(self, config, keyword='command'):
        """Initialize the command from **config** which a dictionnary
        (preferably an OrderedDict). **keyword** is the name use for knowing the
        path of subcommands (ie: 'command0', 'command1', ... in the namespace of
        arguments)."""
        self.config = config
        self.keyword = keyword
        self.__parsers = {}
        self.parser = None
        self._add_parser([])


    #
    # Parser functions.
    #
    def _gen_parser(self, parser_config):
        return {
            'prog':             parser_config.get('prog', None),
            'usage':            None,
            'description':      parser_config.get('description', None),
            'epilog':           parser_config.get('epilog', None),
            'formatter_class':  getattr(argparse,
                parser_config.get('formatter_class', 'HelpFormatter')),
            'argument_default': parser_config.get('argument_default', None),
            'conflict_handler': parser_config.get('conflict_handler', 'error'),
            'add_help':         parser_config.get('add_help', True)}


    def _check_parser(self, path, config):
        if config is None:
            raise CLGError(path, EMPTY_CONF)
        _check_conf(path, config, 'parser')


    def _add_parser(self, config_path, parser=None):
        # Get configuration elements from config_path.
        config = self.__get_config(config_path)
        self._check_parser(config_path, config)

        # Initialize parent parser.
        if parser is None:
            self.parser = argparse.ArgumentParser(**self._gen_parser(config))
            parser = self.parser
        # It may be needed to access to the parser object later (for printing
        # usage by exemple) so memorize it.
        self.__parsers.setdefault(
            '/'.join([elt
                for index, elt in enumerate(config_path)
                if not (config_path[index-1] == 'subparsers' and elt=='parsers')]),
            parser)

        # Generate custom usage.
        if 'usage' in config:
            parser.usage = format_usage(parser.prog, config['usage'])

        # Add subparsers.
        if 'subparsers' in config:
            self._add_subparsers(parser, config_path, config['subparsers'])

        # For options, use a deep copy for not altering initial configuration
        # when change must be done in it (when generating groups by example).
        options_config = copy.deepcopy(config.get('options', {}))

        # Add groups.
        for group_type in 'groups', 'exclusive_groups':
            if type(config.get(group_type, [])) is not list:
                raise CLGError(config_path, INVALID_SECTION % (group_type, 'list'))
            for index, group_config in enumerate(config.get(group_type, [])):
                self._add_group(parser, config_path,
                    group_config, options_config, group_type, index)

        # Add options.
        for option, option_config in options_config.items():
            self._add_arg(parser, config_path, option, option_config, True)

        # Add args.
        args_config = config.get('args', {})
        for arg, arg_config in args_config.items():
            self._add_arg(parser, config_path, arg, arg_config, False)


    #
    # Subparsers functions.
    #
    def _check_subparsers(self, path, config):
        if 'parsers' in config:
            _check_conf(path, config, 'subparser')

            for keyword in KEYWORDS['subparser']['argparse']:
                if keyword in config and not isinstance(config[keyword], str):
                    raise CLGError(
                        path, INVALID_SECTION % ('subparsers', 'string'))

            if 'parsers' in config and not isinstance(config['parsers'], dict):
                raise CLGError(path + ['parsers'],
                    INVALID_SECTION % ('subparsers', 'dict'))



    def _add_subparsers(self, parser, config_path, subparsers_config):
        config_path.append('subparsers')
        self._check_subparsers(config_path, subparsers_config)

        # Initiliaze subparsers.
        required = True
        subparsers_init = {'dest': '%s%d' % (self.keyword, len(config_path) / 2)}
        if 'parsers' in subparsers_config:
            config_path.append('parsers')
            for keyword in KEYWORDS['subparser']['argparse']:
                if keyword not in subparsers_config:
                    continue
                subparsers_init.setdefault(keyword, subparsers_config[keyword])
            required = subparsers_config.get('required', True)
            subparsers_config = subparsers_config['parsers']
        subparsers = parser.add_subparsers(**subparsers_init)
        subparsers.required = required

        # Add parsers.
        for parser_name, parser_config in subparsers_config.items():
            subparser_path = list(config_path)
            subparser_path.append(parser_name)
            self._check_parser(subparser_path, parser_config)
            subparser = subparsers.add_parser(
                parser_name, **self._gen_parser(parser_config))
            self._add_parser(subparser_path, subparser)


    #
    # Groups function.
    #
    def _check_group(self, path, config, options, group_type, index):
        path = path + [group_type]
        section = ('%s' % (
            'group' if group_type == 'groups' else 'exclusive_group'))

        if config is None:
            raise CLGError(path, "(%s) %s" % (section, EMPTY_CONF))

        _check_conf(path, config, section, '#%d' % (index+1))

        if 'options' not in config:
            raise CLGError(path, "(%s) 'options' keyword is needed" % section)
        if type(config['options']) is not list:
            raise CLGError(path, "(%s) 'options' must be a list" % section)
        if len(config['options']) == 1:
            raise CLGError(path, "(%s) need at least two options" % section)
        for option in config['options']:
            if option not in options:
                raise CLGError(path,
                    "(%s) unknown option '%s'" % (section, option))


    def _add_group(self,
      parser, config_path, config, parser_options, group_type, group_number):
        self._check_group(
            config_path, config, parser_options, group_type, group_number)

        # Add group or exclusive group to parser.
        group = {
            'exclusive_groups': lambda: parser.add_mutually_exclusive_group(
                required=config.get('required', False)),
            'groups': lambda: parser.add_argument_group(
                **{keyword: value for keyword, value in config.items()
                    if keyword in ('title', 'description')})
        }[group_type]()

        # Add options to the group.
        for option in config['options']:
            self._add_arg(
                group, config_path, option, parser_options[option], True)
            del(parser_options[option])


    #
    # Options and args functions.
    #
    def _check_arg(self, path, config, name, isopt):
        path = path + ['options' if isopt else 'args', name]
        arg_type = "%s" % ('option' if isopt else 'argument')
        _check_conf(path, config, arg_type)

        if 'short' in config and len(config['short']) != 1:
            raise CLGError(path,
                "(%s) short parameter must be a single letter" % arg_type)

        if not isopt:
            return

        for keyword in KEYWORDS['option']['post']:
            if keyword not in config:
                continue
            for opt in config[keyword]:
                if opt not in self.__get_config(path[:-1]):
                    raise CLGError(path, "(%s) unknown option '%s'" % (keyword, opt))


    def _add_arg(self, parser, config_path, name, config, isopt):
        self._check_arg(config_path, config, name, isopt)
        option_args = []
        option_kwargs = {}

        if isopt:
            if 'short' in config:
                option_args.append('-%s' % config['short'])
                del(config['short'])
            option_args.append('--%s' % format_optname(name))
            option_kwargs.setdefault('dest', name)
        else:
            option_args.append(name)

        for param, value in sorted(config.items()):
            if isopt and param in KEYWORDS['option']['post']:
                continue

            option_kwargs.setdefault(param, {
                'type': lambda: eval(value),
                'help': lambda: value.replace(
                    '__DEFAULT__', str(option_kwargs.get('default', '?')))
            }.get(param, lambda: self._set_builtin(value))())

        parser.add_argument(*option_args, **option_kwargs)


    def _set_builtin(self, value):
        try:
            return eval(re.search('^__([A-Z]*)__$', value).group(1).lower())
        except (AttributeError, TypeError):
            return (value.replace('__FILE__', sys.path[0])
                if type(value) is str else value)


    #
    # Parsing functions.
    #
    def __has_value(self, optvalue, optconf):
        if optvalue is None or (isinstance(optvalue, list) and not optvalue):
            return False
        if 'action' in optconf:
            action = optconf['action']
            if ((action == 'store_true' and not optvalue)
              or (action == 'store_false' and optvalue)):
                return False
        return True


    def parse(self, args=None):
        # Parse arguments:
        args = Namespace(self.parser.parse_args(args).__dict__)

        # Get subparser configuration.
        path = []
        for arg, value in sorted(args):
            if re.match('^%s[0-9]*$' % self.keyword, arg):
                path.extend([value, 'subparsers'])
        if path:
            path = ['subparsers'] + path[:-1]
        config = self.__get_config(path, ignore=False)
        parser = self.__parsers['/'.join(path)]

        # Post checks.
        for option, option_config in config['options'].items():
            if not self.__has_value(args[option], option_config):
                if 'nargs' in option_config and option_config['nargs'] in ('*', '+'):
                    args[option] = []
                continue

            for keyword in KEYWORDS['option']['post']:
                if keyword in option_config:
                    if type(option_config[keyword]) is not list:
                        raise CLGError(path + ["options/%s" % option],
                            INVALID_SECTION % ('need', 'list'))
                    self._check_dependency(
                        args, config['options'], option, parser, keyword)

        # Execute.
        if 'execute' in config:
            self._execute(config['execute'], args)

        return args


    def _check_dependency(self, args, options, option, parser, keyword):
        for optname in options[option][keyword]:
            has_value = self.__has_value(args[optname], options[optname])
            if (keyword == 'need' and not has_value
              or keyword == 'conflict' and has_value):
                parser.print_usage()
                values = (parser.prog,
                    format_optdisplay(option, options[option]),
                    format_optdisplay(optname, options[optname]))
                print(
                    (NEED_ERROR if keyword == 'need' else CONFLICT_ERROR) % values)
                sys.exit(1)


    def _execute(self, exec_config, args):
        if 'module' in exec_config:
            import imp
            module_path = exec_config['module']['path']
            search_params = ([os.path.splitext(module_path)[0]]
                if not os.path.isabs(module_path)
                else [
                    os.path.splitext(os.path.basename(module_path))[0],
                    [os.path.dirname(module_path)]])

            module_params = imp.find_module(*search_params)
            module = imp.load_module(
                os.path.splitext(module_path)[0], *module_params)
            getattr(module, exec_config['module'].get('function', 'main'))(args)
