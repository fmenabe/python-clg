# -*- coding: utf-8 -*-

"""This module is a wrapper to ``argparse`` module. It allow to generate a
command-line from a predefined directory (ie: a YAML, JSON, ... file)."""

import os
import re
import sys
import imp
import argparse
from six import iteritems
from collections import OrderedDict

#
# Constants.
#
# Get types.
BUILTINS = sys.modules['builtins'
                       if sys.version_info.major == 3
                       else '__builtin__']
TYPES = {builtin: getattr(BUILTINS, builtin) for builtin in vars(BUILTINS)}
TYPES['suppress'] = argparse.SUPPRESS
# Get current module.
SELF = sys.modules[__name__]

# Keywords (argparse and clg).
KEYWORDS = {
    'parsers': {'argparse': ['prog', 'usage', 'description', 'epilog', 'help',
                             'add_help', 'formatter_class', 'argument_default',
                             'conflict_handler', 'allow_abbrev'],
                'clg': ['anchors', 'subparsers', 'options', 'args', 'groups',
                        'exclusive_groups', 'execute']},
    'subparsers': {'argparse': ['title', 'description', 'prog', 'help',
                                'metavar'],
                   'clg': ['required', 'parsers']},
    'groups': {'argparse': ['title', 'description'],
               'clg': ['options', 'args', 'exclusive_groups']},
    'exclusive_groups': {'argparse': ['required'],
                         'clg': ['options']},
    'options': {'argparse': ['action', 'nargs', 'const', 'default', 'choices',
                             'required', 'help', 'metavar', 'type', 'version'],
                'clg': ['short'],
                'post': ['match', 'need', 'conflict']},
    'args': {'argparse': ['action', 'nargs', 'const', 'default', 'choices',
                          'required', 'help', 'metavar', 'type'],
             'clg': ['short'],
             'post': ['match', 'need', 'conflict']},
    'execute': {'clg': ['module', 'file', 'function']}}

# Help command description.
HELP_PARSER = OrderedDict(
    {'help': {'help': "Print commands' tree with theirs descriptions.",
              'description': "Print commands' tree with theirs descriptions."}})

# Errors messages.
INVALID_SECTION = "this section is not of type '{type}'"
EMPTY_CONF = 'configuration is empty'
INVALID_KEYWORD = "invalid keyword '{keyword}'"
ONE_KEYWORDS = "this section need (only) one of theses keywords: '{keywords}'"
MISSING_KEYWORD = "keyword '{keyword}' is missing"
UNKNOWN_ARG = "unknown {type} '{arg}'"
SHORT_ERR = 'this must be a single letter'
NEED_ERR = "{type} '{arg}' need {need_type} '{need_arg}'"
CONFLICT_ERR = "{type} '{arg}' conflict with {conflict_type} '{conflict_arg}'"
MATCH_ERR = "value '{val}' of {type} '{arg}' does not match pattern '{pattern}'"
FILE_ERR = "Unable to load file: {err}"
LOAD_ERR = "Unable to load module: {err}"


#
# Exceptions.
#
class CLGError(Exception):
    """CLG exception."""
    def __init__(self, path, msg):
        Exception.__init__(self, msg)
        self.path = path
        self.msg = msg

    def __str__(self):
        return "/%s: %s" % ('/'.join(self.path), self.msg)


#
# Utils functions.
#
def _gen_parser(parser_conf, subparser=False):
    """Retrieve arguments pass to **argparse.ArgumentParser** from
    **parser_conf**. A subparser can take an extra 'help' keyword."""
    conf = {
        'prog':             parser_conf.get('prog', None),
        'usage':            None,
        'description':      parser_conf.get('description', None),
        'epilog':           parser_conf.get('epilog', None),
        'formatter_class':  getattr(argparse, parser_conf.get('formatter_class',
                                                              'HelpFormatter')),
        'argument_default': parser_conf.get('argument_default', None),
        'conflict_handler': parser_conf.get('conflict_handler', 'error'),
        'add_help':         parser_conf.get('add_help', True)}

    if subparser and 'help' in parser_conf:
        conf['help'] = parser_conf['help']
    return conf


def _get_args(parser_conf):
    """Get options and arguments from a parser configuration."""
    args = OrderedDict()
    for arg_type in ('options', 'args'):
        for arg, arg_conf in iteritems(parser_conf.get(arg_type, {})):
            args[arg] = (arg_type, OrderedDict(arg_conf))
    for grp_type in ('groups', 'exclusive_groups'):
        for group in parser_conf.get(grp_type, {}):
            args.update(_get_args(group))
    return args


