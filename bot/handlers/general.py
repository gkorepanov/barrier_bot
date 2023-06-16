import logging

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from bot import config
from bot.handlers.utils import (
    send_reply,
)
from bot.handlers.error import send_error_message_to_admin_chat


logger = logging.getLogger(__name__)


async def default_callback_handle(update: Update, context: CallbackContext):
    pass


async def error_handle(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    try:
        await send_reply(
            user_id=update.effective_user.id,
            bot=context.bot,
            text=f"Произошла какая-то ошибка, пожалуйста, напишите @{config.support_username}",
            parse_mode=ParseMode.HTML,
        )
    except:
        logger.error("Could not send error message to user")

    await send_error_message_to_admin_chat(
        bot=context.bot,
        update=update,
        error=context.error,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        username=update.effective_user.username,
    )
