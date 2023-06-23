from nonebot import get_driver
from .classdef import SensojiManager
from src.plugins.globals import data_path, PERMISSION_ADMIN
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot import require

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

global_config = get_driver().config

sensoji_manager = SensojiManager(data_path)

get_sensoji = on_command("抽签")
sensoji_history = on_command("抽签历史")
refresh = on_command("刷新抽签", permission=PERMISSION_ADMIN)


@get_sensoji.handle()
async def get_sensoji_handler(bot: Bot, event: GroupMessageEvent):
    message = await sensoji_manager.get(event)
    await bot.send(event=event, message=message, at_sender=True)


@sensoji_history.handle()
async def sensoji_history_handle(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event, message=sensoji_manager.get_history(str(event.get_user_id())), at_sender=True)


@scheduler.scheduled_job("cron", hour=00, minute=00, misfire_grace_time=60)
async def _():
    sensoji_manager.clear()


@refresh.handle()
async def refresh_handler():
    sensoji_manager.clear()
