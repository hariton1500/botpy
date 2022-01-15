import json
import telebot
from telebot import types
from telebot.types import KeyboardButton, ReplyKeyboardRemove
import requests
import markups as m
import models as model

TOKEN = "5074469034:AAEfZA-kiuBPS840S66Fj2v7kJs_wKLe1QQ"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    chat_id = message.chat.id
    model.abonents[str(chat_id)] = {}
    model.abonents[str(chat_id)]['abons_list'] = []
    from pathlib import Path
    if Path(str(chat_id)).is_file():
        print('found file')
        file = open(str(chat_id), 'r')
        model.abonents[str(chat_id)]['guids_list'] = list(json.loads(file.read()))
        file.close()
        print('guids={}'.format(model.abonents[str(chat_id)]['guids_list']))
        bot.send_message(chat_id, 'Ваши учетные записи:')
        get_uids_data(chat_id, True)
        msg = bot.send_message(chat_id, text=model.Menu.main, reply_markup=m.markup_in)
        bot.register_next_step_handler(msg, askCommands)
    else:
        model.mode = 'notIn'
        bot.send_message(chat_id, 'Вас приветствует бот EvpaNet. С его помощью можно легко увидеть информацию о состоянии учетной записи, а еще, он будет присылать уведомления о скором окончании срока действия пакета интернет и другие оповещения.', reply_markup=ReplyKeyboardRemove())
        msg = bot.send_message(chat_id, 'Для пользования сервисом Вам необходимо авторизоваться. Понадобится указать ID и привязанный к нему номер телефона. В результате будут добавлены все ID к которым привязан этот номер телефона.', reply_markup=m.start_markup_NotIn)
        bot.register_next_step_handler(msg, askCommands)

def askCommands(message):
    chat_id = message.chat.id
    try:
        text = message.text.lower()
    except:
        text = ''
    print('обработка команды ' + text)
    if text == 'отмена':
        msg = bot.send_message(chat_id, text=model.Menu.main, reply_markup=m.markup_in)
        bot.register_next_step_handler(msg, askCommands)
    elif text == 'авторизация' or text == 'новая авторизация' or text == '/reg':
        msg = bot.send_message(chat_id, text='Введите ID:', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, askId)
    elif text == 'показать учетные записи' or text == 'кратко':
        get_uids_data(chat_id, False)
        msg = bot.send_message(chat_id, 'Показать детально - отправьте номер ID:', reply_markup=m.markup_in)
        bot.register_next_step_handler(msg, askCommands)
    elif text in [abon['id'] for abon in model.abonents[str(chat_id)]['abons_list']]:
        model.abonents[str(chat_id)]['selected_id'] = text
        bot.send_message(chat_id, text=abon_show(next(abon for abon in model.abonents[str(chat_id)]['abons_list'] if abon['id'] == text), True))
        bot.send_message(chat_id, text='Доступные команды для управления учетной записью:')
        msg = bot.send_message(chat_id, text='1. Пополнить баланс', reply_markup=m.markup_id_menu)
        bot.register_next_step_handler(msg, askCommands)
    elif text == 'пополнить' or text == 'пополнить баланс':
        msg = bot.send_message(chat_id, text='Введите сумму:', reply_markup=m.markup_reply)
        bot.register_next_step_handler(msg, askSum)
    elif text == 'обращение' or text == 'жалоба' or text == 'оставить обращение':
        msg = bot.send_message(chat_id, text='Введите текст обращения:')
        bot.register_next_step_handler(msg, askText)
    else:
        msg = bot.send_message(chat_id, 'Команда не распознана. Доступные команды: \nID - показать данные учетной записи\nАвторизация - пройти авторизацию')
        bot.register_next_step_handler(msg, askCommands)

def askText(message):
    chat_id = message.chat.id
    selected_id = model.abonents[str(chat_id)]['selected_id']
    guid = model.abonents[str(chat_id)]['guids_list'][model.abonents[str(chat_id)]['abons_list'].index(next(abon for abon in model.abonents[str(chat_id)]['abons_list'] if abon['id'] == selected_id))]
    res = send_remont(guid, chat_id, message.text)
    if (not res['error']):
        msg = bot.send_message(chat_id, text=str(res['message']), reply_markup=m.markup_id_menu)
        bot.register_next_step_handler(msg, askCommands)

