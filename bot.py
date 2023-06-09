import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.database.db_api import on_startup_database
from tgbot.filters.admin_check import AdminFilter
from tgbot.handlers.admin.main_handlers import register_start_admin_handlers
from tgbot.handlers.admin.order.main_order import register_main_order_handlers
from tgbot.handlers.admin.order.show_orders import register_show_order_handlers
from tgbot.handlers.admin.support_handlers.support_call_main import register_support_main_admin_handlers
from tgbot.handlers.admin.support_handlers.support_order import register_support_call_admin_handlers
from tgbot.handlers.admin.portfolio.edit_portfolio import register_edit_portfolio_admin_handlers
from tgbot.handlers.admin.portfolio.portfolio_handlers import register_portfolio_admin_handlers
from tgbot.handlers.admin.portfolio.show_portfolio import register_show_portfolio_admin_handlers
from tgbot.handlers.user.order_handlers.main_make_order import register_main_make_order_handlers
from tgbot.handlers.user.order_handlers.main_order import register_main_order_user_handlers
from tgbot.handlers.user.order_handlers.make_brownie_order import register_make_brownie_order_handlers
from tgbot.handlers.user.order_handlers.make_cake_in_glass_order import register_make_cake_in_glass_order_handlers
from tgbot.handlers.user.order_handlers.make_cake_order import register_make_cake_order_handlers
from tgbot.handlers.user.portfolio_handlers.show_portfolio import register_show_portfolio_user_handlers
from tgbot.handlers.user.start_user_handler import register_start_user_handlers
from tgbot.handlers.user.support_handlers.support_call import register_support_call_user_handlers
from tgbot.handlers.user.support_handlers.support_call_main import register_support_main_user_handlers
from tgbot.middlewares.support_middleware import SupportMiddleware
from tgbot.misc.default_commands import set_default_commands

logger = logging.getLogger(__name__)

config = load_config(".env")
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def register_all_middlewares(dp, config):
    dp.setup_middleware(SupportMiddleware())
    pass


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_start_user_handlers(dp)
    register_show_portfolio_user_handlers(dp)
    register_main_order_user_handlers(dp)

    register_main_make_order_handlers(dp)
    register_make_cake_order_handlers(dp)
    register_make_cake_in_glass_order_handlers(dp)
    register_make_brownie_order_handlers(dp)

    register_start_admin_handlers(dp)
    register_portfolio_admin_handlers(dp)
    register_show_portfolio_admin_handlers(dp)
    register_edit_portfolio_admin_handlers(dp)

    register_support_call_admin_handlers(dp)
    register_support_call_user_handlers(dp)
    register_support_main_user_handlers(dp)
    register_support_main_admin_handlers(dp)

    register_main_order_handlers(dp)
    register_show_order_handlers(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    bot['config'] = config

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        await on_startup_database(dp)
        await set_default_commands(bot)
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
