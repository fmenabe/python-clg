# -*- coding : utf-8 -*-

from pprint import pprint
import os
import re
import sys
import imp
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
        'argparse': ['title', 'description', 'options'],
        'clg': ['options']
    },
    'exclusive_group': {
        'argparse': ['required'],
        'clg': ['options']
    },
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
    'execute': {
        'needone': ['module', 'file'],
        'optional': ['function']
    }
}

# Errors messages.
INVALID_SECTION = "this section is not a '%s'"
EMPTY_CONF = 'configuration is empty'
ONE_KEYWORDS = "this section need (only) one theses keywords: '%s'"
UNKNOWN_KEYWORD = "unknown keyword '%s'"
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


def check_conf(clg_path, config, section, comment=''):
    # Check config is not empty.
    if config is None:
        raise CLGError(clg_path, EMPTY_CONF)

    # Check type of the configuration.
    if not isinstance(config, dict):
        raise CLGError(clg_path, INVALID_SECTION % 'dict')

    # Check keywords.
    valid_keywords = [
        keyword for keywords in KEYWORDS[section].values()
        for keyword in keywords]
    for keyword in config:
        if keyword not in valid_keywords:
            raise CLGError(clg_path, UNKNOWN_KEYWORD % keyword)
        if config[keyword] is None:
            raise CLGError(clg_path + [keyword], EMPTY_CONF)


