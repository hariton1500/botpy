import telebot
from telebot.types import ReplyKeyboardRemove
import markups as m
import dbm

db = dbm.open(file='users', flag='c')

#global mode
mode = 'notIn'

TOKEN = "5074469034:AAEfZA-kiuBPS840S66Fj2v7kJs_wKLe1QQ"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Вас приветствует асситент-бот EvpaNet', reply_markup=ReplyKeyboardRemove())
    if str(chat_id) in db:
        mode = 'In'
        msg = bot.send_message(chat_id, reply_markup=m.start_markup_in_btn_show)
        print(db[str(chat_id)])
        bot.register_next_step_handler(msg, askCommands)
    else:
        mode = 'notIn'
        msg = bot.send_message(chat_id, 'Нужно пройти авторизацию', reply_markup=m.start_markup_NotIn)
        bot.register_next_step_handler(msg, askCommands)

def askCommands(message):
    chat_id = message.chat.id
    text = message.text.lower()
    print('обработка команды ' + text)
    if text == 'авторизация':
        msg = bot.send_message(chat_id, text='Введите ID:', reply_markup=None)
        bot.register_next_step_handler(msg, askId)
    
    if text == 'показать учетные записи':
        bot.send_message(chat_id, text=db.keys, reply_markup=None)

def askId(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if not text.isdigit():
        msg = bot.send_message(chat_id, 'ID должно быть числом. Повторите ввод')
        bot.register_next_step_handler(msg, askId)
    else:
        msg = bot.send_message(chat_id, 'Введите номер телефона')
        bot.register_next_step_handler(msg, askPhone)

def askPhone(message):
    chat_id = message.chat.id
    text = message.text.lower()
    print(text)

bot.polling(none_stop=True)
