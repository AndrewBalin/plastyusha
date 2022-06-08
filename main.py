import logging

from time import sleep
import random
import string

from VKparser import VkParser

import sqlite3

import collections

from telegram.ext import Filters, MessageHandler, Updater, CallbackContext, CommandHandler
from telegram import Update, Bot, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

con = sqlite3.connect('users.db', check_same_thread=False)
cur = con.cursor()

group = VkParser('2115f1962115f1962115f1966b21699d48221152115f19643788347c0b366ed046955d0')

message_plast = "Собирать и сдавать на переработку следует пластики с маркировкрой PET (1), HDPE (2), LDPE (4), ПП (PP, 5). Однако не весь пластик можно переработать. Изделия с маркировками PVC (3), O (7) и ABS в основном не перерабатываются, поэтому их лучше покупать. Но если уже купили, сдайте вместе с остальным пластиком.\n\nДля того, чтобы правильно сдать пластик на переработку нужно:\n   1. Очистить его от остатков еды или другого содержимого.\n  2. Полимерные отходы следует сплющить или смять, чтобы они занимали меньше места и дома, и в кузове мусоровоза.\n   3. Разобрать на составные части - открыть крышки, снять этикетки и так далее. Но делать это не обязательно."

def get_random_id(id):
    data = list(cur.execute(''f'SELECT unid FROM users WHERE id={id}'''))
    while len(data) != 0:
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, 10))
    return rand_string

