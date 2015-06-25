********
Examples
********

All theses examples (and more) are available in the *examples* directory of the
`github repository <https://github.com/fmenabe/python-clg>`_. All examples
describe here use a YAML file.

First argparse example
----------------------
This is the first `argparse example
<https://docs.python.org/dev/library/argparse.html#example>`_. This show a
simple command with an option, an argument and the use of builtins.

*Python program*:

.. code-block:: python

    import clg
    import yaml

    cmd = clg.CommandLine(yaml.load(open('builtins.yml')))
    args = cmd.parse()
    print(args.sum(args.integers))

*Configuration file*:

.. code-block:: yaml

    description: Process some integers.

    options:
        sum:
            action: store_const
            const: __SUM__
            default: __MAX__
            help: "sum the integers (default: find the max)."

    args:
        integers:
            metavar: N
            type: int
            nargs: +
            help: an integer for the accumulator

*Executions*:

.. code:: bash

    # python builtins.py -h
    usage: builtins.py [-h] [--sum] N [N ...]

    Process some integers.

    positional arguments:
      N           an integer for the accumulator

    optional arguments:
      -h, --help  show this help message and exit
      --sum       sum the integers (default: find the max).

    # python builtins.py 1 2 3 4
    4

    # python builtins.py 1 2 3 4 --sum
    10


Subparsers example
------------------
This is the same example that `argparse subparsers documentation
<https://docs.python.org/dev/library/argparse.html#sub-commands>`_.

The python program initialize ``clg`` and print arguments:

.. code-block:: python

    import clg
    import yaml

    cmd = clg.CommandLine(yaml.load(open('subparsers.yml')))
    print(cmd.parse())

Without custom help
~~~~~~~~~~~~~~~~~~~
We begin by a simple configuration without personalizing subparsers help.
``subparsers`` section just contains the configuration of commands.

*Configuration file*:

.. code-block:: yaml

    prog: PROG

    options:
        foo:
            action: store_true
            help: foo help

    subparsers:
        a:
            help: a help
            options:
                bar:
                    type: int
                    help: bar help
        b:
            help: b help
            options:
                baz:
                    choices: XYZ
                help: baz help

*Executions*:

.. code:: bash

    # python subparsers.py --help
    usage: PROG [-h] [--foo] {a,b} ...

    positional arguments:
      {a,b}
        a         a help
        b         b help

    optional arguments:
      -h, --help  show this help message and exit
      --foo       foo help

    # python subparsers.py a 12
    Namespace(bar=12, command0='a', foo=False)

    # python subparsers.py --foo b --baz Z
    Namespace(baz='Z', command0='b', foo=True)

With custom help
~~~~~~~~~~~~~~~~
Now we customize the help. The configuration of commands is put in the
``parsers`` section and other keywords are used for customizing help.

*Configuration file*:

.. code-block:: yaml

    prog: PROG

    options:
        foo:
            action: store_true
            help: foo help

    subparsers:
        title: subcommands
        description: valid subcommands
        help: additional help
        prog: SUBCOMMANDS
        metavar: "{METAVAR}"
        parsers:
            a:
                help: a help
                options:
                    bar:
                        type: int
                        help: bar help
            b:
                help: b help
                options:
                    baz:
                        choices: XYZ
                    help: baz help

*Executions*:

.. code:: bash

    # python subparsers.py --help
    usage: PROG [-h] [--foo] {METAVAR} ...

    optional arguments:
      -h, --help  show this help message and exit
      --foo       foo help

    subcommands:
      valid subcommands

      {METAVAR}   additional help
        a         a help
        b         b help

    # python subparsers.py a --help
    usage: SUBCOMMANDS a [-h] bar

    positional arguments:
      bar         bar help

    optional arguments:
      -h, --help  show this help message and exit


Groups example
--------------
This is the same example that `argparse groups documentation
<https://docs.python.org/dev/library/argparse.html#argument-groups>`_ .

*Configuration file*:

.. code-block:: yaml

    groups:
        - title: group
          description: group description
          options:
            foo:
                help: foo help
          args:
            bar:
                help: bar help
                nargs: "?"


*Execution*:

.. code:: bash

    # python groups.py --help
    usage: groups.py [-h] [--foo FOO] [bar]

    optional arguments:
      -h, --help  show this help message and exit

    group:
      group description

      --foo FOO   foo help
      bar         bar help

Exclusive groups example
------------------------
This is the same example that `argparse exclusives groups documentation
<https://docs.python.org/dev/library/argparse.html#mutual-exclusion>`_ .

