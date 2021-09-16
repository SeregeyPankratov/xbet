from aiogram import types

start_menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
a1 = types.KeyboardButton(text='👨🏼‍💻 Заработать')
a2 = types.KeyboardButton(text='💳 Мой баланс')
a3 = types.KeyboardButton(text='📄 Правила')
a4 = types.KeyboardButton(text='📊 Статистика')
start_menu.add(a1, a2, a3, a4)

verify = types.InlineKeyboardMarkup(row_width=1)
v1 = types.InlineKeyboardButton(text='✅ Проверить', callback_data='verify')
verify.add(v1)

output_money = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
o1 = types.KeyboardButton(text='📤 Вывести')
o2 = types.KeyboardButton(text='🔝 Главное Меню')
output_money.add(o1, o2)

cash = types.InlineKeyboardMarkup(row_width=1)
c1 = types.InlineKeyboardButton(text='💳 Банковская карта', callback_data='card')
c2 = types.InlineKeyboardButton(text='🔶 Кошелек QIWI', callback_data='QIWI')
c3 = types.InlineKeyboardButton(text='🔷 Логин БК', callback_data='BK')
cash.add(c1, c2, c3)

cancel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
can = types.KeyboardButton(text='🚫 Отмена')
cancel.add(can)
