from ..cloud_provider import CloudProvider


class Aws(CloudProvider):
    def __init__(self,
                 plugin_version=None,
                 region_name='eu-west-1',
                 availability_zone=None,
                 access_key_id=None,
                 secret_access_key=None,
                 description=None):
        super(CloudProvider, self).__init__()


class Ec2Instance(object):
    def __init__(self,
                 ):