*Configuration file*:

.. code-block:: yaml

    prog: PROG

    exclusive_groups:
        - options:
            foo:
                action: store_true
            bar:
                action: store_false

*Executions*:

.. code:: bash

    # python exclusive_groups.py --bar
    Namespace(bar=False, foo=False)

    # python exclusive_groups.py --foo
    Namespace(bar=True, foo=True)

    # python exclusive_groups.py --foo --bar
    usage: PROG [-h] [--foo | --bar]
    PROG: error: argument --bar: not allowed with argument --foo


Utility for managing KVM virtuals machines
------------------------------------------
This example is a program I made for managing KVM guests. Actually, there is
only two commands for deploying or migrating guests. Each command use an
external module for implementing the logic. A ``main`` function, taking the
command-line Namespace as argument, has been implemented. For the example,
theses functions will only pprint the command-line arguments.

This example use:
    * YAML anchors
    * subparsers, options, arguments, groups and exclusives groups
    * custom types
    * special "builtins",
    * the root 'help' command
    * specific formatter class
    * ...

*Directory structure*:

.. code:: bash

    .
    ├── commands
    │   ├── deploy.py
    │   ├── __init__.py
    │   └── migrate.py
    ├── kvm.py
    └── kvm.yml

*kvm.py*:

.. code-block:: python

    import clg
    import yaml
    import yamlordereddictloader
    from os import path

    CMD_FILE = path.abspath(path.join(path.dirname(__file__), 'kvm.yml'))

    # Add custom command-line types.
    from commands.deploy import InterfaceType, DiskType, FormatType
    clg.TYPES.update({'Interface': InterfaceType, 'Disk': DiskType, 'Format': FormatType})

    def main():
        cmd = clg.CommandLine(yaml.load(open('kvm.yml'),
                                        Loader=yamlordereddictloader.Loader))
        cmd.parse()

    if __name__ == '__main__':
        main()

*commands/deploy.py*

.. code-block:: python

    from pprint import pprint

    SELF = sys.modules[__name__]
    first_interface = True
    def InterfaceType(value):
        """Custom type for '--interfaces' option with an ugly hack for knowing
        whether this is the first interface."""
        int_conf = dict(inet='static')
        if SELF.first_interface:
            nettype, source, address, netmask, gateway = value.split(',')
            SELF.first_interface = False
            int_conf.update(address=address, netmask=netmask, gateway=gateway)
        else:
            nettype, source, address, netmask = value.split(',')
            int_conf.update(address=address, netmask=netmask)
        return dict(kvm=dict(type=nettype, source=source), conf=int_conf)

    def DiskType(value):
        """Custom type for '--disks' option."""
        value = value.split(',')
        suffix, size = value[:2]
        try:
            fmt = value[2]
            options = {opt: value
                       for elt in value[3:]
                       for opt, value in [elt.split('=')]}
        except IndexError:
            fmt, options = locals().get('fmt', 'qcow2'), {}

        return dict(suffix=suffix, size=size, format=fmt, options=options)

    def FormatType(value):
        """Custom type for '--format' option."""
        value = value.split(',')
        fmt = value.pop(0)
        if fmt not in ('qcow2', 'raw'):
            import argparse
            raise argparse.ArgumentTypeError("format must either 'qcow2' or 'raw'")
        options = {opt: opt_val for elt in value for opt, opt_val in [elt.split('=')]}
        return dict(type=fmt, options=options)


    def main(args):
        pprint(vars(args))

*Configuration file*:

