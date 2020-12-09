import pkg_resources

from jinja2 import Environment, FileSystemLoader

from cloudify_cdk.nodes import NodeTemplate


class Aws(object):
    def __init__(self,
                 region_name='eu-west-1',
                 access_key_id=None,
                 secret_access_key=None):
        self.client_config = {
            'aws_access_key_id': access_key_id,
            'aws_secret_access_key': secret_access_key,
            'region_name': region_name
        }
        self.blueprint_schema_name = 'aws_base.yaml'

        self.node_templates = []
        self.capabilities = []

    @staticmethod
    def get_template():
        templates_env = Environment(
            loader=FileSystemLoader(
                pkg_resources.resource_filename('cloudify_cdk', 'schemas')))

        return templates_env.get_template('aws_base.yaml')

    def _prepare_node_templates(self):
        node_templates_dict = {}
        for node_temp in self.node_templates:
            node_templates_dict[node_temp.name] = node_temp.to_dict()

        return node_templates_dict

    def _prepare_capabilities(self):
        capabilities_dict = {}
        for capability in self.capabilities:
            capabilities_dict[capability.name] = capability.to_dict()

        return capabilities_dict

    def synth(self, output_path):
        rendered_data = self.get_template().render(
            client_config=self.client_config,
            node_templates=self._prepare_node_templates(),
            capabilities=self._prepare_capabilities()
        )
        with open(output_path, 'w') as blueprint:
            blueprint.write(rendered_data)


class VM(NodeTemplate):
    def __init__(self,
                 name,
                 client_config,
                 agent_install_method='none',
                 agent_user='centos',
                 agent_key=None,
                 image_id='ami-082ed116ae2c6d2cc',
                 instance_type='t3.medium',
                 availability_zone='eu-west-1a',
                 user_date=None,
                 block_device_mappings=None,
                 tags=None,
                 use_public_ip=True,
                 relationships=None
                 ):
        super().__init__(name)
        self.client_config = client_config
        self.agent_install_method = agent_install_method
        self.agent_user = agent_user
        self.agent_key = agent_key
        self.image_id = image_id
        self.instance_type = instance_type
        self.availability_zone = availability_zone
        self.user_data = user_date or {
            'get_attribute': ['cloud_init', 'cloud_config']
        }

        self.block_device_mappings = block_device_mappings or [
            {'DeviceName': '/dev/xvda',
             'Ebs': {
                 'VolumeSize': 22,
                 'VolumeType': 'standard',
                 'DeleteOnTermination': True}
             }
        ]

        self.tags = tags or [{'Key': 'protected',
                              'Value': 'integration-tests'}]

        self.use_public_ip = use_public_ip

        self.bp_relationships = relationships or [
            {'type': 'cloudify.relationships.depends_on',
             'target': 'nic'},
            {'type': 'cloudify.relationships.depends_on',
             'target': 'cloud_init'}
        ]

        if use_public_ip and not relationships:
            self.bp_relationships.append(
                {'type': 'cloudify.relationships.depends_on',
                 'target': 'floating_ip'}
            )

    def to_dict(self):
        return {
            'type': 'cloudify.nodes.aws.ec2.Instances',
            'properties': {
                'client_config': self.client_config,
                'agent_config': {
                    'install_method': self.agent_install_method,
                    'user': self.agent_user,
                    'key': self.agent_key
                },
                'resource_config': {
                    'ImageId': self.image_id,
                    'InstanceType': self.instance_type,
                    'kwargs': {
                        'Placement': {
                            'AvailabilityZone': self.availability_zone
                        },
                        'UserData': self.user_data,
                        'BlockDeviceMappings': self.block_device_mappings
                    }
                },
                'Tags': self.tags,
                'use_public_ip': self.use_public_ip
            },
            'relationships': self.bp_relationships
        }


class Vpc(NodeTemplate):
    def __init__(self,
                 name,
                 client_config,
                 vpc_id,
                 cidr_block='10.20.0.0/24'):
        super().__init__(name)
        self.client_config = client_config
        self.vpc_id = vpc_id
        self.cidr_block = cidr_block

    def to_dict(self):
        return {
            'type': 'cloudify.nodes.aws.ec2.Vpc',
            'properties': {
                'client_config': self.client_config,
                'use_external_resource': True,
                'resource_id': self.vpc_id,
                'resource_config': {
                    'CidrBlock': self.cidr_block
                }
            }
        }


class Subnet(NodeTemplate):
    def __init__(self,
                 name,
                 client_config,
                 subnet_id,
                 cidr_block='10.20.0.0/24'):
        super().__init__(name)
        self.client_config = client_config
        self.subnet_id = subnet_id
        self.cidr_block = cidr_block

    def to_dict(self):
        return {
            'type': 'cloudify.nodes.aws.ec2.Subnet',
            'properties': {
                'client_config': self.client_config,
                'use_external_resource': True,
                'resource_id': self.subnet_id,
                'resource_config': {
                    'CidrBlock': self.cidr_block
                }
            },
            'relationships': [
                {'type': 'cloudify.relationships.depends_on',
                 'target': 'vpc'}
            ]
        }


class ElasticIP(NodeTemplate):
    def __init__(self,
                 name,
                 client_config):
        super().__init__(name)
        self.client_config = client_config

    def to_dict(self):
        return {
            'type': 'cloudify.nodes.aws.ec2.ElasticIP',
            'properties': {
                'client_config': self.client_config
            },
            'relationships': [
                {'type': 'cloudify.relationships.depends_on',
                 'target': 'nic'}
            ]
        }


class SecurityGroup(NodeTemplate):
    def __init__(self,
                 name,
                 client_config,
                 security_group_id,
                 security_group_name,
                 security_group_description):
        super().__init__(name)
        self.client_config = client_config
        self.security_group_id = security_group_id
        self.security_group_name = security_group_name
        self.security_group_description = security_group_description

    def to_dict(self):
        return {
            'type': 'cloudify.nodes.aws.ec2.SecurityGroup',
            'properties': {
                'client_config': self.client_config,
                'use_external_resource': True,
                'resource_id': self.security_group_id,
                'resource_config': {
                    'GroupName': self.security_group_name,
                    'Description': self.security_group_description
                }
            },
            'relationships': [
                {'type': 'cloudify.relationships.depends_on',
                 'target': 'vpc'}
            ]
        }


class NIC(NodeTemplate):
    def __init__(self,
                 name,
                 client_config,
                 subnet_id,
                 groups):
        super().__init__(name)
        self.client_config = client_config
        self.subnet_id = subnet_id
        self.groups = groups
        self.description = 'Created by cloudify-getting-started-example.'

    def to_dict(self):
        return {
            'type': 'cloudify.nodes.aws.ec2.Interface',
            'properties': {
                'client_config': self.client_config,
                'resource_config': {
                    'kwargs': {
                        'Description': self.description,
                        'SubnetId': self.subnet_id,
                        'Groups': self.groups
                    }
                }
            },
            'relationships': [
                {'type': 'cloudify.relationships.depends_on',
                 'target': 'security_group'},
                {'type': 'cloudify.relationships.depends_on',
                 'target': 'subnet'}
            ]
        }
