from src.core.ports.repository import RepositoryPort
from src.infra.model.user import UserModel
from src.interfaces.schema.auth import UserSchema
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(RepositoryPort):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = UserModel
        self.schema = UserSchema
