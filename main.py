import openai
import pytesseract
from PIL import Image
from io import BytesIO
import telebot
from telebot import types
import datetime

bot = telebot.TeleBot('SECRET_KEY')

def get_image_from_bytes(b):
    stream = BytesIO(b)
    image = Image.open(stream).convert("RGBA")
    stream.close()
    return image

def get_text_from_img(img):
    image = get_image_from_bytes(img)
    string = pytesseract.image_to_string(image, lang="rus+eng")
    return "распиши подробное решение " + string

def run_ask(message):
    model_engine = "text-davinci-003"
    prompt = message

    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return completion.choices[0].text

@bot.message_handler(commands=['start'])
def start(message):
    global is_gpt
    is_gpt = False
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("👋 Начать")
    btn2 = types.KeyboardButton("Задать вопрос")
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник!\n /help - для помощи\n/answer - задать вопрос", reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
    global is_gpt
    is_gpt = False
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("Назад")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Помощь: бла бла бла", reply_markup=markup)

@bot.message_handler(commands=['answer'])
def send_question(message):
    global is_gpt
    is_gpt = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn = types.KeyboardButton("Назад")
    markup.add(btn)
    bot.send_message(message.from_user.id, "Отправьте свой вопрос или отправьте картинку: ", reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def send_img(message):
    global is_gpt
    is_gpt = True
    photo_id = message.photo[-1].file_id
    # Достаём картинку
    bot.send_message(message.from_user.id, "⏳ Обрабатываем ваш вопрос...")
    photo_file = bot.get_file(photo_id)  # <class 'telebot.types.File'>
    photo_bytes = bot.download_file(photo_file.file_path)  # <class 'bytes'>
    # Отправить в дальнейшем можно таким образом
    bot.send_message(message.from_user.id, run_ask(get_text_from_img(photo_bytes)))

@bot.message_handler()
def get_user_text(message):
    if message.text == 'Назад' or message.text == '👋 Начать':
        start(message)
    elif message.text == 'Задать вопрос':
        send_question(message)
    else:
        if is_gpt:
            msg = bot.send_message(message.from_user.id, "⏳ Обрабатываем ваш вопрос...")
            bot.edit_message_text(run_ask(message.text), chat_id=message.chat.id, message_id=msg.message_id)
        else:
            bot.send_message(message.from_user.id, "Я не понимаю, что вы хотите. Можете пояснить?")


if __name__ == '__main__':
    MAX_MESSAGES_PER_DAY = 10
    openai.api_key = "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"
    is_gpt = False
    bot.polling(none_stop=True, interval=0)
