import os
import random
import time

import requests
import telebot
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot import *

load_dotenv()

# Каждые 10 секунд бот отправляет анегдот пользователю
SPAM_TIME = 10

# Страница на которую отправляем запрос
url = 'https://www.anekdotov-mnogo.ru/anekdoti_userov.php'
headers = {'user-agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
html = response.text
soup = BeautifulSoup(html, 'lxml')
pages = '210'
print('Всего страниц: ' + pages)
data = []


def parser(url, headers, response, html, soup, pages):
    for page in range(1, int(pages)+1):
        response = requests.get(url, headers=headers, params={'page': page})
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        blocks = soup.find_all(
            'div',
            class_='tmpLineUnderContent tmpPaddingContent'
        )
        print(f'Парсинг страницы {page} из {pages}...')
        for block in blocks:
            try:
                data.append(block.find('p').get_text("\n"))
            except:
                print("")
    print('Получили ' + str(len(data)) + ' позиций')
    print("\n")
    return data


list_of_jokets = parser(url, headers, response, html, soup, pages)
random.shuffle(list_of_jokets)

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN)

# Словарь для хранения информации о последних анекдотах для каждого пользователя
last_joke = {}


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("😜ПОГНАЛИ😜")
    item2 = types.KeyboardButton("📝Помощь📝")
    markup.add(item1, item2)

    bot.send_sticker(
        message.chat.id,
        'CAACAgIAAxkBAAEIqtVkQk6jdnyn7TbwMgoHgmirbLFdkwACpwIAAvEElxNzELAdFfmXJS8E'
    )
    bot.send_message(
        message.chat.id,
        '❗Привет ' + message.from_user.first_name + "❗\n😜Ты попал в спам-бот анекдотов😜\n😁Теперь ставь мобилу на зарядку😁",
        reply_markup=markup
    )


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == "📝Помощь📝":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("😜ПОГНАЛИ😜")
        item2 = types.KeyboardButton("📝Помощь📝")
        markup.add(item1, item2)
        bot.send_message(message.chat.id,
                         "03 или 112",
                         reply_markup=markup)

    elif message.text == "😜ПОГНАЛИ😜" or message.text == "/anecdote":
        send_anecdote(message.chat.id)


def send_anecdote(chat_id):
    global list_of_jokets, last_joke
    if chat_id not in last_joke or time.time() - last_joke[chat_id] >= SPAM_TIME:
        if len(list_of_jokets) > 0:
            anecdote = list_of_jokets[0]
            del list_of_jokets[0]
            bot.send_message(chat_id, anecdote)
            last_joke[chat_id] = time.time()
        else:
            bot.send_message(chat_id, "Ошибка")


set_interval(
    lambda: [send_anecdote(chat_id) for chat_id in last_joke.keys()], SPAM_TIME
)

bot.polling()
