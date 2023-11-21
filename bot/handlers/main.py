import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

import bot.handlers.manage_data as md
from bot.handlers.utils import (
    send_reply,
    add_handler_routines,
)
from bot.database import db
from bot.gates import call_number
from bot import config


logger = logging.getLogger(__name__)



@add_handler_routines(
    check_is_admin=True,
    check_is_allowed_to_open_barriers=True,
)
async def add_barrier_handler(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await send_reply(
            message=update.effective_message,
            text=(
                "Отправьте команду в формате \n\n"
                "`/add_barrier +7XXXXXXXXXX <название шлагбаума>`"
            ),
            send_as_reply=True,
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    phone_number, *barrier_name = context.args
    if not barrier_name:
        await send_reply(
            message=update.effective_message,
            text="Не вижу названия шлагбаума",
            send_as_reply=True,
        )
        return
    if (
        not phone_number.startswith("+79") or
        not all(x.isdigit() for x in phone_number[1:]) or
        len(phone_number) != 12
    ):
        await send_reply(
            message=update.effective_message,
            text=f"Неверный формат номера `{phone_number}`!",
            send_as_reply=True,
        )
        return
    barrier_name = "_".join(barrier_name)
    barrier_id = db.add_barrier(phone_number=phone_number, name=barrier_name)
    db.add_barrier_to_user(
        user_id=update.effective_user.id,
        barrier_id=barrier_id,
    )
    await send_reply(
        message=update.effective_message,
        text=(
            f"Добавил шлагбаум `{barrier_name}` с номером `{phone_number}`.\n"
            f"Не забудьте внести номер {config.zadarma_number} в базу шлагбаума!"
        ),
        send_as_reply=True,
    )


@add_handler_routines(
    check_is_allowed_to_open_barriers=True,
)
async def show_barriers_handler(update: Update, context: CallbackContext) -> None:
    text = "Выбери шлагбаум:\n"
    buttons = []
    accessible_barriers = db.get_user_attribute(update.effective_user.id, "barriers", default=[])
    if len(accessible_barriers) == 0:
        await send_reply(
            message=update.effective_message,
            text=(
                "Пока нет доступных шлагбаумов. Либо добавь новый (/help), "
                "либо попроси дать тебе доступ другого админа."
            )
        )
        return
    for i, barrier_id in enumerate(accessible_barriers, start=1):
        barrier = db.get_barrier(barrier_id)
        name = barrier["name"].replace("_", " ")
        button_text = f"{i}. {name}\n"
        buttons.append(InlineKeyboardButton(
            text=button_text,
            callback_data=md.BarrierData(barrier["_id"]).dump(),
        ))
    await send_reply(
        message=update.effective_message,
        text=text,
        reply_markup=InlineKeyboardMarkup.from_column(buttons),
    )


@add_handler_routines(
    answer_callback_query=False,
    check_is_allowed_to_open_barriers=True,
)
async def open_barrier_handler(update: Update, context: CallbackContext) -> None:
    await update.callback_query.answer(text="Открываю шлагбаум.")
    barrier_id = md.BarrierData.load(update.callback_query.data).barrier_id
    logger.info(barrier_id)
    barrier = db.get_barrier(barrier_id)
    accessible_barriers = db.get_user_attribute(update.effective_user.id, "barriers", default=[])
    if barrier["_id"] not in accessible_barriers:
        await send_reply(update.effective_message, text="Нет доступа к шлагбауму!")
    else:
        try:
            text = call_number(barrier["phone_number"])
        except Exception as e:
            text = str(e)
            await send_reply(
                message=update.effective_message,
                text=f"Позвонил на шлагбаум через API. Ошибка:\n{text}",
            )
