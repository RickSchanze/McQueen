from pathlib import Path
import os
import nonebot
import random
from nonebot import require
from nonebot import get_driver, get_bot, on_command
from nonebot.adapters.onebot.v11 import Message, Event, Bot, GROUP_ADMIN, GROUP_OWNER
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
import json


# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "plugins").
    resolve()))


work_directory = Path.absolute(Path.cwd())
json_path = work_directory / "data" / "goodmorning"
json_file = json_path / "config.json"

with open(json_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 早上好
@scheduler.scheduled_job("cron", hour=7, minute=30, misfire_grace_time=60)
async def good_morning():
    bot = get_bot()
    mor_images_dir = Path.absolute(Path.cwd() / "src" / "plugins" / "goodmorning" / "morning")
    mor_images_file = os.listdir(mor_images_dir)
    mor_images_dir_p = str(mor_images_dir).replace('\\', '/')
    for item in config:
        index = random.randint(0, len(mor_images_file) - 1)
        await bot.call_api("send_msg", 
                        message_type="group", 
                        group_id=item, 
                        message=Message(f"[CQ:image,file=file:///{mor_images_dir_p}/{mor_images_file[index]}]"))

# 晚上好
@scheduler.scheduled_job("cron", hour=23, minute=53, misfire_grace_time=60)
async def good_evening():
    bot = get_bot()
    env_images_dir = Path.absolute(Path.cwd() / "src" / "plugins" / "goodmorning" / "evening")
    env_images_file = os.listdir(env_images_dir)
    env_images_dir_p = str(env_images_dir).replace('\\', '/')
    for item in config:
        index = random.randint(0, len(env_images_file) - 1)
        await bot.call_api("send_msg", 
                        message_type="group", 
                        group_id=item, 
                        message=Message(f"[CQ:image,file=file:///{env_images_dir_p}/{env_images_file[index]}]"))
        
        
append_group = on_command("定时早晚安", permission=GROUP_ADMIN | GROUP_OWNER)
@append_group.handle()
async def append_handle(bot: Bot, event: Event):
    global config_
    group_id = event.group_id
    if str(group_id) not in config_:
        config_.append(str(event.group_id))
    with open(json_file, 'w', encoding='utf-8') as f:
        config_ = json.dump(config_, f, ensure_ascii=False, indent=4)
    await bot.send(event=event, message="OK!")
    
delete = on_command("取消早晚安", permission=GROUP_ADMIN | GROUP_OWNER)
@delete.handle()
async def delete_handle(bot: Bot, event: Event):
    global config_
    group_id = event.group_id
    if str(group_id) in config_:
        del config_[config_.index(str(group_id))]
    with open(json_file, 'w', encoding='utf-8') as f:
        config_ = json.dump(config_, f, ensure_ascii=False, indent=4)
    await bot.send(event=event, message="OK!")
    