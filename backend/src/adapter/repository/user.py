from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.ports.repository import RepositoryPort
from src.infra.database.model.user import UserModel
from src.interfaces.schema.auth import SignUp


class UserRepository(RepositoryPort):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = UserModel
        self.schema = SignUp

    async def get(self, _id):
        data = await self.session.execute(
            select(self.model).where(self.model.id == _id)
        )
        return data.scalars().first()

    async def create(self, user: SignUp):
        model = self.model(**user.model_dump())
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def update(self, _id, data: dict | BaseModel):
        if isinstance(data, BaseModel):
            data = data.model_dump()

        not_allowed = [
            'created_at',
            'updated_at',
        ]

        model = await self.get(_id)

        for k, v in data.items():
            if k in not_allowed:
                continue
            setattr(model, k, v)

        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def find(self, data):
        data = await self.session.execute(
            select(self.model).where(
                or_(
                    self.model.email == data.username,
                    self.model.username == data.username,
                )
            )
        )
        return data.scalars().all()
