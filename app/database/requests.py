from sqlalchemy import select
from app.database.models import async_session
from app.database.models import User, Module, Word

async def set_user(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))

        if user is None:
            session.add(User(tg_id = user_id))
            await session.commit()

async def set_module(user_id, module_name):
    async with async_session() as session:
        module = await session.scalar(select(Module).where(Module.name == module_name, Module.user_id == user_id))
        
        if module is None:
            session.add(Module(name = module_name, user_id = user_id))
            await session.commit()