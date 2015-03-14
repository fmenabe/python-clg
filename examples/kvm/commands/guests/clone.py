# -*- coding: utf-8 -*-

import sys


SELF = sys.modules[__name__]
def InterfaceType(value):
    """Custom type for '--interfaces' option with a (ugly) hack for knowing
    whether this is the first interface."""
    interface = {'mac': kvm.gen_mac(), 'driver': 'virtio'}
    SELF.first_interface = True
    if SELF.first_interface:
        address, netmask, gateway, vlan = value.split(',')
        SELF.first_interface = False
        return dict(address=address,
                    netmask=netmask,
                    gateway=gateway,
                    vlan=vlan,
                    **interface)
    else:
        address, netmask, vlan = value.split(',')
        return dict(address=address,
                    netmask=netmask,
                    vlan=vlan,
                    **interface)

def URIType(value):
    guest, hypervisor = value.split('@')
    return {'guest': guest, 'hypervisor': hypervisor}


def main(args):
    print(vars(args))