class DialogBot(object):

    def __init__(self, token):
        self.bot = Bot(
            token=token,
        )
        self.updater = Updater(
            bot=self.bot,
        )
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help))
        dispatcher.add_handler(MessageHandler(Filters.text, self.text))

    def on(self):
        self.updater.start_polling()
        self.updater.idle()


    def send_message(self, message: str, chat, keyboard=0):
        if keyboard == 1:
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[[
                    KeyboardButton(text="Город Тюмень"),
                    KeyboardButton(text="ЯНАО"),
                    KeyboardButton(text="ХМАО"),
                ]],
                resize_keyboard=True
            )
            self.bot.send_message(
                chat_id=chat,
                text=message,
                reply_markup=reply_markup,
            )
        elif keyboard == 2:
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[[
                    KeyboardButton(text="Переработка пластика"),
                    KeyboardButton(text="Акции и мероприятия"),
                    KeyboardButton(text="О проекте"),
                ]],
                resize_keyboard=True
            )
            self.bot.send_message(
                chat_id=chat,
                text=message,
                reply_markup=reply_markup,
            )
        else:
            self.bot.send_message(
                chat_id=chat,
                text=message,
                reply_markup=ReplyKeyboardRemove()
            )

    def start(self, update, context):
        id = update.message.from_user['id']
        print(list(cur.execute(''f'SELECT * FROM users WHERE id={id}''')))
        data = list(cur.execute(''f'SELECT username FROM users WHERE id={id}'''))
        print(data, id)
        if len(data) == 0:
            self.send_message("Привет, я бот Пластюша. Я помогу тебе отыскать ближайшие акции по переработке пластика и научу делать это правильно. А как зовут тебя?", id)
            cur.execute(''f'INSERT INTO users (id, stade) VALUES ({id}, 1)''')
        else:
            stade = list(cur.execute(''f'SELECT stade FROM users WHERE id={id}'''))
            print(stade)
            if stade[0][0] == 1:
                self.send_message("Тебя ведь не зовут Старт, верно? Хахах, так какое твоё настоящее имя?", id)
            else:
                self.send_message(f"Привет, {data[0][0]}, мы уже знакомы, что ты хотел узнать?", id)
                cur.execute(''f'UPDATE users SET stade=7 WHERE id={id}''')
        con.commit()

    def help(self, update, context):
        id = update.message.from_user['id']
        name = list(cur.execute(''f'SELECT username FROM users WHERE id={id}'''))
        if name == None:
            self.send_message("Привет, я бот Пластюша. Я помогу тебе отыскать ближайшие акции по переработке пластика и научу делать это правильно, давай же скорее знакомится, как зовут тебя?", id)
            cur.execute(''f'INSERT INTO users (id, stade) VALUES ({id}, 1)''')
        else:
            stade = list(cur.execute(''f'SELECT stade FROM users WHERE id={id}'''))
            if stade[0][0] == 1:
                self.send_message("Тебя ведь не зовут Помощь, верно? Хахах, так какое твоё настоящее имя?", id)
            else:
                self.send_message(f"{name}, я бот Пластюша. Я помогу тебе отыскать ближайшие акции по переработке пластика и научу делать это правильно. Для этого спроси у меня 'Как сортировать пластик' или 'Какие мероприятия проходят в моём городе?'", id)
        con.commit()

    def text(self, update, context):
        id = update.message.from_user['id']
        stade = list(cur.execute(''f'SELECT stade FROM users WHERE id={id}'''))
        name = list(cur.execute(''f'SELECT username FROM users WHERE id={id}'''))
        text = update.message.text.lower()
        if len(stade) == 0:
            self.send_message(
                "Привет, я бот Пластюша. Я помогу тебе отыскать ближайшие акции по переработке пластика и научу делать это правильно. А как зовут тебя?",
                id)
            cur.execute(''f'INSERT INTO users (id, stade) VALUES ({id}, 1)''')
        elif stade[0][0] == 1:
            cur.execute(''f'UPDATE users SET username="{update.message.text.rstrip(".!").split()[0].capitalize()}", stade=2, unid="{get_random_id(id)}" WHERE id={id}''')
            self.send_message(f"Приятно познакомиться, {update.message.text.rstrip('.!').split()[0].capitalize()}. Ты ведь живёшь в Тюменской области (Тюмень, ХМАО, ЯНАО)?", id)
        elif stade[0][0] == 2:
            if 'да' in text:
                cur.execute(''f'UPDATE users SET stade=3 WHERE id={id}''')
                self.send_message("А знаешь ли ты какой пластик нужно сдавать на переработку и как правильно это делать?)", id)
            elif 'нет' in text:
                cur.execute(''f'UPDATE users SET stade=6 WHERE id={id}''')
                self.send_message(
                    "Жаль, но я всё равно могу рассказать тебе о том, какой пластик нужно сдавать на переработку и как правильно это делать, хочешь?",
                    id)
            else:
                self.send_message("Так да или нет?", id)
        elif stade[0][0] == 3:
            if 'да' in text:
                cur.execute(''f'UPDATE users SET stade=4 WHERE id={id}''')
                self.send_message(f"Молодец, {name[0][0]}! Хочешь я расскажу о том, какие мероприятия и акции проводятся в твоём городе?", id)
            elif 'нет' in text:
                self.send_message("Хорошо, сейчас я тебе всё расскажу!", id)
                sleep(random.randint(1, 3))
                self.send_message(message_plast, id)
                sleep(random.randint(1, 3))
                self.send_message("Теперь ты знаешь всё что нужно, для того, чтобы сдать пластик и принять участие в акциях и мероприятиях.", id)
                sleep(random.randint(1, 3))
                cur.execute(''f'UPDATE users SET stade=5 WHERE id={id}''')
                self.send_message(f"Выбери, пожалуйста, регион, в котором ты проживаешь или сейчас находишься.", id, 1)
            else:
                self.send_message("Так да или нет?", id)
        elif stade[0][0] == 4:
            if 'да' in text:
                cur.execute(''f'UPDATE users SET stade=5 WHERE id={id}''')
                self.send_message(f"Выбери, пожалуйста, регион, в котором ты проживаешь или сейчас находишься.", id, 1)
            elif 'нет' in text:
                cur.execute(''f'UPDATE users SET stade=7 WHERE id={id}''')
                self.send_message(
                    f"Удачи, {name[0][0]}! Я буду рад помочь.",
                    id)
            else:
                self.send_message("Так да или нет?", id)
        elif stade[0][0] == 5:
            if "город тюмень" in text:
                post = group.get_last_post(44919504)
                id = 44919504
                town = 'город тюмень'
            elif "янао" in text:
                post = group.get_last_post(145387764)
                id = 145387764
                town = 'янао'
            elif "хмао" in text:
                post = group.get_last_post(180197200)
                id = 180197200
                town = 'хмао'
            else:
                dialoger.send_message("Увы, но пока я не могу рассказать тебе об этом городе, но ты всегда можешь помочь и рассказать мне о нём, написав @AndrewBall")
                con.commit()
                return

            cur.execute(''f'UPDATE users SET stade=7, town="{town}" WHERE id={id}''')
            dialoger.send_message(
                f"В твоём городе сейчас проходит:\n\n{post}\n\nПодробнее: https://vk.com/club{id}", id)
        elif stade[0][0] == 6:
            if 'да' in text:
                cur.execute(''f'UPDATE users SET stade=7 WHERE id={id}''')
                self.send_message("Хорошо, сейчас я тебе всё расскажу!", id)
                sleep(random.randint(1, 3))
                self.send_message(message_plast, id)
                sleep(random.randint(1, 3))
                self.send_message(
                    "Теперь ты знаешь всё что нужно, для того, чтобы сдать пластик и принять участие в акциях и мероприятиях своего города. Ты всегда можешь помочь и рассказать мне о нём, написав @AndrewBall",
                    id)
            elif 'нет' in text:
                cur.execute(''f'UPDATE users SET stade=7 WHERE id={id}''')
                self.send_message(
                    f"Удачи, {name[0][0]}! Я буду рад помочь.",
                    id)
            else:
                self.send_message("Так да или нет?", id)
        elif stade[0][0] == 7:
            if text == "переработка пластика":
                self.send_message(message_plast, id)
                sleep(random.randint(1, 3))
                self.send_message(
                    "Давай участвовать в экологических акциях?)",
                    id,
                    2)
            elif text == "акции и мероприятия":
                if len(list(cur.execute(''f'SELECT town FROM users WHERE id={id}'''))) == 0:
                    cur.execute(''f'UPDATE users SET stade=4 WHERE id={id}''')
                else:
                    town = list(cur.execute(''f'SELECT town FROM users WHERE id={id}'''))[0][0]
                    if "город тюмень" in town:
                        post = group.get_last_post(44919504)
                        id = 44919504
                        town = 'город тюмень'
                    elif "янао" in town:
                        post = group.get_last_post(145387764)
                        id = 145387764
                        town = 'янао'
                    elif "хмао" in town:
                        post = group.get_last_post(180197200)
                        id = 180197200
                        town = 'хмао'

                    cur.execute(''f'UPDATE users SET stade=7, town="{town}" WHERE id={id}''')
                    dialoger.send_message(
                        f"В твоём городе сейчас проходит:\n\n{post}\n\nПодробнее: https://vk.com/club{id}", id, 2)

            elif text == "о проекте":
                self.send_message("о нас", id, 2)

            else:
                self.send_message(f"{name[0][0]}, чем я могу помочь?", id, 2)
        con.commit()

print("Start")
dialoger = DialogBot('5317596411:AAHKWtmVCEYg0Gu8LMCL3JNLcZPtefPBbMI')
dialoger.on()
