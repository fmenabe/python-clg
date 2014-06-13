# -*- coding : utf-8 -*-

import os
import re
import sys
import imp
import copy
import argparse


# Get builtins.
BUILTINS = sys.modules['builtins'
                       if sys.version_info.major == 3
                       else '__builtin__']

# Keywords (argparse and clg).
KEYWORDS = {
    'parser': {'argparse': ['prog', 'usage', 'description', 'epilog', 'help',
                            'add_help', 'formatter_class', 'argument_default',
                            'conflict_handler'],
               'clg': ['anchors', 'subparsers', 'options', 'args', 'groups',
                       'exclusive_groups', 'execute']},
    'subparser': {'argparse': ['title', 'description', 'prog', 'help',
                               'metavar'],
                  'clg': ['required', 'parsers']},
    'group': {'argparse': ['title', 'description'],
              'clg': ['options']},
    'exclusive_group': {'argparse': ['required'],
                        'clg': ['options']},
    'option': {'argparse': ['action', 'nargs', 'const', 'default', 'choices',
                            'required', 'help', 'metavar', 'type'],
               'clg': ['short'],
               'post': ['match', 'need', 'conflict']},
    'argument': {'argparse': ['action', 'nargs', 'const', 'default', 'choices',
                              'required', 'help', 'metavar', 'type'],
                 'clg': ['short'],
                 'post': ['match']},
    'execute': {'needone': ['module', 'file'],
                'optional': ['function']}}

# Errors messages.
INVALID_SECTION = "this section is not a '%s'"
EMPTY_CONF = 'configuration is empty'
ONE_KEYWORDS = "this section need (only) one theses keywords: '%s'"
UNKNOWN_KEYWORD = "unknown keyword '%s'"
NEED_ERROR = '%s: error: argument %s: need %s argument'
CONFLICT_ERROR = '%s: error: argument %s: conflict with %s argument'
MATCH_ERROR = "%s: value '%s' of %s '%s' does not match '%s'"


class CLGError(Exception):
    def __init__(self, path, msg):
        Exception.__init__(self, msg)
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


#
# Utils functions.
#
def _gen_parser(parser_conf, subparser=False):
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


def _set_builtin(value):
    try:
        return getattr(BUILTINS,
                       re.search('^__([A-Z]*)__$', value).group(1).lower())
    except (AttributeError, TypeError):
        return (value.replace('__FILE__', sys.path[0])
                if type(value) is str
                else value)


def _has_value(opt_val, opt_conf):
    if opt_val is None or (isinstance(opt_val, list) and not opt_val):
        return False

    if 'action' in opt_conf:
        action = opt_conf['action']
        store_true = (action == 'store_true' and not opt_val)
        store_false = (action == 'store_false' and opt_val)
        if store_true or store_false:
            return False
    return True


def _print_error(parser, msg, *args):
    parser.print_usage()
    values = [parser.prog]
    values.extend(args)
    print(msg % tuple(values))
    sys.exit(1)


#
# Formatting functions.
#
def _format_usage(prog, usage):
    """Format usage."""
    spaces = ''.join([' ' for _ in "usage: "])
    usage_elts = [prog]
    usage_elts.extend(["%s  %s" % (spaces, elt)
                       for elt in usage.split('\n')[:-1]])
    return '\n'.join(usage_elts)


def _format_optname(value):
    return value.replace('_', '-').replace(' ', '-')


def _format_optdisplay(value, conf):
    return ('-%s/--%s' % (conf['short'], _format_optname(value))
            if 'short' in conf
            else '--%s' % _format_optname(value))


#
# Check functions.
#
def _check_conf(path, conf, section):
    # Check config is not empty.
    if conf is None:
        raise CLGError(path, EMPTY_CONF)

    # Check type of the configuration.
    if not isinstance(conf, dict):
        raise CLGError(path, INVALID_SECTION % 'dict')

    # Check keywords.
    valid_keywords = [keyword
                      for keywords in KEYWORDS[section].values()
                      for keyword in keywords]
    for keyword in conf:
        if keyword not in valid_keywords:
            raise CLGError(path, UNKNOWN_KEYWORD % keyword)
        if conf[keyword] is None:
            raise CLGError(path + [keyword], EMPTY_CONF)


def _check_subparsers(path, conf):
    # Check configuration is not empty.
    if conf is None:
        raise CLGError(path, EMPTY_CONF)
    if not isinstance(conf, dict):
        raise CLGError(path, INVALID_SECTION % 'dict')

    if 'parsers' in conf:
        _check_conf(path, conf, 'subparser')

        for keyword in KEYWORDS['subparser']['argparse']:
            if keyword in conf and not isinstance(conf[keyword], str):
                raise CLGError(path + [keyword], INVALID_SECTION % 'string')

        if not isinstance(conf['parsers'], dict):
            raise CLGError(path + ['parsers'], INVALID_SECTION % 'dict')


