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
only two commands for deploying or migrating guests. For each of theses
commands, it is possible to deploy/migrate one guest or to use a YAML file which
allow to deploy/migrate multiple guests successively. For example, for deploying
a new guest, we need the name of the guest (``--name``), the hypervisor on
which it will be deploy (``--dst-host``), the model on which it is based
(``--model``) and the network configuration (``--interfaces``). In per guest
deployment, all theses parameters must be in the command-line. When using a YAML
file (``--file``), the name and the network configuration must absolutely be
defined in the deployment file. Others parameters will be retrieved from the
command-line if they are not defined in the file.

To summarize, ``--name`` and ``--file`` options can't be used at the same time.
If ``--name`` is used, ``--dst-host``, ``--model``, ``--interfaces`` options
must be in the command-line. If ``--file`` is used, ``--interfaces`` option must
no be in the command-line but ``--dst-host`` and ``--model`` options may be in
the command. There also are many options which are rarely used because they are
optionals or have default values.

Each command use an external module for implemented the logic. A *main*
function, taking the command-line Namespace as argument, has been implemented.
For the example, theses functions will only pprint the command-line arguments.

*Directory structure*:

.. code:: bash

    .
    ├── commands
    │   ├── deploy.py
    │   ├── __init__.py
    │   └── migrate.py
    ├── kvm.py
    └── kvm.yml

*commands/deploy.py*

.. code-block:: python

    from pprint import pprint

    def main(args):
        pprint(vars(args))

*Configuration file*:

.. code-block:: yaml

    subparsers:
        deploy:
            description: Deploy new KVM guests from a model.

            usage: |
                {
                    -n NAME -d DEST -t MODEL
                    -i IP,NETMASK,GATEWAY,VLAN [IP2,NETMASK2,VLAN2 ...]
                } | { -f YAML_FILE [-d DEST] [-t model] }
                [-c CORES] [-m MEMORY] [--resize SIZE] [--format FORMAT]
                [--disks SUFFIX1,SIZE1 [SUFFIX2,SIZE2 ...]]
                [--force] [--no_check] [--nbd DEV] [--no-autostart]
                [--vgroot VGROOT] [--lvroot LVROOT]
                [--src-host HOST] [--src-conf PATH] [--src-disks PATH]
                [--dst-conf PATH] [--dst-disks PATH]

            execute:
                module: commands.deploy

            exclusive_groups:
                -
                    required: True
                    options:
                        - name
                        - file

            options:
                name:
                    short: n
                    help: "Name of the VM to deploy (default: __DEFAULT__)."
                    need:
                        - dst_host
                        - interfaces
                        - model
                dst_host:
                    short: d
                    help: "Host on which deploy the new VM."
                interfaces:
                    short: i
                    nargs: "*"
                    help: >
                        Network interfaces separated by spaces. Parameters of
                        each interfaces are separated by commas. The first interface
                        has four parameters: IP address, netmask, gateway and VLAN.
                        The others interfaces have the same parameters except the
                        gateway.
                model:
                    short: t
                    help: "Model on which the new VM is based."
                    choices:
                        - redhat5.8
                        - redhat6.3
                        - centos5
                        - ubuntu-lucid
                        - ubuntu-natty
                        - ubuntu-oneiric
                        - ubuntu-precise
                        - w2003
                        - w2008-r2
                file:
                    short: f
                    help: >
                        YAML File for deploying many hosts. Required parameters
                        on the file are the name and the network configuration.
                        The others parameters are retrieving from the command line (or
                        default values). However, destination and model have
                        no defaults values and must be defined somewhere!
                    conflict:
                        - interfaces
                ...

        migrate:
            description: Hot migrate a KVM guests from an hypervisor to another.
            usage: |
                { -n NAME -s SRC_HOST -d DST_HOST }
                | { -f YAML_FILE [-s SRC_HOST] [-d DST_HOST] }
                [--no-check] [--no-pc-check] [--remove] [--force]

            execute:
                module: commands.migrate

            options:
                name:
                    short: n
                    help: Name of the VM to migrate.
                    need:
                        - src_host
                        - dst_host
                    conflict:
                        - file
                src_host:
                    short: s
                    help: Host on which the VM is actually running.
                dst_host:
                    short: d
                    help: "Host on which migrating the VM."
                file:
                    short: f
                    help: >
                        YAML File for migrating many hosts. Only the name is require in the
                        file and the other parameters are retrieving from the command line.
                        However, in all case, source and destination hosts must be defined!
                ...

