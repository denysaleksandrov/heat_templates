#!/usr/bin/env python
# encoding: utf-8
'''
Clean up all stack in the provided project/tenant
'''
from __future__ import print_function
import os
import sys
import time
from heatclient.client import Client as Heat_Client
from keystoneclient.v2_0 import Client as Keystone_Client

USERNAME = os.getenv('OS_USERNAME')
PASSWORD = os.getenv('OS_PASSWORD')
AUTH_URL = os.getenv('OS_AUTH_URL')
TENANT = os.getenv('OS_TENANT_NAME') 
if not USERNAME or not PASSWORD or not AUTH_URL or not TENANT:
    print('Environment varaibles are not set. ' +
          'Please use ". setup_env TENANT-NAME" from the root ' +
          'folder of heat templates.')
    sys.exit(1)

class Unbuffered:
    '''
    Class for unbuffering stdout
    '''
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)

def delete_stack(heatclient, stack):
    heatclient.stacks.delete(stack.id)
    while stack.stack_status != 'DELETE_COMPLETE':
        print('Deleting stack "{}", id "{}"'.format(stack.stack_name, stack.id), end='\r')
        stack = heatclient.stacks.get(stack.id)
        if stack.stack_status == 'DELETE_FAILED':
            print('Delete failed stack "{}"'.format(stack.stack_name) +
                      '                                                     ')
            break

def clean():
    ks_client = Keystone_Client(**{'username':USERNAME, 
                                   'password':PASSWORD,
                                   'auth_url':AUTH_URL, 
                                   'tenant_name':TENANT})
    heat_endpoint = ks_client.service_catalog.url_for(**{
        'service_type':'orchestration',
        'endpoint_type':'publicURL'})
    heatclient = Heat_Client('1', heat_endpoint, token=ks_client.auth_token)
    for stack in heatclient.stacks.list():
        delete_stack(heatclient, stack)

    print('Done. Check "slist {}".'.format(TENANT) + 
          '                                                                  ')

if __name__ == '__main__':
    sys.stdout = Unbuffered(sys.stdout)
    clean()
