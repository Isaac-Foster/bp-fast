import bcrypt


class HashManager:
    @classmethod
    def hash(cls, user) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(user.password.encode('utf-8'), salt)
        return hashed.decode('utf8')

    @classmethod
    def check(cls, passwd: str, passwd_hash: str) -> bool:
        return bcrypt.checkpw(
            passwd.encode('utf8'), passwd_hash.encode('utf8')
        )


hash_manager = HashManager()