.. code-block:: yaml

    add_help_cmd: True
    allow_abbrev: False
    description: Utility for managing KVM hosts.

    anchors:
        main: &MAIN
            help:
                short: h
                action: help
                default: __SUPPRESS__
                help: Show this help message and exit.
            conf_file:
                help: 'Configuration file (default: __DEFAULT__).'
                default: __FILE__/conf/conf.yml
            logdir:
                help: 'Log directory (default: __DEFAULT__).'
                default: __FILE__/logs
            loglevel:
                choices: [verbose, debug, info, warn, error, none]
                default: info
                help: 'Log level on console (default: __DEFAULT__).'

    subparsers:
        deploy:
            help: Deploy a new guest on an hyperviror based on a model.
            description: Deploy a new guest on an hypervisor based on a model.
            add_help: False
            formatter_class: RawTextHelpFormatter
            execute:
                module: commands.deploy

            groups:
                - title: Common options
                  options: *MAIN
                - title: Optional options
                  options:
                    cores:
                        short: c
                        type: int
                        default: 2
                        help: |
                            Number of cores assigned to the guest (default:
                            __DEFAULT__).
                    memory:
                        short: m
                        type: float
                        default: 2
                        help: |
                            Memory in Gb assigned to the guest (default: __DEFAULT__).
                    format:
                        type: Format
                        metavar: FORMAT,OPT1=VALUE,OPT2=VALUE,...
                        help: |
                            Format of the main image. Each format has options
                            that can be specified, separated by commas. By default
                            models use qcow2 images without options.
                    resize:
                        type: int
                        help: |
                            Resize (in fact, only increase) the main disk image.
                            For linux system, it will allocate the new size on the
                            root LVM Volume Group. This option only work on KVM
                            hypervisors which have a version of qemu >= 0.15.0.
                    disks:
                        nargs: '+'
                        type: Disk
                        metavar: DISK
                        help: |
                            Add new disk(s). Format of DISK is:
                              SUFFIX,SIZE[,FORMAT,OTP1=VAL, OPT2=VAL,...]
                            Where:
                                * SUFFIX is used for generating the filename of
                                  the image. The filename is: NAME-SUFFIX.FORMAT
                                * SIZE is the size in Gb
                                * FORMAT is the format of the image (default is
                                  'qcow2')
                                * OPT=VAL are the options of the format
                    force:
                        action: store_true
                        help: |
                            If a guest or some images already exists on the
                            destination, configuration and disk images are
                            automaticaly backuped, then overwrited, without
                            confirmation.
                    no_check:
                        action: store_true
                        help: |
                            Ignore checking of resources (use with cautions as
                            overloading an hypervisor could lead to bad
                            performance!).
                    no_autostart:
                        action: store_true
                        help: Don't set autostart for the new guest.
                    ...
                - title: Arguments
                  args:
                    name:
                        help: Name of the new guest.
                    dst_host:
                        help: Hypervisor on which deploy the new guest.
                    model:
                        metavar: MODEL
                        choices:
                            - ubuntu-lucid
                            - ubuntu-precise
                            - ubuntu-trusty
                            - redhat-5.8
                            - redhat-6.3
                            - centos-5
                            - w2003
                            - w2008r2
                        help: |
                            Model on which the new guest is based. Choices are:
                                * ubuntu-precise
                                * ubuntu-trusty
                                * redhat-5.8
                                * redhat-6.3
                                * centos-5
                                * w2003
                                * w2008-r2
                    interfaces:
                        nargs: '+'
                        type: Interface
                        metavar: INTERFACE
                        help: |
                            Network configuration. This is a list of network
                            interfaces configurations. Each interface
                            configuration is a list of parameters separated by
                            commas. Parameters are:
                                * the network type ('network' (NAT) or 'bridge'),
                                * the source (network name for 'network' type
                                  or vlan number for 'bridge' type),
                                * the IP address,
                                * the netmask,
                                * the gateway (only for the first interface)
                            For example, for deploying a guest with an inteface
                            in the public network and an interface in the storage
                            network:
                                * bridge,br903,130.79.200.1,255.255.254.0,130.79.201.254,801
                                * bridge,br896,172.30.0.1,255.255.254.0,896
                                * network,default,192.168.122.2,255.255.255.0,192.168.122.1

        migrate:
            description: >
                Move a guest to an other hypervisor. This command manage
                both cold and live migration.
            help: Move a guest to an other hypervisor.
            add_help: False
            execute:
                module: commands.migrate
            groups:
                - title: Common options
                  options: *MAIN
                - title: Optional options
                  options:
                    no_check:
                        action: store_true
                        help: >
                            Don't check for valid resources in the destination
                            hypervisor.
                    force:
                        action: store_true
                        help:
                            If a guest or some images already exists on the
                            destination, configuration and disk images are
                            automaticaly backuped, then overwrited, without
                            confirmation.
                    remove:
                        short: r
                        action: store_true
                        help: Remove guest on source hypervisor after migration.
                - title: Migration type (exclusive and required)
                  exclusive_groups:
                      - required: True
                        options:
                            cold:
                                short: c
                                action: store_true
                                help: Cold migration.
                            live:
                                short: l
                                action: store_true
                                help: Live migration.
                - title: Arguments
                  args:
                    src_host:
                        help: Hypervisor source.
                    name:
                        help: Name of the guest.
                    dst_host:
                        help: Hypervisor destination.


*Executions*:

