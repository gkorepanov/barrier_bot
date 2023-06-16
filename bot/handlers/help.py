import logging
import asyncio

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from bot.handlers.utils import (
    add_handler_routines,
)
from bot.database import db
from bot.handlers import manage_data as md
from bot import config


logger = logging.getLogger(__name__)


@add_handler_routines(
    check_is_allowed_to_open_barriers=True,
)
async def start_handle(update: Update, context: CallbackContext):
    text = (
        f"Привет 👋 Я бот для открывания шлагбаумов от @{config.support_username}.\n"
        f"Чтобы открыть шлагбаум, <b>нажми команду</b> /open.\n\n"
        f"Если у тебя есть права администратора, "
        f"то ты также можешь управлять шлагбаумами и пользователями, "
        f"нажми /help для подробностей или напиши @{config.support_username}"
    )
    await update.message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

@add_handler_routines(
    check_is_allowed_to_open_barriers=True,
)
async def help_handle(update: Update, context: CallbackContext):
    text = (
        f"Привет 👋 Я бот для открывания шлагбаумов от @{config.support_username}.\n"
        f"Чтобы открыть шлагбаум, <b>нажми команду</b> /open.\n\n"
        f"<b>Для админов:</b>\nЧтобы добавить нового пользователя, пришли мне его <b>контакт</b>.\n"
        f"Для добавления нового шлагбаума, напиши \n\n"
        f"<code>/add_barrier +7XXXXXXXXXX 'название шлагбаума'</code>.\n\n"
        f"Убедись, что номер {config.zadarma_number} привязан к шлагбауму.\n\n"
        f"Для удаления шлагбаума обратись к @{config.support_username} 🙂"
    )
    await update.message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
