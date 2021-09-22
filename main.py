from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text, CommandStart
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta
import logging
import config
import os
import re
from sql import SQLUser
import keyboard


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN,)
dp = Dispatcher(bot, storage=MemoryStorage())
CHANEL_ID = '@kazinside_kz'

TEXT = """🤪 Как вы задолбали со своим накручиванием 🤪 
Читай правила 👇"""

EMODZI = '☠'


class Output(StatesGroup):
    Kaspi_number = State()
    how_much = State()


# Приветствие
@dp.message_handler(CommandStart())
async def startup(message: types.Message):
    chat_id = message.from_user.id
    date = (datetime.now() + timedelta(hours=6)).strftime("%d.%m.%Y")
    text = f'''⚡ Поздравляю, {message.from_user.first_name}

✅ Вы получаете <b>5.000 тенге (900₽)</b> бонусом

Чтобы вывести данные бонусы необходимо <b>оформить подписку</b> на этот канал 👇

✅ https://t.me/kazinside_kz

⚡'''
    if message.from_user.is_bot:
        await message.answer(text='😡 Ботам тут не место')
    # если зарегистрирован
    elif SQLUser().user_exists(chat_id):
        await message.answer(text='🔝 Главное Меню', reply_markup=keyboard.start_menu)
    # если не зареган, и зашел по реф ссылке
    elif len(message.text) > 6 and message.text[7] == 'r':
        ref_user = message.text[8:]
        if SQLUser().get_referal_to_day(date, ref_user) < 99:
            SQLUser().add_user(chat_id, message.from_user.first_name, date, ref_user)
            await message.answer(text=text, disable_web_page_preview=True, parse_mode='html',
                                 reply_markup=keyboard.verify)
        else:
            await bot.send_message(chat_id, text=f'❌ По этой ссылке сегодня уже зарегистрировалось 100 человек.'
                                                 f'\nПовторите регистрацию завтра')

    # если не зареган, и зашел без реф ссылки
    else:
        SQLUser().add_user(chat_id, message.from_user.first_name, date, ref_user=0)
        await message.answer(text=text, disable_web_page_preview=True, parse_mode='html',
                             reply_markup=keyboard.verify)


# Обработка инлайн кнопок
@dp.callback_query_handler(lambda call: call.data)
async def inline_button(call: CallbackQuery):
    data = call.data
    chat_id = call.from_user.id
    if data == 'verify':
        if check_sub_channel(await bot.get_chat_member(chat_id=CHANEL_ID, user_id=chat_id)):
            if SQLUser().user_exists(chat_id):
                ref_user = int(SQLUser().get_ref_user(chat_id))
                if ref_user != chat_id:
                    if ref_user > 0:
                        user_name = SQLUser().get_name_user(ref_user)
                        await bot.send_message(chat_id, text=f'✅ Вы были приглашены пользователем {user_name}.')
                        await bot.send_message(chat_id, text=f'🔝 Главное Меню', reply_markup=keyboard.start_menu)
                        await bot.send_message(ref_user, text=f'✅ Вы пригласили пользователя, Вам начислено 500 тенге.')
                        SQLUser().referal_update(ref_user)
                    else:
                        await bot.send_message(chat_id, text=f'✅ Вы подписаны на канал!')
                        await bot.send_message(chat_id, text=f'🔝 Главное Меню', reply_markup=keyboard.start_menu)

                else:
                    await bot.send_message(chat_id, text=f'✅ Вы подписаны на канал!')
                    await bot.send_message(chat_id, text=f'🔝 Главное Меню', reply_markup=keyboard.start_menu)
            else:
                await bot.send_message(chat_id, text=f'С вашим акаунтом чтото не так! 😱 '
                                                     f'нажмите /start')

        else:
            await bot.send_message(chat_id,
                                   text=f'Чтобы вывести данные бонусы необходимо <b>оформить подписку</b> '
                                        f'на этот канал 👇 \n✅ https://t.me/kazinside_kz \n⚡',
                                   disable_web_page_preview=True, parse_mode='html', reply_markup=keyboard.verify)

    elif data == 'Kaspi':
        name = SQLUser().get_name_user(chat_id)
        text = f"⚠ Недостаточно денег на счету для снятия" \
               f"\n\n💳  {name}, минимальный баланс для снятия должен составлять: 30.000 тенге (6.000₽)"
        if corekt_referal(chat_id):
            await bot.send_message(chat_id, EMODZI)
            await bot.send_message(chat_id, TEXT)
        elif check_money(chat_id):
            await bot.send_message(chat_id,
                                   text="💳  Укажите номер Kaspi Gold "
                                        "\n<b>+77xxxxxxxxx</b>", parse_mode='html', reply_markup=keyboard.cancel)
            await Output.Kaspi_number.set()
        else:
            await bot.answer_callback_query(call.id, f'{text}', show_alert=True)