*Executions*:
    .. code-block:: bash

        # python prog.py
        usage: prog.py [-h] {deploy,migrate} ...
        prog.py: error: too few arguments

        # python vm.py deploy --help
        usage: vm.py deploy
                 {
                     -n NAME -d DEST -t MODEL
                     -i IP,NETMASK,GATEWAY,VLAN [IP2,NETMASK2,VLAN2 ...]
                 } | { -f YAML_FILE [-d DEST] [-t model] }
                 [-c CORES] [-m MEMORY] [--resize SIZE] [--format FORMAT]
                 [--disks SUFFIX1,SIZE1 [SUFFIX2,SIZE2 ...]]
                 [--force] [--no_check] [--nbd DEV] [--no-autostart]
                 [--vgroot VGROOT] [--lvroot LVROOT]
                 [--src-host HOST] [--src-conf PATH] [--src-disks PATH]
                 [--dst-conf PATH] [--dst-disks PATH]

        optional arguments:
          -h, --help            show this help message and exit
          -n NAME, --name NAME  Name of the VM to deploy.
          -f FILE, --file FILE  YAML File for deploying many hosts. Required
                                parameters on the file are the name and the network
                                configuration. The others parameters are retrieving
                                from the command line (or default values). However,
                                destination and model have no defaults values and must
                                be defined somewhere!
          -d DST_HOST, --dst-host DST_HOST
                                Host on which deploy the new VM.
          -i [INTERFACES [INTERFACES ...]], --interfaces [INTERFACES [INTERFACES ...]]
                                Network interfaces separated by spaces. Parameters of
                                each interfaces are separated by commas. The first
                                interface has four parameters: IP address, netmask,
                                gateway and VLAN. The others interfaces have the same
                                parameters except the gateway.
          -t {redhat5.8,redhat6.3,centos5,ubuntu-lucid,ubuntu-natty,ubuntu-oneiric,ubuntu-precise,w2003,w2008-r2}, --model {redhat5.8,redhat6.3,centos5,ubuntu-lucid,ubuntu-natty,ubuntu-oneiric,ubuntu-precise,w2003,w2008-r2}
                                Model on which the new VM is based.
          -c CORES, --cores CORES
                                Number of cores assigned to the VM (default: 2).
          -m MEMORY, --memory MEMORY
                                Memory (in Gb) assigned to the VM (default: 1).
          --format {raw,qcow2}  Format of the image(s). If format is different from
                                'qcow2', the image is converting to the specified
                                format (this could be a little long!).
          --resize RESIZE       Resize (in fact, only increase) the main disk image
                                and, for linux system, allocate the new size on the
                                root LVM Volume Group. This option only work on KVM
                                host which have a version of qemu superior to 0.??!
          --disks [DISKS [DISKS ...]]
                                Add new disk(s). Parameters are a suffix and the size.
                                Filename of the created image is NAME-SUFFIX.FORMAT
                                (ex: mavm-datas.qcow2).
          --force               If a virtual machine already exists on destination
                                host, configuration and disk images are automaticaly
                                backuped then overwrited!
          --no-check            Ignore checking of resources (Use with cautions!).
          --no-autostart        Don't set autostart of the VM.
          --nbd NBD             NBD device to use (default: '/dev/nbd0').
          --vgroot VGROOT       Name of the LVM root Volume Group (default: 'sys').
          --lvroot LVROOT       Name of the LVM root Logical Volume (default: 'root')
          --src-host SRC_HOST   Host on which models are stored (default: 'bes1')
          --src-conf SRC_CONF   Path of configurations files on the source host
                                (default: '/vm/conf').
          --src-disks SRC_DISKS
                                Path of images files on the source host (default:
                                '/vm/disk').
          --dst-conf DST_CONF   Path of configurations files on the destination host
                                (default: '/vm/conf').
          --dst-disks DST_DISKS
                                Path of disks files on the destination host (default:
                                '/vm/disk')

        # python vm.py deploy
        usage: vm.py deploy
                 {
                     -n NAME -d DEST -t MODEL
                     -i IP,NETMASK,GATEWAY,VLAN [IP2,NETMASK2,VLAN2 ...]
                 } | { -f YAML_FILE [-d DEST] [-t model] }
                 [-c CORES] [-m MEMORY] [--resize SIZE] [--format FORMAT]
                 [--disks SUFFIX1,SIZE1 [SUFFIX2,SIZE2 ...]]
                 [--force] [--no_check] [--nbd DEV] [--no-autostart]
                 [--vgroot VGROOT] [--lvroot LVROOT]
                 [--src-host HOST] [--src-conf PATH] [--src-disks PATH]
                 [--dst-conf PATH] [--dst-disks PATH]
        vm.py deploy: error: one of the arguments -n/--name -f/--file is required

        # python vm.py deploy -n guest1
        usage: vm.py deploy
                 {
                     -n NAME -d DEST -t MODEL
                     -i IP,NETMASK,GATEWAY,VLAN [IP2,NETMASK2,VLAN2 ...]
                 } | { -f YAML_FILE [-d DEST] [-t model] }
                 [-c CORES] [-m MEMORY] [--resize SIZE] [--format FORMAT]
                 [--disks SUFFIX1,SIZE1 [SUFFIX2,SIZE2 ...]]
                 [--force] [--no_check] [--nbd DEV] [--no-autostart]
                 [--vgroot VGROOT] [--lvroot LVROOT]
                 [--src-host HOST] [--src-conf PATH] [--src-disks PATH]
                 [--dst-conf PATH] [--dst-disks PATH]
        vm.py deploy: error: argument --n/--name: need --d/--dst-host argument

        # python vm.py deploy -n guest1 -d hypervisor1 -i 192.168.122.1,255.255.255.0,192.168.122.1,500 -t test
        usage: vm.py deploy
                 {
                     -n NAME -d DEST -t MODEL
                     -i IP,NETMASK,GATEWAY,VLAN [IP2,NETMASK2,VLAN2 ...]
                 } | { -f YAML_FILE [-d DEST] [-t model] }
                 [-c CORES] [-m MEMORY] [--resize SIZE] [--format FORMAT]
                 [--disks SUFFIX1,SIZE1 [SUFFIX2,SIZE2 ...]]
                 [--force] [--no_check] [--nbd DEV] [--no-autostart]
                 [--vgroot VGROOT] [--lvroot LVROOT]
                 [--src-host HOST] [--src-conf PATH] [--src-disks PATH]
                 [--dst-conf PATH] [--dst-disks PATH]
        vm.py deploy: error: argument -t/--model: invalid choice: 'test' (choose from 'redhat5.8', 'redhat6.3', 'centos5', 'ubuntu-lucid', 'ubuntu-natty', 'ubuntu-oneiric', 'ubuntu-precise', 'w2003', 'w2008-r2')

        # python vm.py deploy -n guest1 -d hypervisor1 -i 192.168.122.2,255.255.255.0,192.168.122.1,500 -t ubuntu-precise -c 4 -m 4
        'main' function on 'deploy' module
        {'command0': 'deploy',
         'cores': 4,
         'disks': [],
         'dst_conf': '/vm/conf',
         'dst_disks': '/vm/disk',
         'dst_host': 'hypervisor1',
         'force': False,
         'format': 'qcow2',
         'interfaces': ['192.168.122.1,255.255.255.0,192.168.122.1,500'],
         'lvroot': 'root',
         'memory': 4,
         'model': 'ubuntu-precise',
         'name': 'guest1',
         'nbd': '/dev/nbd0',
         'no_autostart': True,
         'no_check': False,
         'resize': None,
         'src_conf': '/vm/conf',
         'src_disks': '/vm/disk',
         'src_host': 'bes1',
         'vgroot': 'sys'}

        # python vm.py deploy -f test.yml -n guest1
        usage: vm.py deploy
                 {
                     -n NAME -d DEST -t MODEL
                     -i IP,NETMASK,GATEWAY,VLAN [IP2,NETMASK2,VLAN2 ...]
                 } | { -f YAML_FILE [-d DEST] [-t model] }
                 [-c CORES] [-m MEMORY] [--resize SIZE] [--format FORMAT]
                 [--disks SUFFIX1,SIZE1 [SUFFIX2,SIZE2 ...]]
                 [--force] [--no_check] [--nbd DEV] [--no-autostart]
                 [--vgroot VGROOT] [--lvroot LVROOT]
                 [--src-host HOST] [--src-conf PATH] [--src-disks PATH]
                 [--dst-conf PATH] [--dst-disks PATH]
        vm.py deploy: error: argument -n/--name: not allowed with argument -f/--file

        # python vm.py deploy -f test.yml -i 192.168.122.2,255.255.255.0,192.168.122.1,500
        usage: vm.py deploy
                 {
                     -n NAME -d DEST -t MODEL
                     -i IP,NETMASK,GATEWAY,VLAN [IP2,NETMASK2,VLAN2 ...]
                 } | { -f YAML_FILE [-d DEST] [-t model] }
                 [-c CORES] [-m MEMORY] [--resize SIZE] [--format FORMAT]
                 [--disks SUFFIX1,SIZE1 [SUFFIX2,SIZE2 ...]]
                 [--force] [--no_check] [--nbd DEV] [--no-autostart]
                 [--vgroot VGROOT] [--lvroot LVROOT]
                 [--src-host HOST] [--src-conf PATH] [--src-disks PATH]
                 [--dst-conf PATH] [--dst-disks PATH]
        vm.py deploy: error: argument --f/--file: conflict with --i/--interfaces argument

        # python vm.py deploy -f test.yml -d hypervisor1
        {'command0': 'deploy',
         'cores': 2,
         'disks': [],
         'dst_conf': '/vm/conf',
         'dst_disks': '/vm/disk',
         'dst_host': 'hypervisor1',
         'file': 'test.yml',
         'force': False,
         'format': 'qcow2',
         'interfaces': None,
         'lvroot': 'root',
         'memory': 1,
         'model': None,
         'name': None,
         'nbd': '/dev/nbd0',
         'no_autostart': True,
         'no_check': False,
         'resize': None,
         'src_conf': '/vm/conf',
         'src_disks': '/vm/disk',
         'src_host': 'bes1',
         'vgroot': 'sys'}

.. A way to organize files
.. -----------------------
