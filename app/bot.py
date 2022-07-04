import asyncio

from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config import TELEGRAM_API_TOKEN, GATE_NAMES
from gates import open_gates

import telebot
import logging

logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG)

auth = 0
#print(TELEGRAM_API_TOKEN)
bot = AsyncTeleBot(TELEGRAM_API_TOKEN)

buttons = {}
markup = ReplyKeyboardMarkup(resize_keyboard=True)


def add_button(markup, button_text, button_callback):
    item = KeyboardButton(button_text)
    markup.add(item)
    buttons.update({button_text: button_callback})


def make_gate_handler(gate_name):
    async def button_open(message):
        open_gates(gate_name)
        await bot.reply_to(message, f"Открываю {gate_name}", reply_markup=markup)
    return button_open


for gate_name in GATE_NAMES:
    add_button(markup, gate_name, make_gate_handler(gate_name))


@bot.message_handler(commands=["start"])
async def start(message):
    await bot.reply_to(message, "Что открываем?", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
async def handle_text(message):
    name = message.text.strip()
    if (handler := buttons.get(name)) is None:
        await bot.reply_to(message, f"Нет такого шлагбаума: {name}, есть {list(buttons)}", reply_markup=markup)
    else:
        await handler(message)


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)


asyncio.run(bot.polling())
