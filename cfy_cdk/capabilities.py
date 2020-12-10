class Capability(object):
    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description

    def to_dict(self):
        return {
            'description': self.description,
            'value': self.value
        }
