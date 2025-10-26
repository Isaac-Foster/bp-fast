"""
Helpers para operações comuns de banco de dados
Facilita commit + refresh e outras operações frequentes
"""

from sqlalchemy.ext.asyncio import AsyncSession


async def save_and_refresh(session: AsyncSession, *objects) -> None:
    """
    Faz commit e refresh de um ou mais objetos
    Args:
        session: Sessão do SQLAlchemy
        *objects: Objetos para fazer commit e refresh
    """
    for obj in objects:
        session.add(obj)

    await session.commit()

    for obj in objects:
        await session.refresh(obj)


async def update_and_save(session: AsyncSession, obj, **kwargs) -> None:
    """
    Atualiza atributos de um objeto e salva
    Args:
        session: Sessão do SQLAlchemy
        obj: Objeto a ser atualizado
        **kwargs: Atributos para atualizar
    """
    for key, value in kwargs.items():
        if hasattr(obj, key):
            setattr(obj, key, value)

    await save_and_refresh(session, obj)
