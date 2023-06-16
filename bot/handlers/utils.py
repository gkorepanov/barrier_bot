from contextlib import contextmanager
from typing import Optional, List, Tuple
from functools import wraps
import logging
import base64
import secrets


import telegram
from telegram import Update, Message, Bot
from telegram.ext import CallbackContext
from telegram.constants import ChatAction, ParseMode

from bot import config
from bot.database import db
from bot.handlers import manage_data as md


logger = logging.getLogger(__name__)


def get_start_url(source: str) -> str:
    link = f"https://t.me/{config.bot_username}?start=source={source}"
    return link


def get_start_href(source: str) -> str:
    url = get_start_url(source)
    result = f'<a href="{url}">{config.bot_name}</a>'
    return result


def get_short_secure_key() -> str:
    key = secrets.token_bytes(8)
    utf8_key = base64.urlsafe_b64encode(key).decode('utf-8')
    return utf8_key


def add_handler_routines(
    check_is_admin: bool = False,
    check_is_allowed_to_open_barriers: bool = False,
    send_typing: bool = False,
    answer_callback_query: bool = False,
):
    def decorator(f):
        @wraps(f)
        async def _fn(update: Update, context: CallbackContext, *args, **kwargs):
            user = update.effective_user
            user_id = user.id
            db.add_or_update_user(
                user_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
            )
            role = db.get_user_role(user_id)
            is_admin = (
                (role == md.Role.ADMIN) or
                user.username in config.admin_usernames
            )
            if not is_admin and (
                check_is_admin or
                (check_is_allowed_to_open_barriers and not db.is_user_allowed_to_open_barrier(user_id))
            ):
                await send_reply(
                    message=update.effective_message,
                    text=f"У вас нет доступа. Обратитесь к @{config.support_username}",
                    parse_mode=ParseMode.HTML,
                    send_as_reply=True,
                )
                return

            if send_typing:
                try:
                    await update.effective_chat.send_action(ChatAction.TYPING)
                except:
                    pass
            if answer_callback_query:
                try:
                    await update.callback_query.answer()
                except:
                    pass
            await f(update, context, *args, **kwargs)
        return _fn
    return decorator


def split_text_into_chunks(text, chunk_size):
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]


def truncate_text(line, width, add_dots: bool = True):
    if len(line) > width:
        line = line[:width-3] + '...'
    return line


async def send_reply(
    message: Optional[Message] = None,
    bot: Optional[Bot] = None,
    user_id: Optional[int] = None,
    chat_id: Optional[int] = None,
    message_id: Optional[int] = None,
    try_edit: bool = False,
    try_delete: bool = False,
    try_no_parse_mode: bool = False,
    send_as_reply: bool = False,
    ignore_message_not_modified_error: bool = True,
    ignore_not_enough_rights_error: bool = False,
    **kwargs,
) -> Message:
    if message is None:
        assert bot is not None
    else:
        bot = message.get_bot()
        chat_id = message.chat.id
        message_id = message.message_id

    if chat_id is None and user_id is not None:
        chat_id = user_id   # use private chat

    assert chat_id is not None
    assert bot is not None
    kwargs['chat_id'] = chat_id
    if try_edit or try_delete or send_as_reply:
        assert message_id is not None

    async def _reply():
        if try_edit:
            try:
                return await bot.edit_message_text(message_id=message_id, **kwargs)
            except telegram.error.BadRequest as e:
                if ignore_message_not_modified_error and "message is not modified" in str(e).lower():
                    logger.error(f"Message is not modified for chat {chat_id} and message {message_id}")
                    return message
            except:  # TODO: handle specific error only
                pass
        elif try_delete:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:   # TODO: handle specific error only
                pass

        if send_as_reply:
            kwargs['reply_to_message_id'] = message_id

        return await bot.send_message(**kwargs)

    try:
        if try_no_parse_mode:
            try:
                return await _reply()
            except telegram.error.BadRequest as e:
                if 'parse_mode' in kwargs:
                    logger.error(f"Retrying without parse mode because of error: {str(e)}")
                    kwargs.pop('parse_mode')
                    return await _reply()
                else:
                    raise
        else:
            return await _reply()
    except (telegram.error.BadRequest, telegram.error.Forbidden) as e:
        if not ignore_not_enough_rights_error:
            raise
        if isinstance(e, telegram.error.BadRequest) and "not enough rights" in str(e).lower():
            pass
        elif isinstance(e, telegram.error.Forbidden):
            pass
        else:
            raise
        logger.error(f"Not enough rights for chat {chat_id}")
        return message


def heading_dash(heading: str):
    return "-" * len(heading)


def wrap_heading_dash(heading: str, n: Optional[int] = None):
    if n is not None:
        assert n >= len(heading)
        heading = heading.center(n)
    return f"{heading_dash(heading)}\n{heading}\n{heading_dash(heading)}"


def split_text_at_good_places(
    text: str,
    message_size_limit: int,
):
    parts = _split_text(text, message_size_limit=message_size_limit)
    return _combine_parts(parts, message_size_limit=message_size_limit)


def _split_text(
    text: str,
    message_size_limit: int,
    separators: Tuple[str] = (
        '\n\n',
        '\n',
        '. ',
        '! ',
        '? ',
        ', ',
        ' ',
    ),
) -> List[str]:
    if len(separators) == 0:
        parts = split_text_into_chunks(text, message_size_limit - 1)
    else:
        separator = separators[0]
        parts = text.split(separator)
        parts = [x + separator for x in parts[:-1]] + [parts[-1]]

    result = []
    for part in parts:
        if len(part) < message_size_limit:
            result.append(part)
        else:
            result += _split_text(
                part,
                message_size_limit,
                separators=separators[1:],
            )
    return result


def _combine_parts(parts: List[str], message_size_limit: int):
    result = [parts[0]]
    for part in parts[1:]:
        if len(result[-1] + part) < message_size_limit:
            result[-1] = result[-1] + part
        else:
            result.append(part)
    return result


@contextmanager
def ignore_message_not_modified_error():
    try:
        yield
    except telegram.error.BadRequest as e:
        if "message is not modified" in str(e).lower():
            pass
        else:
            raise


async def send_message_to_admin_chat(
    text: str,
    bot: Bot,
):
    if not config.admin_chat_id:
        return
    try:
        for message_chunk in split_text_into_chunks(text, 4000):
            await send_reply(
                chat_id=config.admin_chat_id,
                bot=bot,
                text=message_chunk,
                parse_mode=ParseMode.HTML,
                try_no_parse_mode=True,
            )
    except:
        logger.exception("Could not send message to admin chat")