def askSum(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if text == 'отмена':
        msg = bot.send_message(chat_id, text=model.Menu.main, reply_markup=m.markup_in)
        bot.register_next_step_handler(msg, askCommands)
    elif text.isdigit():
        selected_id = model.abonents[str(chat_id)]['selected_id']
        guid = model.abonents[str(chat_id)]['guids_list'][model.abonents[str(chat_id)]['abons_list'].index(next(abon for abon in model.abonents[str(chat_id)]['abons_list'] if abon['id'] == selected_id))]
        res = get_payment_id(guid, chat_id)
        #print(res)
        if (not res['error']):
            url = 'https://paymaster.ru/payment/init?LMI_MERCHANT_ID=95005d6e-a21d-492a-a4c5-c39773020dd3&LMI_PAYMENT_AMOUNT=' + str(text) + '&LMI_CURRENCY=RUB&LMI_PAYMENT_NO=' + str(res['message']['payment_id']) + '&LMI_PAYMENT_DESC=%D0%9F%D0%BE%D0%BF%D0%BE%D0%BB%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5%20EvpaNet%20ID%20' + model.abonents[str(chat_id)]['selected_id']
            msg = bot.send_message(chat_id, text='Нажмите для перехода по ссылке: [URL](' + url + ')', parse_mode='markdown')
            bot.register_next_step_handler(msg, askCommands)
    else:
        msg = bot.send_message(chat_id, text='Нужно ввести сумму. Повторите ввод')
        bot.register_next_step_handler(msg, askSum)

def askId(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if text == 'отмена':
        msg = bot.send_message(chat_id, text=model.Menu.main, reply_markup=m.markup_in)
        bot.register_next_step_handler(msg, askCommands)
    elif not text.isdigit():
        msg = bot.send_message(chat_id, 'ID должно быть числом. Повторите ввод', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, askId)
    else:
        model.abonents[str(chat_id)]['uid'] = int(text)
        #uid = int(text)
        msg = bot.send_message(chat_id, 'Введите номер телефона', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, askPhone)

def askPhone(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if text == 'отмена':
        msg = bot.send_message(chat_id, text=model.Menu.main, reply_markup=m.markup_in)
        bot.register_next_step_handler(msg, askCommands)
    elif not isValidPhoneNumber(text):
        msg = bot.send_message(chat_id, 'Введенный номер не корректный. Нужно вводить в фрмате +7ХХХХХХХХХХ. Повторите ввод')
        bot.register_next_step_handler(msg, askPhone)
    else:
        model.abonents[str(chat_id)]['phone'] = text
        res = register(model.abonents[str(chat_id)]['uid'], model.abonents[str(chat_id)]['phone'], chat_id)
        if res['error']:
            msg = bot.send_message(chat_id, 'Ошибка авторизации. ' + res['message'] + '. Повторите ввод данных', reply_markup=m.start_markup_NotIn)
            bot.register_next_step_handler(msg, askId)
        else:
            model.abonents[str(chat_id)]['guids_list'] = res['message']['guids']
            mode = 'In'
            file = open(str(chat_id), 'w')
            file.write(json.dumps(model.abonents[str(chat_id)]['guids_list']))
            file.close()
            msg = bot.send_message(chat_id, 'Авторизация прошла успешно', reply_markup=m.markup_in)
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

def get_payment_id(guid, chat_id):
    api_url = 'https://evpanet.com/api/apk/payment'
    headers = {'token': str(chat_id)}
    body = {'guid': guid}
    resp = requests.post(api_url, headers=headers, json=body)
    return resp.json()

def send_remont(guid, chat_id, text):
    api_url = 'https://evpanet.com/api/apk/support/request'
    headers = {'token': str(chat_id)}
    body = {'message': text, 'guid': guid}
    resp = requests.post(api_url, headers=headers, json=body)
    return resp.json()

def get_uids_data(chat_id, brief):
    for guid in model.abonents[str(chat_id)]['guids_list']:
        res = get_abon_data(guid, chat_id)
        if res['error']:
            msg = bot.send_message(chat_id, 'Ошибка получения данных. ' + res['message'] + '. Повторите позже', reply_markup=m.start_markup_NotIn)
            bot.register_next_step_handler(msg, askCommands)
        else:
            model.abonents[str(chat_id)]['abon'] = res['message']['userinfo']
            model.abonents[str(chat_id)]['abons_list'].append(model.abonents[str(chat_id)]['abon'])
            if brief:
                bot.send_message(chat_id, text=model.abonents[str(chat_id)]['abon']['id'])
            else:
                bot.send_message(chat_id, abon_show(model.abonents[str(chat_id)]['abon'], False))

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

#bot.polling(none_stop=True)
#bot.infinity_polling(timeout=40, long_polling_timeout=40)

