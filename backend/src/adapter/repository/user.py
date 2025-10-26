from pydantic import BaseModel
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
