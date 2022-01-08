import json
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardRemove
import requests
import markups as m
import models as model

TOKEN = "5074469034:AAEfZA-kiuBPS840S66Fj2v7kJs_wKLe1QQ"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Вас приветствует бот EvpaNet. С его помощью можно легко увидеть информацию о состоянии учетной записи, а еще, он будет присылать уведомления о скором окончании срока действия пакета интернет и другие оповещения.', reply_markup=ReplyKeyboardRemove())
    model.abonents[str(chat_id)] = {}
    model.abonents[str(chat_id)]['abons_list'] = []
    from pathlib import Path
    if Path(str(chat_id)).is_file():
        print('found file')
        file = open(str(chat_id), 'r')
        model.abonents[str(chat_id)]['guids_list'] = list(json.loads(file.read()))
        file.close()
        print('guids={}'.format(model.abonents[str(chat_id)]['guids_list']))
        msg = bot.send_message(chat_id, 'Вы уже авторизованы.\nВаши учетные записи: ' + str(model.abonents[str(chat_id)]['guids_list']) + '\nДоступные команды:\n1. Авторизация - пройти новую авторизацию (для тех у кого много разных учетных записей)\n2. Показать учетные записи - отобразит краткий список учетных записей\n3. ID - покажет данные учетной записи более детально', reply_markup=m.start_markup_in)
        bot.register_next_step_handler(msg, askCommands)
    else:
        model.mode = 'notIn'
        msg = bot.send_message(chat_id, 'Авторизация', reply_markup=m.start_markup_NotIn)
        bot.register_next_step_handler(msg, askCommands)

def askCommands(message):
    chat_id = message.chat.id
    text = message.text.lower()
    print('обработка команды ' + text)
    if text == 'авторизация' or text == 'новая авторизация' or text == '/reg':
        msg = bot.send_message(chat_id, text='Введите ID:', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, askId)
    elif text == 'показать учетные записи':
        for guid in model.abonents[str(chat_id)]['guids_list']:
            res = get_abon_data(guid, chat_id)
            if res['error']:
                msg = bot.send_message(chat_id, 'Ошибка получения данных. ' + res['message'] + '. Повторите позже')
                bot.register_next_step_handler(msg, askCommands)
            else:
                model.abonents[str(chat_id)]['abon'] = res['message']['userinfo']
                model.abonents[str(chat_id)]['abons_list'].append(model.abonents[str(chat_id)]['abon'])
                bot.send_message(chat_id, abon_show(model.abonents[str(chat_id)]['abon'], False))
        msg = bot.send_message(chat_id, 'Показать детально - отправьте номер ID:', reply_markup=m.get_uids_buttons(model.abons).add(KeyboardButton(text='Предыдущее меню')))
        bot.register_next_step_handler(msg, askCommands)
    elif text in [abon['id'] for abon in model.abonents[str(chat_id)]['abons_list']]:
        msg = bot.send_message(chat_id, text=abon_show(next(abon for abon in model.abonents[str(chat_id)]['abons_list'] if abon['id'] == text), True))
        bot.register_next_step_handler(msg, askCommands)
    else:
        msg = bot.send_message(chat_id, 'Команда не распознана. Доступные команды: \nID - показать данные учетной записи\nАвторизация - пройти авторизацию')
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
            model.abonents[str(chat_id)]['guids_list'] = res['message']['guids']
            mode = 'In'
            file = open(str(chat_id), 'w')
            file.write(json.dumps(model.abonents[str(chat_id)]['guids_list']))
            file.close()
            msg = bot.send_message(chat_id, 'Авторизация прошла успешно', reply_markup=m.start_markup_in)
            bot.register_next_step_handler(msg, askCommands)

def register(uid, phone, chat_id):
    api_url = 'https://evpanet.com/api/apk/login/user'
    headers = {'token': str(chat_id)}
    body = {'number': phone, 'uid': str(uid)}
    #print(body)
    resp = requests.post(api_url, json=body, headers=headers)
    #print(resp.status_code)
    #print(resp.json())
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
    out = 'Данные абонента ID: {}\nФИО: {}\nАдрес: {}'.format(abon['id'], abon['name'], abon['street'] + ' ' + abon['flat'])
    if full:
        out += '\nБаланс: {}\nДата окончания срока действия пакета: {}\nТариф: {} ({}) руб.\n'.format(abon['extra_account'], abon['packet_end'], abon['tarif_name'], abon['tarif_sum'])
    return out

bot.polling(none_stop=True)

