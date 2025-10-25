from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.model.user import UserModel
from src.interfaces.schema.auth import SignUp
from src.core.ports.repository import RepositoryPort


class UserRepository(RepositoryPort):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = UserModel
        self.schema = SignUp

    async def get(self, _id):
        return await self.session.query(self.model, _id)

    async def create(self, user: SignUp):
        model = self.model(**user.model_dump())
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def update(self, _id, data):
        not_allowed = [
            'password',
            'secret_otp',
            'logged_in',
            'blocked',
            'attempts',
            'last_login',
            'created_at',
            'updated_at',
        ]
        model = await self.session.get(self.model, _id)
        for k, v in data.model_dump().items():
            if k in not_allowed:
                continue

        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def find(self, data):
        data = await self.session.execute(
            select(self.model).where(
                or_(
                    self.model.email == data.email,
                    self.model.username == data.username,
                )
            )
        )
        return data.scalars().all()