# обработка кнопок
@dp.message_handler(content_types="text")
async def buttons(message: types.Message):
    msg = message.text
    if msg == '👨🏼‍💻 Заработать':
        foto = os.path.join(config.TEMP_DIR, "8094aba2-d20d-46ad-a7b0-f5e10de5cd1b.jpg")
        url = f'https://t.me/Kazinside_rabota_bot=r{message.chat.id}'
        user_name = SQLUser().get_name_user(message.chat.id)
        await bot.send_photo(message.chat.id, photo=open(foto, "rb"), caption=f"""Привет {user_name}
        
📍 Данный бот выплачивает деньги за приглашённого реферала (друзей) <b>которые увлекаются «Ставками на спорт»</b>

{url}

👆🏻 За каждого приглашённого человека по этой ссылке вы получаете <b>500 тенге (90₽)</b>

📩 Данную ссылку вы можете отправлять:
☑ Друзьям в личные сообщения
☑ В чаты telegram с тематикой <b>«прогнозов на спорт»</b>
☑ Писать в личные сообщения участникам чатов <b>«прогнозов на спорт»</b>

💰 Можешь начинать приглашать друзей и получать за это деньги!""", parse_mode='html')

    elif msg == '📄 Правила':
        foto = os.path.join(config.TEMP_DIR, "09f14cbb-9c6f-45d7-8dd9-1e7cbd794f53.jpg")
        await bot.send_photo(message.chat.id, photo=open(foto, "rb"), caption=f"""👨🏼‍💻 <b>Правила бота:</b>
        
1⃣ Бот не принимает / не засчитывает <b>накрученных</b> пользователей 
2⃣ Один пользователь может присоединиться <b>только один раз!</b>
3⃣ В день можно пригласить <b>не более</b> 100 людей
4⃣ Приглашать нужно только людей связанных с тематикой <b>«Прогнозов на спорт»</b>
""", parse_mode='html')

    elif msg == '💳 Мой баланс':
        if corekt_referal(message.chat.id):
            await message.answer(EMODZI)
            await message.answer(TEXT)
        else:
            user_name = SQLUser().get_name_user(message.chat.id)
            balance = SQLUser().get_balance(message.chat.id)
            foto = os.path.join(config.TEMP_DIR, "47c7a006-3159-4614-a43c-32d1510dda7a.jpg")
            bonus = SQLUser().get_bonus(message.chat.id)
            if bonus == 0:
                await bot.send_photo(message.chat.id, photo=open(foto, "rb"),
                                     caption=f"""💳 {user_name}, ваш баланс составляет: {balance} тенге
                                 
<i>📍 Ваши бонусные 5000 тенге (900₽) (за оформлении подписки) будут прибавлены при снятии денег!</i>""",
                                     parse_mode='html', reply_markup=keyboard.output_money)
            else:
                await bot.send_photo(message.chat.id, photo=open(foto, "rb"),
                                     caption=f"""💳 {user_name}, ваш баланс составляет: {balance} тенге""",
                                     parse_mode='html', reply_markup=keyboard.output_money)

    elif msg == '🔝 Главное Меню':
        await message.answer('🔝 Главное Меню', reply_markup=keyboard.start_menu)

    elif msg == '📤 Вывести':
        if corekt_referal(message.chat.id):
            await message.answer(EMODZI)
            await message.answer(TEXT)
        else:
            await message.answer('💰 Вывод денег: 👇', reply_markup=keyboard.cash)

    elif msg == '📊 Статистика':
        if corekt_referal(message.chat.id):
            await message.answer(EMODZI)
            await message.answer(TEXT)
        else:
            date = (datetime.now() + timedelta(hours=6)).strftime("%d.%m.%Y")
            foto = os.path.join(config.TEMP_DIR, "1fee3ce9-0ccc-4ca8-b493-265a43e9f8db.jpg")
            url = f'https://t.me/Kazinside_rabota_bot?start=r{message.chat.id}'
            balance = SQLUser().get_balance(message.chat.id)
            referal = int(SQLUser().get_referal(message.chat.id)[-1][-1])
            all_user = SQLUser().get_all_user()
            user_to_day = SQLUser().get_user_to_day(date)
            await bot.send_photo(message.chat.id, photo=open(foto, "rb"), caption=f"""♻ Статистика:

👨🏼‍💻 Вы пригласили <b>{referal}</b> человек
💸 Ваш баланс: <b>{balance}</b> тенге
👥 Пользователей в боте: <b>{all_user}</b>
👤 Новых за сегодня: <b>{user_to_day}</b>

💰 Ваша реферальная ссылка для приглашения: 
{url}""", parse_mode='html')

    else:
        await message.answer(f"""❌ Неизвестная команда!
        
<i>Вы отправили сообщение напрямую в чат бота, или структура меню была изменена Админом.</i>

ℹ Не отправляйте прямых сообщений боту или обновите Меню, нажав /start""", parse_mode='html')


