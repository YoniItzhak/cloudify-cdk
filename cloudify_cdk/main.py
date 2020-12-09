from aws.aws import AwsStack, Ec2Instance


class EC2InstanceStack(AwsStack):
    def __init__(self):
        super().__init__()
        self.vm = Ec2Instance(self.client_config)


def main():
    EC2InstanceStack().synth('/home/yoniitzhak/Desktop/test_aws.yaml')


if __name__ == '__main__':
    main()
