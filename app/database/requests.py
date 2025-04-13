from sqlalchemy import select, delete
from app.database.models import async_session
from app.database.models import User, Module, Word


async def set_user(tg_id, username):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user is None:
            session.add(User(tg_id=tg_id, username=username))
            await session.commit()


async def set_module(tg_id, module_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user is None:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        module = await session.scalar(
            select(Module).where(Module.name == module_name, Module.user_id == user.id)
        )

        if module is None:
            session.add(Module(name=module_name, user_id=user.id))
            await session.commit()


async def get_modules(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return []

        modules = await session.scalars(select(Module.name).where(Module.user_id == user.id))
        return modules.all()


async def set_word(tg_id, module_name, word, translation):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return

        module_id = await session.scalar(
            select(Module.id).where(Module.user_id == user.id, Module.name == module_name)
        )

        if module_id is not None:
            new_word = await session.scalar(
                select(Word).where(
                    Word.word == word,
                    Word.translation == translation,
                    Word.module_id == module_id
                )
            )

            if new_word is None:
                session.add(Word(word=word, translation=translation, module_id=module_id))
                await session.commit()


async def get_words(tg_id, module_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return []

        module_id = await session.scalar(
            select(Module.id).where(Module.user_id == user.id, Module.name == module_name)
        )

        if module_id is not None:
            result = await session.execute(
                select(Word.word, Word.translation).where(Word.module_id == module_id)
            )
            return result.all()
        return []


async def delete_module(tg_id, module_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return

        module = await session.scalar(
            select(Module).where(Module.user_id == user.id, Module.name == module_name)
        )

        if module:
            await session.execute(delete(Word).where(Word.module_id == module.id))
            await session.delete(module)
            await session.commit()


async def delete_word(tg_id, module_name, word, translation):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return

        module_id = await session.scalar(
            select(Module.id).where(Module.user_id == user.id, Module.name == module_name)
        )

        if module_id is not None:
            word_obj = await session.scalar(
                select(Word).where(
                    Word.word == word,
                    Word.translation == translation,
                    Word.module_id == module_id
                )
            )

            if word_obj:
                await session.delete(word_obj)
                await session.commit()
