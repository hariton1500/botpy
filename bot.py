import json
import telebot
from telebot.types import ReplyKeyboardRemove
import requests
import markups as m
#import dbm
import models as model

#db = dbm.open(file='users', flag='c')

#global mode
#mode = 'notIn'
#guids = list()
abons = []


TOKEN = "5074469034:AAEfZA-kiuBPS840S66Fj2v7kJs_wKLe1QQ"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Вас приветствует ассистент-бот EvpaNet', reply_markup=ReplyKeyboardRemove())
    from pathlib import Path
    if Path(str(chat_id)).is_file():#str(chat_id) in db:
        print('found file')
        file = open(str(chat_id), 'r')
        print('guids before: {}'.format(model.guids))
        model.guids = list(json.loads(file.read()))
        print('guids={}'.format(model.guids))
        model.mode = 'In'
        msg = bot.send_message(chat_id, 'Меню:',reply_markup=m.start_markup_in)
        bot.register_next_step_handler(msg, askCommands)
    else:
        model.mode = 'notIn'
        msg = bot.send_message(chat_id, 'Нужно пройти авторизацию', reply_markup=m.start_markup_NotIn)
        bot.register_next_step_handler(msg, askCommands)

def askCommands(message):
    chat_id = message.chat.id
    text = message.text.lower()
    print('обработка команды ' + text)
    if text == 'авторизация' or text == 'новая авторизация':
        msg = bot.send_message(chat_id, text='Введите ID:', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, askId)
    elif text == 'показать учетные записи':
        #bot.send_message(chat_id, text=model.guids.__str__, reply_markup=ReplyKeyboardRemove())
        #print('iterating through {}'.format(model.guids))
        for guid in model.guids:
            res = get_abon_data(guid, chat_id)
            #print('res={}'.format(res))
            if res['error']:
                msg = bot.send_message(chat_id, 'Ошибка получения данных. ' + res['message'] + '. Повторите позже')
                bot.register_next_step_handler(msg, askCommands)
            else:
                abons.clear()
                abons.append(res['message']['userinfo'])
                bot.send_message(chat_id, abon_show(abons[-1], False))
        msg = bot.send_message(chat_id, 'Меню:', reply_markup=m.get_uids_buttons(abons))
        bot.register_next_step_handler(msg, askCommands)
    elif text in [abon['id'] for abon in abons]:
        msg = bot.send_message(chat_id, text=abon_show(next(abon for abon in abons if abon['id'] == text), True))
        bot.register_next_step_handler(msg, askCommands)
    else:
        msg = bot.send_message(chat_id, 'Команда не распознана')
        bot.register_next_step_handler(msg, askCommands)

def askId(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if not text.isdigit():
        msg = bot.send_message(chat_id, 'ID должно быть числом. Повторите ввод', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, askId)
    else:
        global uid
        uid = int(text)
        msg = bot.send_message(chat_id, 'Введите номер телефона', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, askPhone)

def askPhone(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if not isValidPhoneNumber(text):
        msg = bot.send_message(chat_id, 'Введенный номер не корректный. Нужно вводить в фрмате +7ХХХХХХХХХХ. Повторите ввод')
        bot.register_next_step_handler(msg, askPhone)
    else:
        phone = text
        res = register(uid, phone, chat_id)
        if res['error']:
            msg = bot.send_message(chat_id, 'Ошибка авторизации. ' + res['message'] + '. Повторите ввод данных')
            bot.register_next_step_handler(msg, askId)
        else:
            guids = res['message']['guids']
            print(guids)
            mode = 'In'
            #db[str(chat_id)] = json.dumps(guids)
            file = open(str(chat_id), 'w')
            file.write(json.dumps(guids))
            file.close()
            #print(json.dumps(guids))
            msg = bot.send_message(chat_id, 'Авторизация прошла успешно', reply_markup=m.start_markup_in)
            bot.register_next_step_handler(msg, start_handler)

def register(uid, phone, chat_id):
    api_url = 'https://evpanet.com/api/apk/login/user'
    headers = {'token': str(chat_id)}
    body = {'number': phone, 'uid': str(uid)}
    print(body)
    resp = requests.post(api_url, json=body, headers=headers)
    print(resp.status_code)
    print(resp.json())
    return resp.json()

def get_abon_data(guid, chat_id):
    api_url = 'https://evpanet.com/api/apk/user/info/' + guid
    headers = {'token': str(chat_id)}
    resp = requests.get(api_url, headers=headers)
    return resp.json()

def isValidPhoneNumber(text):
    if text[0] == '+' and text[1:].isdigit() and len(text)==12:
        return True
    else:
        return False

def abon_show(abon, full):
    out = '''Данные абонента ID: {}
    ФИО: {}
    Адрес: {}
    '''.format(abon['id'], abon['name'], abon['street'] + ' ' + abon['flat'])
    if full:
        out += '''Баланс: {}
        Дата окончания срока действия пакета: {}
        Тариф: {} ({}) руб.
        '''.format(abon['extra_account'], abon['packet_end'], abon['tarif_name'], abon['tarif_sum'])
    return out

bot.polling(none_stop=True)