def _check_group(path, conf, options, grp_type, grp_number):
    path = path + [grp_type, '#%d' % (grp_number + 1)]
    section = 'group' if grp_type == 'groups' else 'exclusive_group'

    # Check group configuration (type and keywords).
    _check_conf(path, conf, section)

    # Check group options.
    if 'options' not in conf:
        raise CLGError(path, "'options' keyword is needed")
    if not isinstance(conf['options'], list):
        raise CLGError(path, INVALID_SECTION % 'list')
    if len(conf['options']) == 1:
        raise CLGError(path, "need at least two options")
    for opt in conf['options']:
        if opt not in options:
            raise CLGError(path, "unknown option '%s'" % opt)


def _check_opt(path, conf, opts):
    if 'short' in conf and len(conf['short']) != 1:
        raise CLGError(path + ['short'], "this must be a single letter")

    for keyword in ('need', 'conflict'):
        if keyword not in conf:
            continue
        for opt in conf[keyword]:
            if opt not in opts:
                raise CLGError(path + [keyword], "unknown option '%s'" % opt)


def _check_execute(path, conf):
    path = path + ['execute']
    _check_conf(path, conf, 'execute')

    keywords = KEYWORDS['execute']['needone']
    if [arg in conf for arg in keywords].count(True) != 1:
        raise CLGError(path, ONE_KEYWORDS % ("', '".join(keywords)))


def _check_dependency(args, options, option, parser, keyword):
    for optname in options[option][keyword]:
        has_value = _has_value(args[optname], options[optname])
        need = (keyword == 'need' and not has_value)
        conflict = (keyword == 'conflict' and has_value)
        if need or conflict:
            _print_error(parser,
                         NEED_ERROR if keyword == 'need' else CONFLICT_ERROR,
                         _format_optdisplay(option, options[option]),
                         _format_optdisplay(optname, options[optname]))


def _check_match(parser, config, arg, value, arg_type):
    pattern = config.get('match', None)
    if pattern is None:
        return

    if 'nargs' in config and config['nargs'] in ('*', '+'):
        [_print_error(parser, MATCH_ERROR, val, arg_type, arg, pattern)
         for val in value
         if not re.match(pattern, val)]
    elif not re.match(pattern, value):
        _print_error(parser, MATCH_ERROR, value, arg_type, arg, pattern)


