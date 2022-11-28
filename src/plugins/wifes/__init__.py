# from nonebot import get_driver

# global_config = get_driver().config

# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass
from random import random
from nonebot.log import logger
import json
from ...utils import Utils
from pathlib import Path
from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER, Event, Bot, Message
from nonebot.params import CommandArg

util = Utils(Path.absolute(Path(__file__).parent.parent.parent.parent) / "data"/ "wifes" / "pictures")
jsonpath = Path(Path.absolute(Path(__file__).parent.parent.parent.parent)) / "data"/ "wifes" / "config.json"
contentpath = Path.absolute(Path(Path(__file__).parent.parent.parent.parent)) / "data"/ "wifes" / "content.json"

with open(jsonpath, encoding='utf-8') as f:
    config = json.load(f)
    
with open(contentpath, encoding='utf-8') as f:
    content = json.load(f)
    
get_wife = on_command("抽老婆")
append_wife = on_command("增加老婆", permission=GROUP_ADMIN | GROUP_OWNER)

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

@get_wife.handle()
async def get_wife_handeler(bot: Bot, event: Event, args: Message=CommandArg()):
    global config
    given_name = args.extract_plain_text()
    if given_name.strip() == "" or given_name.strip() == "自己":
        given_name = event.sender.nickname

    if given_name in config.keys():
        index = config[given_name]
        message = util.get_a_picture(index)
    else: 
        index, message = util.get_a_picture_path()
        
    name = content[index]["name"]
    description = content[index]["description"]
    config[given_name] = index
    with open(jsonpath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    await bot.send(event=event, message=Message(f"{given_name}抽到了\n{message}{name}\n{description}"))
    
@append_wife.handle()
async def append_wife_handler(bot: Bot, event: Event):
    global config, content
    user_id = str(event.get_user_id())
    raw_message = event.raw_message
    messages = raw_message.split(' ')
    description = ""; name = ""
    try:
        if len(messages) == 3:
            name = messages[1]
            url = messages[2]
            content.append({"name": name, "description": description, "author": user_id})
            await util.get_and_write(url)
            await bot.send(event=event, message=f"添加成功！{name}已入老婆池！", at_sender=True)
        elif len(messages) == 4:
            name = messages[1]
            description = messages[2]
            url = messages[3]
            content.append({"name": name, "description": description, "author": user_id})
            await util.get_and_write(url)
            await bot.send(event=event, message=f"添加成功！{name}已入老婆池！", at_sender=True)
        else:
            await bot.send(event=event, message="正确的输入格式应为：\"增加老婆\" 名字 描述 图片，其中描述可选", at_sender=True)
            
        with open(contentpath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        await bot.send(event=event, message=f"由于某些异常，添加失败了", at_sender=True)
        logger.error(e)
        
@scheduler.scheduled_job("cron", hour=00, minute=00, misfire_grace_time=60)
async def _():
    global config
    config = {}
    with open(jsonpath, 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)