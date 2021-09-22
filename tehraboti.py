from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text, CommandStart
import config


bot = Bot(token=config.BOT_TOKEN,)
dp = Dispatcher(bot, storage=MemoryStorage())


# Приветствие
@dp.message_handler(CommandStart())
async def startup(message: types.Message):
    chat_id = message.from_user.id
    await message.answer(text='🔧 Проводятся тех.работы 🔧')


# обработка кнопок
@dp.message_handler(content_types="text")
async def buttons(message: types.Message):
    if message:
        await message.answer(text='🔧 Проводятся тех.работы 🔧')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
