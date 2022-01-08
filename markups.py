import models as model
from telebot import types


markup_in = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
start_markup_in_btn_reIn = types.KeyboardButton(text='Авторизация')
start_markup_in_btn_show = types.KeyboardButton(text='Кратко')
start_markup_in_btn_cancel = types.KeyboardButton(text='Отмена')
markup_in.add(start_markup_in_btn_reIn, start_markup_in_btn_show, start_markup_in_btn_cancel)

def get_uids_buttons(abons):
    uids_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btns = []
    for abon in abons:
        btns.append(types.KeyboardButton(text=abon['id']))
    uids_markup.add(btns, start_markup_in_btn_reIn, start_markup_in_btn_show)
    return uids_markup

start_markup_NotIn = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
start_markup_NotIn_btn = types.KeyboardButton(text='Авторизация')
#start_markup_NotIn_btn_show = types.KeyboardButton(text='Показать учетные записи')
start_markup_NotIn.add(start_markup_NotIn_btn)

markup_id_menu = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
markup_id_menu_pay = types.KeyboardButton(text='Пополнить баланс')
markup_id_menu.add(markup_id_menu_pay, start_markup_in_btn_cancel, start_markup_in_btn_show)


