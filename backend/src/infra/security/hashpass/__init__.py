from bcrypt import checkpw, gensalt, hashpw


class HashPassManager:
    @staticmethod
    def hash(password: str) -> str:
        """Gera um hash de senha."""
        return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        """Verifica se a senha é válida."""
        return checkpw(
            password.encode('utf-8'), hashed_password.encode('utf-8')
        )


hash_pass_manager = HashPassManager()


if __name__ == '__main__':
    password = 'S3nhaF0rte21@#*'
    hashed_password = hash_pass_manager.hash(password)
    print('Hashed password:', hashed_password)
    print(
        'Password is valid:',
        hash_pass_manager.verify(password, hashed_password),
    )
