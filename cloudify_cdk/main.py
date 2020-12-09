from cloudify_cdk.functions import get_secret
from cloudify_cdk import nodes, aws


class EC2Instance(aws.Aws):
    def __init__(self):
        super().__init__(
            region_name='eu-west-1',
            access_key_id=get_secret('aws_access_key_id'),
            secret_access_key=get_secret('aws_secret_access_key')
        )

        agent_user = 'centos'
        agent_key = nodes.RSAKey('agent_key')

        instance = aws.VM('vm',
                          self.client_config,
                          agent_user=agent_user,
                          agent_key=agent_key.get_attr('private_key_export'))

        vpc = aws.Vpc('vpc', self.client_config, 'vpc-0235ea2ac078b0c40')

        subnet = aws.Subnet('subnet',
                            self.client_config,
                            'subnet-0d8d2ba78d7cab57c')

        elastic_ip = aws.ElasticIP('floating_ip', self.client_config)

        security_group = aws.SecurityGroup('security_group',
                                           self.client_config,
                                           'sg-0571e4ce821463913',
                                           'igr-tests',
                                           'igr-tests')

        nic = aws.NIC('nic',
                      self.client_config,
                      subnet_id=subnet.get_attr('aws_resource_id'),
                      groups=[security_group.get_attr('aws_resource_id')])

        cloud_init = nodes.CloudInit(
            'cloud_init',
            agent_user=agent_user,
            ssh_authorized_keys=[agent_key.get_attr('private_key_export')]
        )

        self.node_templates = [instance,
                               agent_key,
                               vpc,
                               subnet,
                               elastic_ip,
                               security_group,
                               nic,
                               cloud_init]


def main():
    EC2Instance().synth('/home/yoniitzhak/Desktop/test_aws.yaml')


if __name__ == '__main__':
    main()
