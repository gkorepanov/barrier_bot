import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from bot.handlers.utils import (
    add_handler_routines,
    send_reply,
)
from bot.database import db
from bot.handlers import manage_data as md


logger = logging.getLogger(__name__)


def make_user_keyboard(
    contact_user_id: int,
    current_role: Optional[md.Role] = None,
) -> InlineKeyboardMarkup:
    role_to_text = {
        md.Role.ADMIN: "Администратор",
        md.Role.USER: "Пользователь",
        md.Role.BANNED: "Запретить доступ",
    }
    buttons = []
    for role in md.Role:
        text = role_to_text[role]
        if role == current_role:
            text = f"✅ {text}"
        button = InlineKeyboardButton(
            text=text,
            callback_data=md.ChooseRoleData(role=role, user_id=contact_user_id).dump(),
        )
        buttons.append(button)
    return InlineKeyboardMarkup.from_column(buttons)


def make_user_access_barriers_keyboard(
    contact_user_id: int,
    admin_user_id: int, 
) -> InlineKeyboardMarkup:
    buttons = []
    db.add_or_update_user(contact_user_id)
    all_barriers = db.get_user_attribute(admin_user_id, "barriers", default=[])
    accessible_barriers = db.get_user_attribute(contact_user_id, "barriers", default=[])
    for i, barrier_id in enumerate(all_barriers, start=1):
        barrier = db.get_barrier(barrier_id)
        name = barrier["name"].replace("_", " ")
        button_text = f"{i}. {name}\n"
        if barrier_id in accessible_barriers:
            button_text = f"✅ {button_text}"
        buttons.append(InlineKeyboardButton(
            text=button_text,
            callback_data=md.BarrierAccessData(barrier_id=barrier["_id"], user_id=contact_user_id).dump(),
        ))
    return InlineKeyboardMarkup.from_column(buttons)


@add_handler_routines(
    check_is_admin=True,
)
async def user_contact_handler(update: Update, context: CallbackContext) -> None:
    contact = update.message.contact
    contact_user_id = contact.user_id
    name = f"{contact.first_name} {contact.last_name}"
    await send_reply(
        message=update.effective_message,
        text=f"Выберите роль для пользователя {name}:",
        reply_markup=make_user_keyboard(contact_user_id, current_role=md.Role.BANNED),
        send_as_reply=True,
    )
    await send_reply(
         message=update.effective_message,
        text=f"Выберите к каким шлагбаумам дать доступ пользователю {name}:",
        reply_markup=make_user_access_barriers_keyboard(
            contact_user_id=contact_user_id,
            admin_user_id=update.effective_user.id
        ),
        send_as_reply=True,
    )


@add_handler_routines(
    check_is_admin=True,
    answer_callback_query=True,
)
async def choose_role_handler(update: Update, context: CallbackContext) -> None:
    data = md.ChooseRoleData.load(update.callback_query.data)
    user_id = data.user_id
    role = data.role
    db.add_or_update_user(user_id, role=role.value)
    await send_reply(
        message=update.effective_message,
        text=update.effective_message.text,
        reply_markup=make_user_keyboard(user_id, role),
        try_edit=True,
    )


@add_handler_routines(
    check_is_admin=True,
    answer_callback_query=True,
)
async def give_access_handler(update: Update, context: CallbackContext) -> None:
    data = md.BarrierAccessData.load(update.callback_query.data)
    db.switch_barrier_access_for_user(
        barrier_id=data.barrier_id,
        user_id=data.user_id,
    )
    await send_reply(
        message=update.effective_message,
        text=update.effective_message.text,
        reply_markup=make_user_access_barriers_keyboard(data.user_id, update.effective_user.id),
        try_edit=True,
    )