def _set_builtin(value):
    """Replace configuration values which begin and end by ``__`` by the
    respective builtin function."""
    try:
        return TYPES[re.search('^__([A-Z]*)__$', value).group(1).lower()]
    except (AttributeError, TypeError):
        return (value.replace('__FILE__', sys.path[0])
                if type(value) is str
                else value)


#
# Formatting functions.
#
def _format_usage(prog, usage):
    """Format usage."""
    spaces = re.sub('.', ' ', 'usage: ')
    usage_elts = [prog]
    usage_elts.extend(['%s %s' % (spaces, elt)
                       for elt in usage.split('\n')[:-1]])
    return '\n'.join(usage_elts)


def _format_optname(value):
    """Format the name of an option in the configuration file to a more
    readable option in the command-line."""
    return value.replace('_', '-').replace(' ', '-')


def _format_optdisplay(value, conf):
    """Format the display of an option in error message (short and long option
    with dash(es) separated by a slash."""
    return ('-%s/--%s' % (conf['short'], _format_optname(value))
            if 'short' in conf
            else '--%s' % _format_optname(value))


#
# Check functions.
#
def _check_empty(path, conf):
    """Check **conf** is not ``None`` or an empty iterable."""
    if conf is None or (hasattr(conf, '__iter__') and not len(conf)):
        raise CLGError(path, EMPTY_CONF)


def _check_type(path, conf, conf_type=dict):
    """Check the **conf** is of **conf_type** type and raise an error if not."""
    if not isinstance(conf, conf_type):
        type_str = str(conf_type).split()[1][1:-2]
        raise CLGError(path, INVALID_SECTION.format(type=type_str))


def _check_keywords(path, conf, section, one=None, need=None):
    """Check items of **conf** from **KEYWORDS[section]**. **one** indicate
    whether a check must be done on the number of elements or not."""
    valid_keywords = [keyword
                      for keywords in KEYWORDS[section].values()
                      for keyword in keywords]

    for keyword in conf:
        if keyword not in valid_keywords:
            raise CLGError(path, INVALID_KEYWORD.format(keyword=keyword))
        _check_empty(path + [keyword], conf[keyword])

    if one and len([arg for arg in conf if arg in one]) != 1:
        keywords_str = "', '".join(one)
        raise CLGError(path, ONE_KEYWORDS.format(keywords=keywords_str))

    if need:
        for keyword in need:
            if keyword not in conf:
                raise CLGError(path, MISSING_KEYWORD.format(keyword=keyword))


def _check_section(path, conf, section, one=None, need=None):
    """Check section is not empty, is a dict and have not extra keywords."""
    _check_empty(path, conf)
    _check_type(path, conf, dict)
    _check_keywords(path, conf, section, one=one, need=need)


#
# Post processing functions.
#
def _has_value(value, conf):
    """The value of an argument not passed in the command is *None*, except:
        * if **nargs** is ``*`` or ``+``: in this case, the value is an empty
          list (this is set by this module),
        * if **action** is ``store_true`` or ``store_false``: in this case, the
          value is respectively ``False`` and ``True``.
    This function take theses cases in consideration and check if an argument
    really has a value.
    """
    if value is None or (isinstance(value, list) and not value):
        return False

    if 'action' in conf:
        action = conf['action']
        store_true = (action == 'store_true' and not value)
        store_false = (action == 'store_false' and value)
        if store_true or store_false:
            return False
    return True


def _print_error(parser, msg):
    """Print parser usage with an error message at the end and exit."""
    parser.print_usage()
    print("%s: error: %s" % (parser.prog, msg))
    sys.exit(1)


def _post_need(parser, parser_args, args_values, arg):
    """Post processing that check all for needing options."""
    arg_type, arg_conf = parser_args[arg]
    for cur_arg in arg_conf['need']:
        cur_arg_type, cur_arg_conf = parser_args[cur_arg]
        if not _has_value(args_values[cur_arg], cur_arg_conf):
            arg_str = (_format_optdisplay(arg, arg_conf)
                       if arg_type == 'options' else arg)
            need_str = (_format_optdisplay(cur_arg, cur_arg_conf)
                        if cur_arg_type == 'options' else cur_arg)
            _print_error(parser, NEED_ERR.format(type=arg_type[:-1],
                                                 arg=arg_str,
                                                 need_type=cur_arg_type[:-1],
                                                 need_arg=need_str))


