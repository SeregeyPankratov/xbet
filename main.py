from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text, CommandStart
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import datetime
import logging
import config
import os
import re
from sql import SQLUser
import keyboard


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN,) # proxy=proxy_url)
dp = Dispatcher(bot, storage=MemoryStorage())
CHANEL_ID = '@kazinside_kz'
DATE = datetime.datetime.now().strftime("%d-%m-%Y")
TEMP = []


class Output(StatesGroup):
    card_number = State()
    QIWI_number = State()
    BK_number = State()
    how_much = State()


# Приветствие
@dp.message_handler(CommandStart())
async def startup(message: types.Message):
    chat_id = message.from_user.id
    text = f'''⚡ Поздравляю, {message.from_user.first_name}

✅ Вы получаете <b>5.000 тенге (900₽)</b> бонусом

Чтобы вывести данные бонусы необходимо <b>оформить подписку</b> на этот канал 👇

✅ https://t.me/kazinside_kz

⚡'''
    # если зарегистрирован
    if SQLUser().user_exists(chat_id):
        await message.answer(text='🔝 Главное Меню', reply_markup=keyboard.start_menu)
    # если не зареган, и зашел по реф ссылке
    elif len(message.text) > 6:
        ref_user = message.text[8:]
        if SQLUser().get_referal_to_day(DATE, ref_user) < 99:
            await message.answer(text=text, disable_web_page_preview=True, parse_mode='html',
                                 reply_markup=keyboard.verify)
            SQLUser().add_user(chat_id, message.from_user.first_name, DATE, ref_user)

        else:
            await bot.send_message(chat_id, text=f'❌ По этой ссылке сегодня уже зарегистрировалось 100 человек.'
                                                 f'\nПовторите регистрацию завтра')

    # если не зареган, и зашел без реф ссылки
    else:
        await message.answer(text=text, disable_web_page_preview=True, parse_mode='html',
                             reply_markup=keyboard.verify)
        SQLUser().add_user(chat_id, message.from_user.first_name, DATE, ref_user=0)


# Обработка инлайн кнопок
@dp.callback_query_handler(lambda call: call.data)
async def inline_button(call: CallbackQuery):
    data = call.data
    chat_id = call.from_user.id
    if data == 'verify':
        if check_sub_channel(await bot.get_chat_member(chat_id=CHANEL_ID, user_id=chat_id)):
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
            await bot.send_message(chat_id,
                                   text=f'Чтобы вывести данные бонусы необходимо <b>оформить подписку</b> '
                                        f'на этот канал 👇 \n✅ https://t.me/kazinside_kz \n⚡',
                                   disable_web_page_preview=True, parse_mode='html', reply_markup=keyboard.verify)

    elif data == 'card':
        name = SQLUser().get_name_user(chat_id)
        text = f"⚠ Недостаточно денег на счету для снятия" \
               f"\n\n💳  {name}, минимальный баланс для снятия должен составлять: 30.000 тенге (6.000₽)"
        if check_money(chat_id):
            await bot.send_message(chat_id, text='💳 Укажите номер карты', reply_markup=keyboard.cancel)
            await Output.card_number.set()
            TEMP.append('card_number')
        else:
            await bot.answer_callback_query(call.id, f'{text}', show_alert=True)

    elif data == 'QIWI':
        name = SQLUser().get_name_user(chat_id)
        text = f"⚠ Недостаточно денег на счету для снятия" \
               f"\n\n💳  {name}, минимальный баланс для снятия должен составлять: 30.000 тенге (6.000₽)"
        if check_money(chat_id):
            await bot.send_message(chat_id,
                                   text="🔶 Укажите номер QIWI кошелька "
                                        "\n<b>+77xxxxxxxxx</b>", parse_mode='html', reply_markup=keyboard.cancel)
            await Output.QIWI_number.set()
            TEMP.append('QIWI_number')
        else:
            await bot.answer_callback_query(call.id, f'{text}', show_alert=True)

    elif data == 'BK':
        name = SQLUser().get_name_user(chat_id)
        text = f"⚠ Недостаточно денег на счету для снятия" \
               f"\n\n💳  {name}, минимальный баланс для снятия должен составлять: 30.000 тенге (6.000₽)"
        if check_money(chat_id):
            await bot.send_message(chat_id, text='🔷 Укажите логин БК', reply_markup=keyboard.cancel)
            await Output.BK_number.set()
            TEMP.append('BK_number')
        else:
            await bot.answer_callback_query(call.id, f'{text}', show_alert=True)


