class NodeTemplate(object):
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        raise NotImplementedError()

    def get_attr(self, attribute):
        return {'get_attribute': [self.name, attribute]}


class RSAKey(NodeTemplate):
    def __init__(self,
                 name,
                 openssh_format=True,
                 use_secret_store=True,
                 use_secrets_if_exist=True,
                 store_private_key_material=True):
        super().__init__(name)
        self.openssh_format = openssh_format
        self.use_secret_store = use_secret_store
        self.use_secrets_if_exist = use_secrets_if_exist
        self.store_private_key_material = store_private_key_material

    def to_dict(self):
        return {
            'type': 'cloudify.keys.nodes.RSAKey',
            'properties': {
                'resource_config': {
                    'key_name': self.name,
                    'openssh_format': self.openssh_format
                },
                'use_secret_store': self.use_secret_store,
                'use_secrets_if_exist': self.use_secrets_if_exist
            },
            'interfaces': {
                'cloudify.interfaces.lifecycle': {
                    'create': {
                        'implementation':
                            'keys.cloudify_ssh_key.operations.create',
                        'inputs': {
                            'store_private_key_material':
                                self.store_private_key_material
                        }
                    }
                }
            }
        }
