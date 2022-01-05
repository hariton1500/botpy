from telebot import types

start_markup_in = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
start_markup_in_btn_reIn = types.KeyboardButton(text='Новая авторизация')
start_markup_in_btn_show = types.KeyboardButton(text='Показать учетные записи')
start_markup_in.add(start_markup_in_btn_reIn, start_markup_in_btn_show)

start_markup_NotIn = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
start_markup_NotIn_btn = types.KeyboardButton(text='Авторизация')
#start_markup_NotIn_btn_show = types.KeyboardButton(text='Показать учетные записи')
start_markup_NotIn.add(start_markup_NotIn_btn)

def get_uids_buttons(abons):
    uids_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    #btns = []
    for abon in abons:
        #btns.append(types.KeyboardButton(text=abon['id']))
        uids_markup.add(types.KeyboardButton(text=abon['id']))
    #uids_markup.add(btns)
    return uids_markup
