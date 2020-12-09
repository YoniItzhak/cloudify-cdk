from cloudify_cdk import nodes, aws


class EC2Instance(aws.Aws):
    def __init__(self):
        super().__init__(
            region_name='eu-west-1',
            access_key_id={'get_secret': 'aws_access_key_id'},
            secret_access_key={'get_secret': 'aws_secret_access_key'}
        )

        agent_key = nodes.RSAKey('agent_key')
        instance = aws.VM('vm',
                          self.client_config,
                          agent_key=agent_key.get_attr('private_key_export'))

        self.node_templates = [instance, agent_key]


def main():
    EC2Instance().synth('/home/yoniitzhak/Desktop/test_aws.yaml')


if __name__ == '__main__':
    main()