# обработка кнопок
@dp.message_handler(content_types="text")
async def buttons(message: types.Message):
    msg = message.text
    if msg == '👨🏼‍💻 Заработать':
        foto = os.path.join(config.TEMP_DIR, "8094aba2-d20d-46ad-a7b0-f5e10de5cd1b.jpg")
        url = f'https://t.me/sp_demo_bot?start=r{message.chat.id}'
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
        await message.answer('💰 Выберите удобные для Вас варианты снятия денег:', reply_markup=keyboard.cash)

    elif msg == '📊 Статистика':
        foto = os.path.join(config.TEMP_DIR, "1fee3ce9-0ccc-4ca8-b493-265a43e9f8db.jpg")
        url = f'https://t.me/sp_demo_bot?start=r{message.chat.id}'
        balance = SQLUser().get_balance(message.chat.id)
        referal = SQLUser().get_referal(message.chat.id)[-1][-1]
        all_user = SQLUser().get_all_user()
        user_to_day = SQLUser().get_user_to_day(DATE)
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


# Отмена, убираем все состояния
@dp.message_handler(Text(equals='🚫 Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    TEMP.clear()
    await message.answer('Действие отменено', reply_markup=keyboard.start_menu)


# Получаем номер карты
@dp.message_handler(content_types='text', state=Output.card_number)
async def card_handler(message: types.Message, state: FSMContext):
    card_number = message.text
    msg = re.match(r'[0-9]{16}', card_number) and len(card_number) == 16
    if msg:
        money = SQLUser().get_balance(message.chat.id)
        await message.answer(f'Ваш баланс составляет <b>{money} тенге</b>'
                             f'\nУкажите количество для вывода', parse_mode='html')
        async with state.proxy() as data:
            data["card_number"] = card_number
        await Output.how_much.set()
    else:
        await message.answer(text='❌ Номер карты должен состоять из 16 цифр')


# Получаем номер QIWI
@dp.message_handler(content_types='text', state=Output.QIWI_number)
async def QIWI_handler(message: types.Message, state: FSMContext):
    QIWI_number = message.text
    msg = re.match(r'[+77]{3}[0-9]{9}', QIWI_number) and len(QIWI_number) == 12
    if msg:
        money = SQLUser().get_balance(message.chat.id)
        await message.answer(f'Ваш баланс составляет <b>{money} тенге</b>'
                             f'\nУкажите количество для вывода', parse_mode='html')
        async with state.proxy() as data:
            data["QIWI_number"] = QIWI_number
        await Output.how_much.set()
    else:
        await message.answer("❌ Укажите номер Qiwi кошелька "
                             "\n<b>+77xxxxxxxxx</b>", parse_mode='html')


# Получаем номер БК
@dp.message_handler(content_types='text', state=Output.BK_number)
async def BK_handler(message: types.Message, state: FSMContext):
    BK_number = message.text
    money = SQLUser().get_balance(message.chat.id)
    await message.answer(f'Ваш баланс составляет <b>{money} тенге</b>'
                         f'\nУкажите количество для вывода', parse_mode='html')
    async with state.proxy() as data:
        data["BK_number"] = BK_number
    await Output.how_much.set()


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
            number = data.get(TEMP[-1])
            vivod = sposob_vivoda(TEMP[-1])
            await message.answer(text='✨ Ваш запрос отправлен❗'
                                      '\nВ ближайшее время деньги поступят на указанный счет')
            await bot.send_message(message.chat.id,
                                   text=f'❗Вот такое сообщение будет \nприходить администратору❗'
                                        f'\n\nПользователь {user_name} ({message.chat.id}) хочет вывести деньги '
                                        f'в размере <b>{how_money} тенге</b>, {vivod} <b>{number}</b>',
                                   parse_mode='html', reply_markup=keyboard.start_menu)
            if SQLUser().get_bonus(message.chat.id) == 0:
                await bot.send_message(message.chat.id, text='Пользователю надо выплатить 5000 тенге за регистрацию')
                SQLUser().upload_bonus(message.chat.id)
            else:
                pass
            SQLUser().upload_balance(chat_id=message.chat.id, balance=money - int(how_money))
            TEMP.clear()
            await state.finish()
        else:
            await message.answer(text='В нулях ошиблись 😁')
    else:
        await message.answer(text='Укажите количество цифрами')


def sposob_vivoda(info):
    if info == 'card_number':
        return 'на карту №'
    elif info == 'QIWI_number':
        return 'на кошелек Qiwi №'
    elif info == 'BK_number':
        return 'на логин БК - '


# проверка подписки
def check_sub_channel(chat_member):
    if chat_member['status'] != 'left':
        return True
    else:
        return False


# проверка набрал ли юзер баланс для вывода
def check_money(chat_id):
    if SQLUser().get_balance(chat_id) > 30000:
        return True
    else:
        return False


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
