from heat.common import exception
from heat.engine.resources.neutron import neutron
from heat.engine import properties

from neutronclient.common.exceptions import NeutronClientException
from neutronclient.neutron import v2_0 as neutronV20
from heat.openstack.common import log as logging
from contrail_heat.resources import contrail
from vnc_api import vnc_api

logger = logging.getLogger(__name__)


class AttachPolicy(contrail.ContrailResource):

    PROPERTIES = (
        NETWORK, POLICY, TENANT,
    ) = (
        'network', 'policy', 'tenant',
    )

    properties_schema = {
        NETWORK: properties.Schema(
            properties.Schema.STRING,
            description=_('The network id or fq_name_string'),
            required=True),
        POLICY: properties.Schema(
            properties.Schema.STRING,
            description=_('policy name FQ name notation'),
            required=True),
        TENANT: properties.Schema(
            properties.Schema.STRING,
            description=_('tenant name'),
            required=True),
    }

    def handle_create(self):
        tenant = self.properties.get(self.TENANT) 
        if not ":" in self.properties.get(self.NETWORK):
            network = ['default-domain', tenant, 
                       self.properties.get(self.NETWORK)]
        else:
            network = self.properties.get(self.NETWORK).split(':')
        if not ":" in self.properties.get(self.POLICY):
            policy = ['default-domain', tenant,
                      self.properties.get(self.POLICY)]
        else:
            policy = self.properties.get(self.POLICY).split(':')
        net = self.vnc_lib().virtual_network_read(fq_name=network)
        policy = self.vnc_lib().network_policy_read(fq_name=policy)
        net.add_network_policy(policy, vnc_api.VirtualNetworkPolicyType(
                        sequence=vnc_api.SequenceType(0, 0)))
        self.vnc_lib().virtual_network_update(net)
        self.resource_id_set('%s|%s' % (net.get_uuid(), policy.get_uuid()))

    def handle_delete(self):
        if not self.resource_id:
            return
        (network_id, policy_id) = self.resource_id.split('|')
        try:
            self.vnc_lib().ref_update('virtual-network', network_id,
                                    'network-policy', policy_id, None, 'DELETE')
        except Exception as ex:
            self._ignore_not_found(ex)
            LOG.warn(_("Virtual Network %s already deleted.") % network_id)

def resource_mapping():
    return {
        'OS::Contrail::AttachPolicy': AttachPolicy,
    }
