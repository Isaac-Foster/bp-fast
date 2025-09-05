class WeakPasswordError(Exception):
    def __init__(self, password, message: str = 'Senha é muito fraca'):
        self.message = message
        super().__init__(self.message)
