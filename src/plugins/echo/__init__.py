from nonebot import get_driver
from nonebot import on_command

from .config import EchoConfig

global_config = get_driver().config

config = EchoConfig.parse_obj(global_config)

# Commands
echo = on_command("echo", priority=5)


@echo.handle()
async def echo_handle(bot, event):
    await echo.finish(event.get_message())
