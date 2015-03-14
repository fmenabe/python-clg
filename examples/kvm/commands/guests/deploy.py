# -*- coding: utf-8 -*-

import sys

"""Command for deploying a new guest."""

SELF = sys.modules[__name__]
first_interface = True
def InterfaceType(value):
    """Custom type for '--interfaces' option with a ugly hack for knowing
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
    print(vars(args))
