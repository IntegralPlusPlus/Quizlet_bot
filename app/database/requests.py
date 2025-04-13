from sqlalchemy import select, delete
from app.database.models import async_session
from app.database.models import User, Module, Word

async def set_user(user_id, _username):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id, User.username == _username))

        if user is None:
            session.add(User(tg_id = user_id, username = _username))
            await session.commit()

async def set_module(user_id, module_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        
        if user is None:
            user = User(tg_id=user_id)
            session.add(user)
            await session.commit()
            await session.refresh(user) 

        module = await session.scalar(
            select(Module).where(Module.name == module_name, Module.user_id == user.id)
        )

        if module is None:
            session.add(Module(name=module_name, user_id=user.id))
            await session.commit()

async def get_modules(user_id):
    async with async_session() as session:
        modules = await session.scalars(select(Module.name).where(Module.user_id == user_id))

        return modules.all()

async def set_word(_user_id, _module_name, _word, _translation):
    async with async_session() as session:
        _module_id = await session.scalar(select(Module.id).where(Module.user_id == _user_id,
                                                                  Module.name == _module_name))

        if _module_id is not None:
            new_word = await session.scalar(select(Word).where(Word.word == _word, 
                                                           Word.translation == _translation, 
                                                           Word.module_id == _module_id))

            if new_word is None:
                session.add(Word(word = _word, translation = _translation, module_id = _module_id))
                await session.commit()

async def get_words(_user_id, _module_name):
    async with async_session() as session:
        _module_id = await session.scalar(select(Module.id).where(Module.user_id == _user_id, 
                                                                  Module.name == _module_name))

        if _module_id is not None:
            words = await session.execute(select(Word.word, Word.translation).where(Word.module_id == _module_id))

            return words.all()

async def delete_module(_user_id, _module_name):
    async with async_session() as session:
        module = await session.scalar(select(Module).where(Module.user_id == _user_id, 
                                                           Module.name == _module_name))

        if module is not None:
            await session.execute(delete(Word).where(Word.module_id == module.id))
            await session.delete(module)
            
            await session.commit()

async def delete_word(_user_id, _module_name, _word, _translation):
    async with async_session() as session:
        _module_id = await session.scalar(select(Module.id).where(Module.user_id == _user_id, 
                                                                  Module.name == _module_name))

        if _module_id is not None:
            word = await session.scalar(select(Word).where(Word.word == _word, 
                                                          Word.translation == _translation, 
                                                          Word.module_id == _module_id))

            if word is not None:
                await session.delete(word)
                await session.commit()