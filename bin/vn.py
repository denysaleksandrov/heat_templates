#!/usr/bin/env python
# encoding: utf-8
'''
Create/Delete/Update VirtualNetworks using heat template.
Note: update functionality is not there yet.
'''

import os
import sys
import time
import argparse
from subprocess import Popen, PIPE 

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter
                                )
parser.add_argument('tenant', type=str, metavar='TENANT')
parser.add_argument('name', type=str, metavar='NAME')
subparsers = parser.add_subparsers(help='sub-command help')

create = subparsers.add_parser('create', help='create help')
create.set_defaults(which='create')
create.add_argument('-s', '--shared', dest='shared', action='store_true')
create.add_argument('-e', '--external', dest='external', action='store_true')
create.add_argument('-ex', '--extend', dest='net_extend',
                    action='store', type=str)
create.add_argument('-fm', '--forwarding-mode', dest='forwarding_mode',
                    action='store', type=str)
create.add_argument('-at', '--allow-transit', dest='allow_transit',
                    action='store_true')
create.add_argument('-fu', '--forward-unknown', dest='forward_unknown',
                    action='store_true')
create.add_argument('-p', '--prefix', dest='ip_prefix', action='store', type=str)
create.add_argument('-gw', '--default-gateway', dest='default_gateway', 
                    action='store', type=str)
create.add_argument('-dh', '--dhcp', dest='dhcp', action='store_true')
create.add_argument('-dn', '--dns', dest='dns_nameservers', action='store',
                    type=str)
create.add_argument('-afs', '--addr-from-start', dest='addr_from_start', 
                    action='store_true')
create.add_argument('-rt', '--route-targets', dest='route_targets',
                    action='store', type=str)
create.add_argument('-nps', '--net-pool-start', dest='net_pool_start',
                    action='store', type=str)
create.add_argument('-npe', '--net-pool-end', dest='net_pool_end',
                    action='store', type=str)

delete = subparsers.add_parser('delete', help='delete help')
delete.set_defaults(which='delete')
delete.add_argument('-sn', '--stack_name', dest='stack_name')

update = subparsers.add_parser('update', help='update help')
update.set_defaults(which='update')
update.add_argument('-sn', '--stack_name', dest='stack_name')
#TODO: update 


args = parser.parse_args()
if args.which == 'delete':
    stack_name = args.stack_name if args.stack_name else args.tenant + '-' + args.name 
    pipe = Popen(['heat', '--os-tenant-name', args.tenant, 'stack-delete',
        stack_name], stdout=PIPE)
    print pipe.stdout.read()

elif args.which == 'create':
    if (args.net_pool_end and not args.net_pool_start) or \
        (args.net_pool_start and not args.net_pool_end):
        print 'ValueError: If one of the net pool properties is specified the \
other one must be as well.'
        sys.exit(1)
    items = ["{}={}".format(k,v) 
             for k,v in args.__dict__.iteritems() 
                 if k not in ['tenant', 'name', 'which'] and 
                    v not in [False, None]]
    if args.net_pool_end and args.net_pool_start:
        pipe = Popen(['heat', '--os-tenant-name', args.tenant, 'stack-create',
                     args.tenant + '-' + args.name, '-f',
                     '{}/vn_create_with_pool.yaml'.format(os.getenv('TMPLT_DIR')), 
                     '-P', 'net_name={};{}'.format(args.name, ';'.join(items))],
                     stdout=PIPE)
    else:
        pipe = Popen(['heat', '--os-tenant-name', args.tenant, 'stack-create',
                     args.tenant + '-' + args.name, '-f',
                     '{}/vn_create.yaml'.format(os.getenv('TMPLT_DIR')), 
                     '-P', 'net_name={};{}'.format(args.name, ';'.join(items))],
                     stdout=PIPE)

    print pipe.stdout.read()
    time.sleep(5)
    pipe = Popen(['slist', args.tenant], stdout=PIPE)
    output = pipe.stdout.readlines()
    if "CREATE_FAILED" in output[-2]:
        print '--------------------'
        print 'CREATE_FAILED'
        print '--------------------'
        pipe = Popen(['heat', '--os-tenant-name', args.tenant, 'stack-show',
            args.tenant + '-' + args.name], stdout=PIPE)
        print pipe.stdout.read()
