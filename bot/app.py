from typing import Optional
import logging

from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    CallbackQueryHandler,
    filters,
    AIORateLimiter,
)

from bot import config
import bot.handlers.manage_data as md
from bot.handlers.help import (
    start_handle,
    help_handle,
)
from bot.handlers.general import (
    error_handle,
    default_callback_handle,
)
from bot.handlers.admin import (
    user_contact_handler,
    choose_role_handler,
    give_access_handler,
)
from bot.handlers.main import (
    add_barrier_handler,
    show_barriers_handler,
    open_barrier_handler,
)


logger = logging.getLogger(__name__)


def run_bot() -> None:
    application = (
        ApplicationBuilder()
        # .base_url('http://bot-api:8081/bot')
        # .local_mode(True)
        # .base_file_url('http://bot-api:8081/file/bot')
        .token(config.telegram_token)
        .concurrent_updates(True)
        .rate_limiter(AIORateLimiter(max_retries=3))
        .http_version("1.1")
        .get_updates_http_version("1.1")
        .read_timeout(60)
        .write_timeout(60)
        .build()
    )

    # add handlers
    if len(config.allowed_telegram_usernames) == 0:
        user_filter = filters.ALL
    else:
        user_filter = filters.User(username=config.allowed_telegram_usernames)

    if len(config.admin_usernames) == 0:
        raise ValueError("You must specify at least 1 admin username in config")
    admin_filter = filters.User(username=config.admin_usernames)

    handlers = [
        CommandHandler("start", start_handle, filters=user_filter),
        CommandHandler("help", help_handle, filters=user_filter),
        MessageHandler(filters=filters.CONTACT, callback=user_contact_handler),
        CallbackQueryHandler(choose_role_handler, pattern=md.ChooseRoleData.pattern()),
        CallbackQueryHandler(give_access_handler, pattern=md.BarrierAccessData.pattern()),
        CommandHandler("add_barrier", add_barrier_handler, filters=user_filter),
        CommandHandler("open", show_barriers_handler, filters=user_filter),
        CallbackQueryHandler(open_barrier_handler, pattern=md.BarrierData.pattern()),
    ]

    application.add_handlers(handlers)
    application.add_handler(CallbackQueryHandler(default_callback_handle))
    application.add_error_handler(error_handle)
    application.run_polling()