#
# CommandLine object.
#
class CommandLine(object):
    def __get_config(self, path, ignore=True):
        config = self.config
        for index, elt in enumerate(path):
            config = (config['parsers'][elt]
                      if (not ignore
                          and path[index-1] == 'subparsers'
                          and 'parsers' in config)
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


    def _add_parser(self, path, parser=None):
        """Add a parser to a subparser."""
        # Get and check parser configuration.
        conf = self.__get_config(path)
        _check_conf(path, conf, 'parser')
        if 'execute' in conf:
            _check_execute(path, conf['execute'])

        # Initialize parent parser.
        if parser is None:
            self.parser = argparse.ArgumentParser(**_gen_parser(conf))
            parser = self.parser
        # Set custom usage.
        if 'usage' in conf:
            parser.usage = _format_usage(parser.prog, conf['usage'])

        # It may be needed to access the parser object later (for printing
        # usage for example), so memorize it.
        parser_path = '/'.join(elt
                               for idx, elt in enumerate(path)
                               if not (path[idx-1] == 'subparsers'
                                       and elt == 'parsers'))
        self.__parsers.setdefault(parser_path, parser)

        # Add subparsers.
        if 'subparsers' in conf:
            self._add_subparsers(path, parser, conf['subparsers'])

        # For options, use a deep copy for not altering initial configuration
        # when change must be done in it (when generating groups by example).
        opts_conf = copy.deepcopy(conf.get('options', {}))

        # Add groups.
        for grp_type in 'groups', 'exclusive_groups':
            if not isinstance(conf.get(grp_type, []), list):
                raise CLGError(path, INVALID_SECTION % (grp_type, 'list'))
            for grp_number, grp_conf in enumerate(conf.get(grp_type, [])):
                self._add_group(path, parser, grp_conf,
                                opts_conf, grp_type, grp_number)

        # Add options.
        for opt_name, opt_conf in opts_conf.items():
            self._add_arg(path, parser, opt_name, opt_conf, True)

        # Add args.
        args_conf = conf.get('args', {})
        for arg_name, arg_conf in args_conf.items():
            self._add_arg(path, parser, arg_name, arg_conf, False)


    def _add_subparsers(self, path, parser, subparsers_config):
        """Add subparsers to a parser."""
        path.append('subparsers')
        _check_subparsers(path, subparsers_config)

        # Initiliaze subparsers.
        required = True
        subparsers_init = {'dest': '%s%d' % (self.keyword, len(path) / 2)}
        if 'parsers' in subparsers_config:
            path.append('parsers')
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
            subparser_path = list(path)
            subparser_path.append(parser_name)
            _check_conf(subparser_path, parser_config, 'parser')
            subparser = subparsers.add_parser(parser_name,
                                              **_gen_parser(parser_config, True))
            self._add_parser(subparser_path, subparser)


    def _add_group(self, path, parser, conf, opts, grp_type, grp_number):
        """Add a group of options to a parser."""
        _check_group(path, conf, opts, grp_type, grp_number)
        grp_type = 'group' if grp_type == 'groups' else 'exclusive_group'

        # Add group or exclusive group to parser.
        if grp_type == 'groups':
            group = parser.add_argument_group(
                **{key: value
                   for key, value in conf.items()
                   if key in KEYWORDS[grp_type]['argparse']})
        else:
            required=conf.get('required', False)
            group = parser.add_mutually_exclusive_group(required=required)

        # Add options to the group.
        for opt in conf['options']:
            self._add_arg(path, group, opt, opts[opt], True)
            del opts[opt]


    def _add_arg(self, path, parser, arg_name, conf, isopt):
        """Add an argument/option to a parser."""
        path = path + ['options' if isopt else 'args', arg_name]
        arg_type = "%s" % ('option' if isopt else 'argument')
        _check_conf(path, conf, arg_type)

        opt_args, opt_kwargs = [], {}
        if isopt:
            opts = self.__get_config(path[:-1])
            _check_opt(path, conf, opts)
            if 'short' in conf:
                opt_args.append('-%s' % conf['short'])
                del conf['short']
            opt_args.append('--%s' % _format_optname(arg_name))
            opt_kwargs.setdefault('dest', arg_name)
        else:
            opt_args.append(arg_name)

        default = str(conf.get('default', '?'))
        match = str(conf.get('match', '?'))
        for param, value in sorted(conf.items()):
            if param in KEYWORDS['option']['post']:
                continue

            opt_kwargs.setdefault(
                param,
                {'type': lambda: getattr(BUILTINS, value),
                 'help': lambda: value.replace('__DEFAULT__', default)
                                      .replace('__MATCH__', match)
                }.get(param, lambda: _set_builtin(value))())

        parser.add_argument(*opt_args, **opt_kwargs)


    def parse(self, args=None):
        """Parse arguments."""
        # Parse arguments.
        args = Namespace(self.parser.parse_args(args).__dict__)

        # Get subparser configuration.
        path = []
        for arg, value in sorted(args):
            if re.match('^%s[0-9]*$' % self.keyword, arg):
                path.extend([value, 'subparsers'])
        if path:
            path = ['subparsers'] + path[:-1]
        conf = self.__get_config(path, ignore=False)
        parser = self.__parsers['/'.join(path)]

        # Options checks.
        for opt_name, opt_conf in conf.get('options', {}).items():
            if not _has_value(args[opt_name], opt_conf):
                if 'nargs' in opt_conf and opt_conf['nargs'] in ('*', '+'):
                    args[opt_name] = []
                continue

            for keyword in ('need', 'conflict'):
                if keyword in opt_conf:
                    if not isinstance(opt_conf[keyword], list):
                        raise CLGError(path + ["options/%s" % opt_name],
                                       INVALID_SECTION % ('need', 'list'))
                    _check_dependency(args, conf['options'],
                                      opt_name, parser, keyword)

            _check_match(parser, opt_conf, opt_name, args[opt_name], 'option')

        # Arguments check.
        for arg_name, arg_conf in conf.get('args', {}).items():
            _check_match(parser, arg_conf, arg_name, args[arg_name], 'argument')

        # Execute.
        if 'execute' in conf:
            if 'module' in conf['execute']:
                self._exec_module(conf['execute'], args, path)
            if 'file' in conf['execute']:
                self._exec_file(conf['execute'], args, path)

        return args


    def _exec_file(self, conf, args, path):
        """Load and execute a python file."""
        mdl_path = os.path.abspath(conf['file'])
        mdl_name = os.path.splitext(os.path.basename(mdl_path))[0]
        mdl_func = conf.get('function', 'main')

        if not os.path.exists(mdl_path):
            raise CLGError(path + ['file'],
                           "file '%s' not exists" % mdl_path)

        getattr(imp.load_source(mdl_name, mdl_path), mdl_func)(args)


    def _exec_module(self, conf, args, path):
        """Load and execute a python module."""
        mdl_func = conf.get('function', 'main')
        mdl_tree = conf['module'].split('.')
        mdl = None

        for mdl_idx, mdl_name in enumerate(mdl_tree):
            try:
                imp_args = imp.find_module(mdl_name,
                                           mdl.__path__ if mdl else None)
                mdl = imp.load_module('.'.join(mdl_tree[:mdl_idx + 1]),
                                      *img_args)
            except (ImportError, AttributeError) as err:
                raise CLGError(path + ['module'],
                               "Unable to load module '%s': %s" % (mdl, err))

        getattr(mdl, mdl_func)(args)