def _post_conflict(parser, parser_args, args_values, arg):
    """Post processing that check for conflicting options."""
    arg_type, arg_conf = parser_args[arg]
    for cur_arg in arg_conf['conflict']:
        cur_arg_type, cur_arg_conf = parser_args[cur_arg]
        if _has_value(args_values[cur_arg], cur_arg_conf):
            arg_str = (_format_optdisplay(arg, arg_conf)
                       if arg_type == 'options' else arg)
            conflict_str = (_format_optdisplay(cur_arg, cur_arg_conf)
                            if cur_arg_type == 'options' else cur_arg)
            _print_error(parser,
                         CONFLICT_ERR.format(type=arg_type[:-1],
                                             arg=arg_str,
                                             conflict_type=cur_arg_type[:-1],
                                             conflict_arg=conflict_str))


def _post_match(parser, parser_args, args_values, arg):
    """Post processing that check the value."""
    arg_type, arg_conf = parser_args[arg]
    pattern = arg_conf['match']

    msg_elts = {'type': arg_type, 'arg': arg, 'pattern': pattern}
    if arg_conf.get('nargs', None) in ('*', '+'):
        for value in args_values[arg]:
            if not re.match(pattern, value):
                _print_error(parser, MATCH_ERR.format(val=value, **msg_elts))
    elif not re.match(pattern, args_values[arg]):
        _print_error(parser, MATCH_ERR.format(val=args_values[arg], **msg_elts))


def _exec_module(path, exec_conf, args_values):
    """Load and execute a function of a module according to **exec_conf**."""
    mdl_func = exec_conf.get('function', 'main')
    mdl_tree = exec_conf['module'].split('.')
    mdl = None

    for mdl_idx, mdl_name in enumerate(mdl_tree):
        try:
            imp_args = imp.find_module(mdl_name, mdl.__path__ if mdl else None)
            mdl = imp.load_module('.'.join(mdl_tree[:mdl_idx + 1]), *imp_args)
        except (ImportError, AttributeError) as err:
            raise CLGError(path, LOAD_ERR.format(err=err))
    getattr(mdl, mdl_func)(args_values)


def _exec_file(path, exec_conf, args_values):
    """Load and execute a function of a file according to **exec_conf**."""
    mdl_path = os.path.abspath(exec_conf['file'])
    mdl_name = os.path.splitext(os.path.basename(mdl_path))[0]
    mdl_func = exec_conf.get('function', 'main')

    try:
        getattr(imp.load_source(mdl_name, mdl_path), mdl_func)(args_values)
    except (IOError, ImportError, AttributeError) as err:
        raise CLGError(path, FILE_ERR.format(err=err))


#
# Classes.
#
class NoAbbrevParser(argparse.ArgumentParser):
    """Child class of **ArgumentParser** allowing to disable abbravetions."""
    def _get_option_tuples(self, option_string):
        return []


class Namespace(argparse.Namespace):
    """Iterable namespace."""
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
        return ((key, value) for key, value in iteritems(self.__dict__))


