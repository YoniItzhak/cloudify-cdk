import cfy_cdk.nodes as nodes
import cfy_cdk.aws as aws
from cfy_cdk.functions import get_secret
from cfy_cdk.capabilities import Capability


class EC2Instance(aws.Aws):
    def __init__(self):
        super(EC2Instance, self).__init__(
            region_name='eu-west-1',
            access_key_id=get_secret('aws_access_key_id'),
            secret_access_key=get_secret('aws_secret_access_key')
        )

        agent_user = 'centos'
        agent_key = nodes.RSAKey('agent_key',
                                 key_name='agent_key')

        instance = aws.VM('vm',
                          client_config=self.client_config,
                          agent_user=agent_user,
                          agent_key=agent_key.get_attr('private_key_export'))

        vpc = aws.Vpc('vpc',
                      client_config=self.client_config,
                      vpc_id='vpc-0235ea2ac078b0c40')

        subnet = aws.Subnet('subnet',
                            client_config=self.client_config,
                            subnet_id='subnet-0d8d2ba78d7cab57c')

        floating_ip = aws.ElasticIP('floating_ip',
                                    client_config=self.client_config)

        security_group = aws.SecurityGroup('security_group',
                                           client_config=self.client_config,
                                           security_group_id='sg-0571e4ce821463913',
                                           security_group_name='igr-tests',
                                           security_group_description='igr-tests')

        nic = aws.NIC('nic',
                      client_config=self.client_config,
                      subnet_id=subnet.get_attr('aws_resource_id'),
                      groups=[security_group.get_attr('aws_resource_id')])

        cloud_init = nodes.CloudInit('cloud_init',
                                     agent_user=agent_user,
                                     ssh_authorized_keys=[agent_key.get_attr('private_key_export')])

        self.node_templates = [instance, agent_key, vpc, subnet, floating_ip,
                               security_group, nic, cloud_init]

        self.capabilities = [
            Capability('endpoint',
                       value=floating_ip.get_attr('aws_resource_id'),
                       description='The external endpoint of the application'),
            Capability('user',
                       value=agent_user,
                       description='User ID'),
            Capability('key_content',
                       value=agent_key.get_attr('private_key_export'),
                       description='Private agent key')
        ]


EC2Instance().synth()
