from typing import Optional, Tuple
import logging
import traceback
import html
import json
import uuid

from telegram import Update, Bot
from telegram.constants import ParseMode, MessageLimit

from bot import config
from bot.database import db, ChatId, UserId
from bot.handlers.utils import split_text_at_good_places
from bot.handlers.utils import send_reply


logger = logging.getLogger(__name__)


async def send_error_message_to_admin_chat(
    error: Exception,
    bot: Bot,
    username: Optional[str] = None,
    chat_id: Optional[ChatId] = None,
    user_id: Optional[UserId] = None,
    update: Optional[Update] = None,
) -> None:
    error_id = str(uuid.uuid4())

    async def _send_text(text: str):
        for text_chunk in split_text_at_good_places(text, MessageLimit.MAX_TEXT_LENGTH):
            await send_reply(
                bot=bot,
                chat_id=config.admin_chat_id,
                text=text_chunk,
                parse_mode=ParseMode.HTML,
                try_no_parse_mode=True
            )

    try:
        if config.admin_chat_id is not None:
            # update str
            if update is not None:
                if isinstance(update, Update):
                    update_str = update.to_dict()
                    try:
                        if "message" in update_str:
                            update_str["message"]["text"] = update_str["message"]["text"][:50] + "..."
                    except:
                        pass
                else:
                    update_str = str(update)
            else:
                update_str = ""

            # traceback str
            traceback_list = traceback.format_exception(None, error, error.__traceback__)
            filtered_traceback_list = []
            system_files_started = False
            system_files_finished = False
            for x in traceback_list:
                is_system_line = 'File "/usr/local/lib' in x
                if is_system_line:
                    system_files_started = True
                if system_files_finished or not is_system_line:
                    filtered_traceback_list.append(x)
                if system_files_started and not is_system_line:
                    system_files_finished = True
            traceback_str = "".join(filtered_traceback_list)

            text = (
                f"<b>🚨 Exception was raised:</b>\n"
                f"  ⤷ error_id: <code>{error_id}</code>\n"
                f"  ⤷ chat_id: <code>{chat_id}</code>\n"
                f"  ⤷ user_id: <code>{user_id}</code>\n"
                f"  ⤷ username: @{username}\n\n"
            )
            await _send_text(text)

            if update_str:
                text = (
                    f"<b>🔄 Update:</b>\n"
                    f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>\n\n"
                )
                await _send_text(text)

            if traceback_str:
                text = (
                    f"<b>🔴 Traceback:</b>\n"
                    f"<pre>{html.escape(traceback_str)}</pre>"
                )
                await _send_text(text)
    except Exception as e:
        logger.error("Could not send error message to admin chat")