class CommandLine(object):
    """CommandLine object that parse a preformatted dictionnary and generate
    ``argparse`` parser."""
    def __init__(self, config, keyword='command'):
        """Initialize the command from **config** which is a dictionnary
        (preferably an OrderedDict). **keyword** is the name use for knowing the
        path of subcommands (ie: 'command0', 'command1', ... in the namespace of
        arguments)."""
        self.config = config

        # Manage the case when we want a help command that prints a description
        # of all commands.
        self.help_cmd = config.pop('add_help_cmd', False)
        if self.help_cmd:
            try:
                subparsers_conf = self.config['subparsers']
            except KeyError:
                raise CLGError('unable to add help command: no subparsers')

            if 'parsers' in subparsers_conf:
                subparsers_conf['parsers'] = OrderedDict(
                    list(HELP_PARSER.items())
                    + list(subparsers_conf['parsers'].items()))
            else:
                subparsers_conf = OrderedDict(
                    list(HELP_PARSER.items())
                    + list(subparsers_conf.items()))
            self.config['subparsers'] = subparsers_conf

        self.keyword = keyword
        self._parsers = OrderedDict()
        self.parser = None
        self._add_parser([])


    def _get_config(self, path, ignore=True):
        """Retrieve an element configuration (based on **path**) in the
        configuration."""
        config = self.config
        for idx, elt in enumerate(path):
            if elt.startswith('#'):
                config = config[int(elt[1:])]
            else:
                config = (config['parsers'][elt]
                          if (not ignore
                              and path[idx-1] == 'subparsers'
                              and 'parsers' in config)
                          else config[elt])
        return config


    def _add_parser(self, path, parser=None):
        """Add a subparser to a parser. If **parser** is ``None``, the subparser
        is in fact the main parser."""
        # Get configuration.
        parser_conf = self._get_config(path)

        # Check parser configuration.
        _check_section(path, parser_conf, 'parsers')
        if 'execute' in parser_conf:
            _check_section(path + ['execute'],
                           parser_conf['execute'],
                           'execute',
                           one=('module', 'file'))

        # Initialize parent parser.
        if parser is None:
            self.parser = (argparse.ArgumentParser
                           if parser_conf.pop('allow_abbrev', False)
                           else NoAbbrevParser)(**_gen_parser(parser_conf))
            parser = self.parser

        # Index parser (based on path) as it may be necessary to access it
        # later (manage case where subparsers does not have configuration).
        parser_path = [elt
                       for idx, elt in enumerate(path)
                       if not (path[idx-1] == 'subparsers'
                               and elt == 'parsers')]
        self._parsers['/'.join(parser_path)] = parser

        # Add custom usage.
        if 'usage' in parser_conf:
            parser.usage = _format_usage(parser.prog, parser_conf['usage'])

        # Add subparsers.
        if 'subparsers' in parser_conf:
            self._add_subparsers(parser,
                                 path + ['subparsers'],
                                 parser_conf['subparsers'])

        # Add options and arguments.
        for arg_type in ('options', 'args'):
            arg_path = path + [arg_type]
            arg_type_conf = parser_conf.get(arg_type, {})
            _check_type(arg_path, arg_type_conf, dict)
            for arg, arg_conf in iteritems(arg_type_conf):
                arg_path.append(arg)
                self._add_arg(parser, arg_path, arg, arg_type, arg_conf)

        # Add groups.
        for grp_type in ('groups', 'exclusive_groups'):
            if grp_type in parser_conf:
                _check_empty(path, parser_conf[grp_type])
                _check_type(path, parser_conf[grp_type], list)
                for index, group in enumerate(parser_conf[grp_type]):
                    grp_path = path + [grp_type, '#%d' % index]
                    self._add_group(parser, grp_path, group, grp_type)


    def _add_subparsers(self, parser, path, subparsers_conf):
        """Add subparsers. Subparsers can have a global configuration or
        directly parsers configuration. This is the keyword **parsers** that
        indicate it."""
        # Get arguments to pass to add_subparsers method.
        required = True
        subparsers_kwargs = {'dest': '%s%d' % (self.keyword, len(path) / 2)}
        if 'parsers' in subparsers_conf:
            _check_section(path, subparsers_conf, 'subparsers')

            keywords = KEYWORDS['subparsers']['argparse']
            subparsers_kwargs.update({keyword: subparsers_conf[keyword]
                                      for keyword in keywords
                                      if keyword in subparsers_conf})
            required = subparsers_conf.get('required', True)

            subparsers_conf = subparsers_conf['parsers']
            path.append('parsers')

        # Initialize subparsers.
        subparsers = parser.add_subparsers(**subparsers_kwargs)
        subparsers.required = required

        # Add subparsers.
        for parser_name, parser_conf in iteritems(subparsers_conf):
            _check_section(path + [parser_name], parser_conf, 'parsers')
            subparser = subparsers.add_parser(parser_name,
                                              **_gen_parser(parser_conf,
                                                            subparser=True))
            self._add_parser(path + [parser_name], subparser)


    def _add_group(self, parser, path, conf, grp_type):
        _check_section(path, conf, grp_type)
        params = {keyword: conf.pop(keyword)
                  for keyword in KEYWORDS[grp_type]['argparse']
                  if keyword in conf}
        grp_method = {'groups': 'add_argument_group',
                      'exclusive_groups': 'add_mutually_exclusive_group'
                     }[grp_type]
        group = getattr(parser, grp_method)(**params)
        self._add_parser(path, group)


    def _add_arg(self, parser, path, arg, arg_type, arg_conf):
        """Add an option/argument to **parser**."""
        # Check configuration.
        _check_section(path, arg_conf, arg_type)
        for keyword in ('need', 'conflict'):
            if keyword not in arg_conf:
                continue
            _check_type(path + [keyword], arg_conf[keyword], list)
            for cur_arg in arg_conf[keyword]:
                if cur_arg not in parser_args:
                    cur_arg_type = parser_args[cur_arg][0][:-1]
                    raise CLGError(arg_path + [keyword],
                                   UNKNOWN_ARG.format(type=cur_arg_type,
                                                      arg=cur_arg))

        # Get argument parameters.
        arg_args, arg_kwargs = [], {}
        if arg_type == 'options':
            if 'short' in arg_conf:
                if len(arg_conf['short']) != 1:
                    raise CLGError(arg_path + ['short'], SHORT_ERR)
                arg_args.append('-%s' % arg_conf['short'])
                del arg_conf['short']
            arg_args.append('--%s' % _format_optname(arg))
            arg_kwargs['dest'] = arg
        elif arg_type == 'args':
            arg_args.append(arg)

        default = str(arg_conf.get('default', '?'))
        choices = ', '.join(map(str, arg_conf.get('choices', ['?'])))
        match = str(arg_conf.get('match', '?'))
        for param, value in sorted(iteritems(arg_conf)):
            if param in KEYWORDS[arg_type]['post']:
                continue

            arg_kwargs[param] = {
                'type': lambda: TYPES[value],
                'help': lambda: value.replace('__DEFAULT__', default)
                                     .replace('__CHOICES__', choices)
                                     .replace('__MATCH__', match)
                                     .replace('__FILE__', sys.path[0])
                }.get(param, lambda: _set_builtin(value))()

        # Add argument to parser.
        parser.add_argument(*arg_args, **arg_kwargs)


    def parse(self, args=None):
        """Parse command-line."""
        # Parse command-line.
        args_values = Namespace(self.parser.parse_args(args).__dict__)
        if self.help_cmd and args_values['command0'] == 'help':
            self.print_help()

        # Get command configuration.
        path = [elt
                for arg, value in sorted(args_values) if value
                for elt in ('subparsers', value)
                if re.match('^%s[0-9]*$' % self.keyword, arg)]
        parser_conf = self._get_config(path, ignore=False)
        parser = self._parsers['/'.join(path)]

        # Post processing.
        parser_args = _get_args(parser_conf)
        for arg, (arg_type, arg_conf) in iteritems(parser_args):
            if any((arg_conf.get('default', '') == '__SUPPRESS__',
                    arg_conf.get('action', '') == 'version')):
                continue
            if not _has_value(args_values[arg], arg_conf):
                if arg_conf.get('nargs', None) in ('*', '+'):
                    args_values[arg] = []
                continue

            for keyword in KEYWORDS[arg_type]['post']:
                if keyword in arg_conf:
                    post_args = (parser, parser_args, args_values, arg)
                    getattr(SELF, '_post_%s' % keyword)(*post_args)

        # Execute.
        if 'execute' in parser_conf:
            for keyword in ('module', 'file'):
                if keyword in parser_conf['execute']:
                    exec_params = (path + ['execute'],
                                   parser_conf['execute'],
                                   args_values)
                    getattr(SELF, '_exec_%s' % keyword)(*exec_params)

        return args_values


    def print_help(self):
        """Print commands' tree with theirs descriptions."""
        # Get column at which we must start printing the description.
        import math
        lengths = []
        for path in self._parsers:
            length = 0
            cmds = list(filter(lambda e: e != 'subparsers', path.split('/')))
            lengths.append(3 * (len(cmds)) + len(cmds[-1]))
        start = max(lengths) + 4
        desc_len = 80 - start

        # Print arboresence of commands with their descriptions. This use
        # closures so we don't have to pass whatmille arguments to functions.
        def parse_conf(cmd_conf, level, last_parent):
            def print_line(cmd, line, first_line, last_cmd):
                symbols = '│ ' * (level - 1)
                symbols += ('  ' if last_parent else '│ ') if level else ''
                symbols += (('└─' if last_cmd else '├─')
                            if first_line
                            else ('  ' if last_cmd else '│ '))
                print('%s%s %s' % (symbols,
                                    cmd if first_line else '',
                                    '\033[%sG%s' % (start, line)))

            if not 'subparsers' in cmd_conf:
                return

            subparsers_conf = (cmd_conf['subparsers']['parsers']
                               if 'parsers' in cmd_conf['subparsers']
                               else cmd_conf['subparsers'])
            nb_cmds = len(subparsers_conf) - 1
            for index, cmd in enumerate(subparsers_conf):
                cmd_conf = subparsers_conf[cmd]
                desc = cmd_conf.get('help', '').strip().split()

                first_line = True
                last_cmd = index == nb_cmds
                cur_line = ''
                while desc:
                    cur_word = desc.pop(0)
                    if (len(cur_line) + 1 + len(cur_word)) > desc_len:
                        print_line(cmd, cur_line, first_line, last_cmd)
                        first_line=False
                        cur_line = ''
                    cur_line += ' ' + cur_word
                print_line(cmd, cur_line, first_line, last_cmd)
                parse_conf(cmd_conf, level + 1, last_cmd)
        parse_conf(self.config, 0, False)
        sys.exit(0)
