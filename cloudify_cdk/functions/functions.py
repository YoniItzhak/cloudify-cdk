class Function(object):
    def __init__(self):
        pass

    def get_function(self):
        raise NotImplementedError()


class GetSecret(Function):
    def __init__(self, secret_name):
        super(GetSecret, self).__init__()
        self.secret_name = secret_name

    def get_function(self):
        return f"{ 'get_secret': {self.secret_name} }"