def corekt_referal(chat_id):
    corect = SQLUser().referal_real(chat_id)
    referal = int(SQLUser().get_referal(chat_id)[-1][-1])
    SQLUser().corect(corect, chat_id)
    if referal > corect:
        return True
    else:
        return False


# Отмена, убираем все состояния
@dp.message_handler(Text(equals='🚫 Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Действие отменено', reply_markup=keyboard.start_menu)


# Получаем номер Kaspi
@dp.message_handler(content_types='text', state=Output.Kaspi_number)
async def Kaspi_handler(message: types.Message, state: FSMContext):
    Kaspi_number = message.text
    msg = re.match(r'[+77]{3}[0-9]{9}', Kaspi_number) and len(Kaspi_number) == 12
    if msg:
        money = SQLUser().get_balance(message.chat.id)
        await message.answer(f'Ваш баланс составляет <b>{money} тенге</b>'
                             f'\nУкажите количество для вывода', parse_mode='html')
        async with state.proxy() as data:
            data["Kaspi_number"] = Kaspi_number
        await Output.how_much.set()
    else:
        await message.answer("💳  Укажите номер Kaspi Gold "
                             "\n<b>+77xxxxxxxxx</b>", parse_mode='html')


# Получаем количество для вывода
@dp.message_handler(content_types='text', state=Output.how_much)
async def money_handler(message: types.Message, state: FSMContext):
    how_money = message.text
    money = SQLUser().get_balance(message.chat.id)
    msg = re.match(r'[0-9]', how_money)
    if msg:
        if int(how_money) <= money:
            user_name = SQLUser().get_name_user(message.chat.id)
            data = await state.get_data()
            number = data.get('Kaspi_number')
            await message.answer(text='✨ Ваш запрос отправлен❗'
                                      '\nВ ближайшее время деньги поступят на указанный счет'
                                 , reply_markup=keyboard.start_menu)
            await bot.send_message(config.ADMIN_ID,
                                   text=f'\n\nПользователь {user_name} ({message.chat.id}) хочет вывести деньги '
                                        f'в размере <b>{how_money} тенге</b>, на Kaspi Gold № <b>{number}</b>',
                                   parse_mode='html')
            if SQLUser().get_bonus(message.chat.id) == 0:
                await bot.send_message(message.chat.id, text='Пользователю надо выплатить 5000 тенге за регистрацию')
                SQLUser().upload_bonus(message.chat.id)
            else:
                pass
            SQLUser().upload_balance(chat_id=message.chat.id, balance=money - int(how_money))
            await state.finish()
        else:
            await message.answer(text='В нулях ошиблись 😁')
    else:
        await message.answer(text='Укажите количество цифрами')


# проверка подписки
def check_sub_channel(chat_member):
    if chat_member['status'] != 'left':
        return True
    else:
        return False


# проверка набрал ли юзер баланс для вывода
def check_money(chat_id):
    if SQLUser().get_balance(chat_id) > 29999:
        return True
    else:
        return False


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