class CommandLine(object):
    def __get_config(self, clg_path, ignore=True):
        config = self.config
        for index, elt in enumerate(clg_path):
            config = (config['parsers'][elt]
                if (not ignore
                  and clg_path[index-1] == 'subparsers' and 'parsers' in config)
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


    def _add_parser(self, clg_path, parser=None):
        # Get configuration elements from clg_path.
        config = self.__get_config(clg_path)
        check_conf(clg_path, config, 'parser')

        # Initialize parent parser.
        if parser is None:
            self.parser = argparse.ArgumentParser(**self._gen_parser(config))
            parser = self.parser

        # It may be needed to access the parser object later (for printing
        # usage by example) so memorize it.
        parser_path = [elt
            for index, elt in enumerate(clg_path)
            if not (clg_path[index-1] == 'subparsers' and elt=='parsers')]
        self.__parsers.setdefault('/'.join(parser_path), parser)

        # Generate custom usage.
        if 'usage' in config:
            parser.usage = format_usage(parser.prog, config['usage'])

        # Add subparsers.
        if 'subparsers' in config:
            self._add_subparsers(parser, clg_path, config['subparsers'])

        # For options, use a deep copy for not altering initial configuration
        # when change must be done in it (when generating groups by example).
        options_config = copy.deepcopy(config.get('options', {}))

        # Add groups.
        for group_type in 'groups', 'exclusive_groups':
            if type(config.get(group_type, [])) is not list:
                raise CLGError(clg_path, INVALID_SECTION % (group_type, 'list'))
            for index, group_config in enumerate(config.get(group_type, [])):
                self._add_group(parser, clg_path,
                    group_config, options_config, group_type, index)

        # Add options.
        for option, option_config in options_config.items():
            self._add_arg(parser, clg_path, option, option_config, True)

        # Add args.
        args_config = config.get('args', {})
        for arg, arg_config in args_config.items():
            self._add_arg(parser, clg_path, arg, arg_config, False)

        # Check 'execute' configuration.
        if 'execute' in config:
            clg_path = clg_path + ['execute']
            check_conf(clg_path, config['execute'], 'execute')

            needed_keywords = KEYWORDS['execute']['needone']
            main_params = [arg in config['execute'] for arg in needed_keywords]
            if main_params.count(True) != 1:
                raise CLGError(
                    clg_path, ONE_KEYWORDS % ("', '".join(needed_keywords)))



    #
    # Subparsers functions.
    #
    def _check_subparsers(self, clg_path, config):
        # Check config is not empty:
        if config is None:
            raise CLGError(clg_path, EMPTY_CONF)

        if 'parsers' in config:
            check_conf(clg_path, config, 'subparser')

            clg_path = clg_path + ['parsers']
            for keyword in KEYWORDS['subparser']['argparse']:
                clg_path = clg_path + [keyword]
                if keyword in config and not isinstance(config[keyword], str):
                    raise CLGError(clg_path, INVALID_SECTION % 'string')

            if not isinstance(config['parsers'], dict):
                raise CLGError(clg_path + ['parsers'], INVALID_SECTION % 'dict')



    def _add_subparsers(self, parser, clg_path, subparsers_config):
        clg_path.append('subparsers')
        self._check_subparsers(clg_path, subparsers_config)

        # Initiliaze subparsers.
        required = True
        subparsers_init = {'dest': '%s%d' % (self.keyword, len(clg_path) / 2)}
        if 'parsers' in subparsers_config:
            clg_path.append('parsers')
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
            subparser_path = list(clg_path)
            subparser_path.append(parser_name)
            check_conf(subparser_path, parser_config, 'parser')
            subparser = subparsers.add_parser(
                parser_name, **self._gen_parser(parser_config))
            self._add_parser(subparser_path, subparser)


    #
    # Groups function.
    #
    def _check_group(self, clg_path, config, options, group_type, index):
        clg_path = clg_path + [group_type, '#%d' % (index + 1)]
        section = 'group' if group_type == 'groups' else 'exclusive_group'

        # Check group configuration (type and keywords).
        check_conf(clg_path, config, section)

        # Check group options.
        if 'options' not in config:
            raise CLGError(clg_path, "'options' keyword is needed")
        if type(config['options']) is not list:
            raise CLGError(clg_path, INVALID_SECTION % 'list')
        if len(config['options']) == 1:
            raise CLGError(clg_path, "need at least two options")
        for option in config['options']:
            if option not in options:
                raise CLGError(clg_path, "unknown option '%s'" % option)


    def _add_group(self,
      parser, clg_path, config, parser_options, group_type, group_number):
        self._check_group(
            clg_path, config, parser_options, group_type, group_number)

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
                group, clg_path, option, parser_options[option], True)
            del(parser_options[option])


    #
    # Options and arguments functions.
    #
    def _check_arg(self, clg_path, config, name, isopt):
        clg_path = clg_path + ['options' if isopt else 'args', name]
        arg_type = "%s" % ('option' if isopt else 'argument')
        check_conf(clg_path, config, arg_type)

        if 'short' in config and len(config['short']) != 1:
            raise CLGError(clg_path + ['short'], "this must be a single letter")

        for keyword in KEYWORDS['option']['post']:
            if keyword not in config:
                continue
            for opt in config[keyword]:
                if opt not in self.__get_config(clg_path[:-1]):
                    raise CLGError(
                        clg_path + [keyword], "unknown option '%s'" % opt)


    def _add_arg(self, parser, clg_path, name, config, isopt):
        self._check_arg(clg_path, config, name, isopt)
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
        clg_path = []
        for arg, value in sorted(args):
            if re.match('^%s[0-9]*$' % self.keyword, arg):
                clg_path.extend([value, 'subparsers'])
        if clg_path:
            clg_path = ['subparsers'] + clg_path[:-1]
        config = self.__get_config(clg_path, ignore=False)
        parser = self.__parsers['/'.join(clg_path)]

        # Post checks.
        for option, option_config in config.get('options', {}).items():
            if not self.__has_value(args[option], option_config):
                if 'nargs' in option_config and option_config['nargs'] in ('*', '+'):
                    args[option] = []
                continue

            for keyword in KEYWORDS['option']['post']:
                if keyword in option_config:
                    if type(option_config[keyword]) is not list:
                        raise CLGError(clg_path + ["options/%s" % option],
                            INVALID_SECTION % ('need', 'list'))
                    self._check_dependency(
                        args, config['options'], option, parser, keyword)


        # Execute.
        if 'execute' in config:
            if 'module' in config['execute']:
                self._exec_module(config['execute'], args, clg_path)
            if 'file' in config['execute']:
                self._exec_file(config['execute'], args, clg_path)

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


    def _exec_file(self, config, args, clg_path):
        mdl_path = os.path.abspath(config['file'])
        mdl_name = os.path.splitext(os.path.basename(mdl_path))[0]
        mdl_func = config.get('function', 'main')

        if not os.path.exists(mdl_path):
            raise CLGError(clg_path + ['file'], "file '%s' not exists" % mdl_path)

        getattr(imp.load_source(mdl_name, mdl_path), mdl_func)(args)


    def _exec_module(self, config, args, clg_path):
        mdl_func = config.get('function', 'main')
        mdl_tree = config['module'].split('.')
        mdl = None

        for mdl_idx, mdl_name in enumerate(mdl_tree):
            try:
                mdl = imp.load_module('.'.join(mdl_tree[:mdl_idx + 1]),
                    *imp.find_module(mdl_name, mdl.__path__ if mdl else None))
            except (ImportError, AttributeError) as err:
                raise CLGError(clg_path + ['module'],
                    "Unable to load module '%s': %s" % (mdl, err))

        getattr(mdl, mdl_func)(args)
