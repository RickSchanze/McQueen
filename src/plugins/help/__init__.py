from nonebot import get_driver, on_command
from nonebot.rule import to_me
from pathlib import Path
from nonebot.adapters.onebot.v11 import Bot, Event, Message

# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

help = on_command("帮助", rule=to_me(), aliases={"help", "菜单"})
help_path = Path.absolute(Path.cwd()) / "help.png"
help_path = str(help_path).replace('\\', '/')
@help.handle()
async def help_handler(bot: Bot, event:Event):
    await bot.send(event=event, message=Message(f"[CQ:image,file=file:///{help_path}]"))