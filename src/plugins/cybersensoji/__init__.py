from nonebot import get_driver
from nonebot.plugin import PluginMetadata

from .classdef import SensojiManager
from src.plugins.globals import data_path, PERMISSION_ADMIN, PERMISSION_SUPERUSER
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot import require

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

global_config = get_driver().config

sensoji_manager = SensojiManager(data_path)

get_sensoji = on_command("抽签")
sensoji_history = on_command("抽签历史")
refresh = on_command("刷新抽签", permission=PERMISSION_SUPERUSER)

__usage__ = r"""
普通命令:
  抽签
    抽一发，每个人每天抽到的都是一样的
  抽签历史
    查看自己的抽签历史
管理员命令:
  刷新抽签
    刷新今日所有的抽签记录，需要超级用户权限
"""

__plugin_meta__ = PluginMetadata(
    name="抽签",
    description="赛博浅草寺抽签！",
    usage=__usage__
)


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