.. code-block:: bash

    # python kvm.py
    usage: kvm.py [-h] {help,deploy,migrate} ...
    kvm.py: error: too few arguments

    # python kvm.py help
    ├─help               Print commands' tree with theirs descriptions.
    ├─deploy             Deploy a new guest on an hyperviror based on a model.
    └─migrate            Move a guest to an other hypervisor.

    # python kvm.py deploy --help
    usage: kvm.py deploy [-h] [--conf-file CONF_FILE] [--logdir LOGDIR]
                         [--loglevel {verbose,debug,info,warn,error,none}]
                         [-c CORES] [-m MEMORY]
                         [--format FORMAT,OPT1=VALUE,OPT2=VALUE,...]
                         [--resize RESIZE] [--disks DISK [DISK ...]] [--force]
                         [--no-check] [--no-autostart] [--no-chef] [--nbd NBD]
                         [--vgroot VGROOT] [--lvroot LVROOT] [-s SRC_HOST]
                         [--src-disks SRC_DISKS] [--dst-conf DST_CONF]
                         [--dst-disks DST_DISKS]
                         name dst_host MODEL INTERFACE [INTERFACE ...]

    Deploy a new guest on an hypervisor based on a model.

    Common options:
      -h, --help            Show this help message and exit.
      --conf-file CONF_FILE
                            Configuration file (default: /home/francois/dev/python-clg/examples/kvm/conf/conf.yml).
      --logdir LOGDIR       Log directory (default: /home/francois/dev/python-clg/examples/kvm/logs).
      --loglevel {verbose,debug,info,warn,error,none}
                            Log level on console (default: info).

    Optional options:
      -c CORES, --cores CORES
                            Number of cores assigned to the guest (default:
                            2).
      -m MEMORY, --memory MEMORY
                            Memory in Gb assigned to the guest (default: 2).
      --format FORMAT,OPT1=VALUE,OPT2=VALUE,...
                            Format of the main image. Each format has options
                            that can be specified, separated by commas. By default
                            models use qcow2 images without options.
      --resize RESIZE       Resize (in fact, only increase) the main disk image.
                            For linux system, it will allocate the new size on the
                            root LVM Volume Group. This option only work on KVM
                            hypervisors which have a version of qemu >= 0.15.0.
      --disks DISK [DISK ...]
                            Add new disk(s). Format of DISK is:
                              SUFFIX,SIZE[,FORMAT,OTP1=VAL, OPT2=VAL,...]
                            Where:
                                * SUFFIX is used for generating the filename of
                                  the image. The filename is: NAME-SUFFIX.FORMAT
                                * SIZE is the size in Gb
                                * FORMAT is the format of the image (default is
                                  'qcow2')
                                * OPT=VAL are the options of the format
      --force               If a guest or some images already exists on the
                            destination, configuration and disk images are
                            automaticaly backuped, then overwrited, without
                            confirmation.
      --no-check            Ignore checking of resources (use with cautions as
                            overloading an hypervisor could lead to bad
                            performance!).
      --no-autostart        Don't set autostart for the new guest.
      --no-chef             Don't update chef configuration.
      --nbd NBD             NBD device (in /dev) to use (default: 'nbd0').
      --vgroot VGROOT       Name of the LVM root Volume Group (default: 'sys').
      --lvroot LVROOT       Name of the LVM root Logical Volume (default:
                            'root').
      -s SRC_HOST, --src-host SRC_HOST
                            Host on which models are stored (default: 'bes1').
      --src-disks SRC_DISKS
                            Path of images files on the source hypervisor (default:
                            '/vm/disk').
      --dst-conf DST_CONF   Path of configurations files on the destination
                            hypervisor (default: '/vm/conf').
      --dst-disks DST_DISKS
                            Path of disks files on the destination hypervisor (default:
                            '/vm/disk')

    Arguments:
      name                  Name of the new guest.
      dst_host              Hypervisor on which deploy the new guest.
      MODEL                 Model on which the new guest is based. Choices are:
                                * ubuntu-precise
                                * ubuntu-trusty
                                * redhat-5.8
                                * redhat-6.3
                                * centos-5
                                * w2003
                                * w2008-r2
      INTERFACE             Network configuration. This is a list of network
                            interfaces configurations. Each interface
                            configuration is a list of parameters separated by
                            commas. Parameters are:
                                * the network type ('network' (NAT) or 'bridge'),
                                * the source (network name for 'network' type
                                  or vlan number for 'bridge' type),
                                * the IP address,
                                * the netmask,
                                * the gateway (only for the first interface)
                            For example, for deploying a guest with an inteface
                            in the public network and an interface in the storage
                            network:
                                * bridge,br903,130.79.200.1,255.255.254.0,130.79.201.254,801
                                * bridge,br896,172.30.0.1,255.255.254.0,896
                                * network,default,192.168.122.2,255.255.255.0,192.168.122.1

    # python kvm.py deploy
    usage: kvm.py deploy [-h] [--conf-file CONF_FILE] [--logdir LOGDIR]
                         [--loglevel {verbose,debug,info,warn,error,none}]
                         [-c CORES] [-m MEMORY]
                         [--format FORMAT,OPT1=VALUE,OPT2=VALUE,...]
                         [--resize RESIZE] [--disks DISK [DISK ...]] [--force]
                         [--no-check] [--no-autostart] [--no-chef] [--nbd NBD]
                         [--vgroot VGROOT] [--lvroot LVROOT] [-s SRC_HOST]
                         [--src-disks SRC_DISKS] [--dst-conf DST_CONF]
                         [--dst-disks DST_DISKS]
                         name dst_host MODEL INTERFACE [INTERFACE ...]
    kvm.py deploy: error: the following arguments are required: name, dst_host, MODEL, INTERFACE

    # python kvm.py deploy guest1
    usage: kvm.py deploy [-h] [--conf-file CONF_FILE] [--logdir LOGDIR]
                         [--loglevel {verbose,debug,info,warn,error,none}]
                         [-c CORES] [-m MEMORY]
                         [--format FORMAT,OPT1=VALUE,OPT2=VALUE,...]
                         [--resize RESIZE] [--disks DISK [DISK ...]] [--force]
                         [--no-check] [--no-autostart] [--no-chef] [--nbd NBD]
                         [--vgroot VGROOT] [--lvroot LVROOT] [-s SRC_HOST]
                         [--src-disks SRC_DISKS] [--dst-conf DST_CONF]
                         [--dst-disks DST_DISKS]
                         name dst_host MODEL INTERFACE [INTERFACE ...]
    kvm.py deploy: error: the following arguments are required: dst_host, MODEL, INTERFACE

    # python kvm.py deploy guest1 hypervisors1  192.168.122.1,255.255.255.0,192.168.122.1,500
    usage: kvm.py deploy [-h] [--conf-file CONF_FILE] [--logdir LOGDIR]
                         [--loglevel {verbose,debug,info,warn,error,none}]
                         [-c CORES] [-m MEMORY]
                         [--format FORMAT,OPT1=VALUE,OPT2=VALUE,...]
                         [--resize RESIZE] [--disks DISK [DISK ...]] [--force]
                         [--no-check] [--no-autostart] [--no-chef] [--nbd NBD]
                         [--vgroot VGROOT] [--lvroot LVROOT] [-s SRC_HOST]
                         [--src-disks SRC_DISKS] [--dst-conf DST_CONF]
                         [--dst-disks DST_DISKS]
                         name dst_host MODEL INTERFACE [INTERFACE ...]
    kvm.py deploy: error: argument MODEL: invalid choice: '192.168.122.1,255.255.255.0,192.168.122.1,500' (choose from 'ubuntu-lucid', 'ubuntu-precise', 'ubuntu-trusty', 'redhat-5.8', 'redhat-6.3', 'centos-5', 'w2003', 'w2008r2')

    # python kvm.py deploy guest1 hypervisors1 ubuntu-trusty bridge,192.168.122.1,255.255.255.0,192.168.122.1,500 -c 4 -m 4
    {'command0': 'deploy',
     'conf_file': '/home/francois/dev/python-clg/examples/kvm/conf/conf.yml',
     'cores': 4,
     'disks': [],
     'dst_conf': '/vm/conf',
     'dst_disks': '/vm/disk',
     'dst_host': 'hypervisors1',
     'force': False,
     'format': None,
     'interfaces': [{'conf': {'address': '255.255.255.0',
                              'gateway': '500',
                              'inet': 'static',
                              'netmask': '192.168.122.1'},
                     'kvm': {'source': '192.168.122.1', 'type': 'bridge'}}],
     'logdir': '/home/francois/dev/python-clg/examples/kvm/logs',
     'loglevel': 'info',
     'lvroot': 'root',
     'memory': 4,
     'model': 'ubuntu-trusty',
     'name': 'guest1',
     'nbd': 'nbd0',
     'no_autostart': False,
     'no_check': False,
     'no_chef': False,
     'resize': None,
     'src_disks': '/vm/disk',
     'src_host': 'bes1',
     'vgroot': 'sys'}
