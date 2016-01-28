#!/usr/bin/env python
# encoding: utf-8
from sys import argv
from vnc_api import vnc_api

_, TENANT, IP = argv

def main():
    vnc_lib = vnc_api.VncApi(api_server_host=IP, username='admin', password='contrail123', tenant_name=TENANT)
    sg = vnc_lib.security_group_read(fq_name=['default-domain', TENANT, 'default'])
    entries = sg.get_security_group_entries()
    rules = entries.get_policy_rule()
    funcs = ['get_dst_addresses()', 'get_src_addresses()']
    for i in rules:
        for func in funcs:
            obj = eval('i.' + func)[0]
            if obj.get_security_group() == 'default-domain:{}:default'.format(TENANT):
                obj.set_security_group(None)
                if i.get_ethertype() == 'IPv4':
                    obj.set_subnet(vnc_api.SubnetType('0.0.0.0', 0))
                else: obj.set_subnet(vnc_api.SubnetType('::', 0))
    sg._pending_field_updates.add('security_group_entries')
    vnc_lib.security_group_update(sg)

if __name__ == '__main__':
    main()
