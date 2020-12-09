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

    def get_template(self):
        templates_env = Environment(
            loader=FileSystemLoader(
                pkg_resources.resource_filename('cloudify_cdk', 'schemas')))

        return templates_env.get_template('aws_base.yaml')

    def _prepare_node_templates(self):
        node_templates_dict = {}
        for node_temp in self.node_templates:
            node_templates_dict[node_temp.name] = node_temp.to_dict()

        return node_templates_dict

    def synth(self, output_path):
        rendered_data = self.get_template().render(
            client_config=self.client_config,
            node_templates=self._prepare_node_templates(),
        )
        with open(output_path, 'w') as blueprint:
            blueprint.write(rendered_data)


class VM(NodeTemplate):
    def __init__(self,
                 name,
                 client_config,
                 agent_install_method=None,
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
             'target': 'cloud_init'},
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
