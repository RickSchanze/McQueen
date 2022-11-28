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
from nonebot.rule import to_me

util = Utils(Path.absolute(Path(__file__).parent.parent.parent.parent) / "data"/ "eatwhat" / "pictures")
contentpath = Path.absolute(Path(Path(__file__).parent.parent.parent.parent) / "data"/ "eatwhat" / "content.json")
    
with open(contentpath, encoding='utf-8') as f:
    content = json.load(f)
    
get_dinner = on_command("待会吃什么", rule=to_me(), aliases={"吃什么", "今天吃什么"})
append_dinner = on_command("加饭", rule=to_me(), permission=GROUP_ADMIN | GROUP_OWNER)

require("nonebot_plugin_apscheduler")

@get_dinner.handle()
async def get_wife_handeler(bot: Bot, event: Event):
    if len(content) != 0:
        index, message = util.get_a_picture_path()
        name = content[index]["name"]
        await bot.send(event=event, message=Message(f"待会吃{message}{name}!"), at_sender=True)
    else:
        await bot.send(event=event, message=Message(f"现在没饭了！！"))
    
@append_dinner.handle()
async def append_wife_handler(bot: Bot, event: Event):
    global config, content
    user_id = str(event.get_user_id())
    raw_message = event.raw_message
    messages = raw_message.split(' ')
    name = ""
    try:
        if len(messages) == 3:
            name = messages[1]
            url = messages[2]
            content.append({"name": name, "author": user_id})
            await util.get_and_write(url)
            await bot.send(event=event, message=f"添加成功！{name}！", at_sender=True)
        else:
            await bot.send(event=event, message="正确的输入格式应为：\"加饭\" 名字 图片", at_sender=True)
            
        with open(contentpath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        await bot.send(event=event, message=f"由于某些异常，添加失败了", at_sender=True)
        logger.error(e)
