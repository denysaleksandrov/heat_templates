#!/usr/bin/env python
# encoding: utf-8
'''
Create/Delete/Update policy using heat template.
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
parser.add_argument('pname', type=str, metavar='POLICY')
subparsers = parser.add_subparsers(help='sub-command help')

create = subparsers.add_parser('create', help='create help')
create.set_defaults(which='create')
create.add_argument('-di', '--direction', dest='direction', action='store',
                    type=str)
create.add_argument('-ssp', '--start-src-port', dest='start_src_port',
                    action='store', type=str)
create.add_argument('-esp', '--end-src-port', dest='end_src_port',
                    action='store', type=str)
create.add_argument('-sdp', '--start-dst-port', dest='start_dst_port',
                    action='store', type=str)
create.add_argument('-edp', '--end-dst-port', dest='end_dst_port',
                    action='store', type=str)
create.add_argument('-a', '--action', dest='action', action='store',
                    type=str)
create.add_argument('-p', '--protocol', dest='protocol', action='store',
                    type=str)
create.add_argument('-vn1', '--virtual_network1', dest='vn1',
                    action='store', type=str)
create.add_argument('-vn2', '--virtual_network2', dest='vn2',
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
    stack_name = args.stack_name if args.stack_name else args.tenant + '-' + args.pname 
    pipe = Popen(['heat', '--os-tenant-name', args.tenant, 'stack-delete',
        stack_name], stdout=PIPE)
    print pipe.stdout.read()

elif args.which == 'create':
    if args.direction and args.direction not in ['>', '<>']:
        print 'Direction allowed values are ">" and "<>".'
        sys.exit(1)
    if (args.vn1 and not args.vn2) or  \
       (args.vn2 and not args.vn1):
        print 'ValueError: If you provide one network please provide another one as well'
        sys.exit(1)
    if args.protocol and args.protocol not in ['any', 'tcp', 'udp', 'icmp']:
        print 'ValueError: {} protocol is not allowed'.format(args.protocol)
        sys.exit(1)
    items = ["{}={}".format(k,v) 
             for k,v in args.__dict__.iteritems() 
                 if k not in ['tenant', 'pname', 'which'] and v != None]
    if items != []:
        pipe = Popen(['heat', '--os-tenant-name', args.tenant, 'stack-create',
            args.tenant + '-' + args.pname, '-f',
            '{}/policy.yaml'.format(os.getenv('TMPLT_DIR')), '-P',
            'policy_name={};{}'.format(args.pname, ';'.join(items))],
            stdout=PIPE)
    elif items == []:
        pipe = Popen(['heat', '--os-tenant-name', args.tenant, 'stack-create',
            args.tenant + '-' + args.pname, '-f',
            '{}/policy.yaml'.format(os.getenv('TMPLT_DIR')), '-P',
            'policy_name={}'.format(args.pname)], stdout=PIPE)
    print pipe.stdout.read()
    time.sleep(5)
    pipe = Popen(['slist', args.tenant], stdout=PIPE)
    output = pipe.stdout.readlines()
    if "CREATE_FAILED" in output[-2]:
        print '--------------------'
        print 'CREATE_FAILED'
        print '--------------------'
        pipe = Popen(['heat', '--os-tenant-name', args.tenant, 'stack-show',
            args.tenant + '-' + args.pname], stdout=PIPE)
        print pipe.stdout.read()
