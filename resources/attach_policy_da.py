from heat.common import exception
from heat.engine.resources.neutron import neutron
from heat.engine import properties

from neutronclient.common.exceptions import NeutronClientException
from neutronclient.neutron import v2_0 as neutronV20
from heat.openstack.common import log as logging

logger = logging.getLogger(__name__)


class AttachPolicyDA(neutron.NeutronResource):

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
        if not ":" in self.properties.get(self.NETWORK):
            network = self.properties.get(self.NETWORK)
        else:
            network = self.properties.get(self.NETWORK).split(":")[2]
        network_id = neutronV20.find_resourceid_by_name_or_id(
            self.neutron(), 'network', network)
        policies = self.neutron().show_network(network_id).get('network').get('contrail:policys')
        if not policies:
            policies = []
        policy = ['default-domain', self.properties.get(self.TENANT), self.properties.get(self.POLICY)]
        #policies.append(self.properties.get(self.POLICY).split(':')) <<<< original from OS::Contrail::AttachPolicy
        policies.append(policy)
        self.neutron().update_network(network_id, {'network':
                                     {'contrail:policys': policies}})
        self.resource_id_set(
            '%s|%s' % (network_id, self.properties.get(self.POLICY)))

    def handle_delete(self):
        #TODO 
        # delete attached policy from a vn, no clue how to do it at the moment
        if not self.resource_id:
            return
        (network_id, policy) = self.resource_id.split('|')
        try:
            policies = self.neutron().show_network(
                network_id).get('network').get('contrail:policys', [])
            try:
                policies.remove(policy.split(':'))
            except ValueError:
                return
            self.neutron().update_network(network_id, {'network':
                                         {'contrail:policys': policies}})
        except NeutronClientException as ex:
            if ex.status_code != 404:
                raise ex


def resource_mapping():
    return {
        'OS::Contrail::AttachPolicyDA': AttachPolicyDA,
    }
