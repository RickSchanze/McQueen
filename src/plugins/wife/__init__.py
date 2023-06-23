import re

from nonebot import get_driver, on_command

from .Wife import Wife
from .wifeconfig import WifeConfig
from .WifeManager import WifeManager
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from src.plugins.globals import extract_picture_from_cqmessage
from pathlib import Path
from nonebot.plugin import PluginMetadata

global_config = get_driver().config
config = WifeConfig.parse_obj(global_config)

wife_manager = WifeManager(config)

add_wife = on_command("增加老婆")
remove_wife = on_command("删除老婆")
show_wife = on_command("查看老婆")
roll_wife = on_command("抽老婆")


__usage__ = r"""
基本命令：
  抽老婆 [<抽取者名称>]   
    若抽取者名称为空，则默认为发送者昵称，每个名字每天抽取到内容一致
管理员命令:
  增加老婆 <名称> <图片> [<描述>]
    想老婆池里增加一个老婆，此命令可能在电脑端失效
  删除老婆 <名称>
    从老婆池里删除一个老婆
  查看老婆 <名称|索引>
    查看老婆池里的老婆，可以通过名字或者下标查看
"""

__plugin_meta__ = PluginMetadata(
    name="抽老婆",
    description="每日一抽，开启一天好心情!",
    usage=__usage__
)


@add_wife.handle()
async def add_wife_handle(event: MessageEvent):
    msg = event.raw_message
    pattern = r'增加老婆\s+(\S+)\s+(\S+)(?:\s+(\S+))?'
    match = re.match(pattern, msg)
    # 提取命令参数
    if match is not None:
        wife_name = match.group(1)
        wife_pic = match.group(2)
        wife_pic = extract_picture_from_cqmessage(wife_pic)
        if wife_pic is None:
            logger.info(f"命令格式错误:{msg}")
            await add_wife.finish("正确格式为:增加老婆 <名称> <图片> [<描述>]")
            return
        # 下载本地图片
        wife_pic = await wife_manager.prepare_wife_data(wife_name, wife_pic)
        if wife_pic is not None:
            wife_disc = match.group(3)
            print(wife_pic)
            wife = wife_manager.get_wife_by_name(wife_name)
            if wife is not None:
                wife.filename = str(wife_pic)
                wife.description = wife_disc
            else:
                wife = Wife(name=wife_name, description=wife_disc, author=event.user_id, filename=str(wife_pic),
                            author_nickname=event.sender.nickname)
                wife_manager.append_wife(wife)
            wife_manager.save_wives_content()
            await add_wife.finish(f"成功添加老婆:{wife_name}")
        else:
            logger.error(f"下载图片失败:{wife_pic}")
            await add_wife.finish(f"增加老婆失败,请尝试使用手机增加或者联系管理员")
    else:
        logger.info(f"命令格式错误:{msg}")
        await add_wife.finish("正确格式为:增加老婆 <名称> <图片> [<描述>]")


@remove_wife.handle()
async def remove_wife_handle(event: MessageEvent):
    msg = event.raw_message
    pattern = r'删除老婆\s+(\S+)'
    match = re.match(pattern, msg)
    # 提取命令参数
    if match is not None:
        wife_name = match.group(1)
        wife = wife_manager.get_wife_by_name(wife_name)
        if wife is not None:
            wife_manager.remove_wife(wife)
            wife_manager.save_wives_content()
            await remove_wife.finish(f"成功删除老婆:{wife_name}")
        else:
            await remove_wife.finish(f"删除老婆失败,不存在老婆:{wife_name}")
    else:
        logger.info(f"命令格式错误:{msg}")
        await remove_wife.finish("正确格式为:删除老婆 <名称>")


@show_wife.handle()
async def show_wife_handle(event: MessageEvent):
    msg = event.raw_message
    pattern = r'查看老婆\s+(\S+)'
    match = re.match(pattern, msg)
    # 提取命令参数
    if match is not None:
        wife_name = match.group(1)
        if wife_name.isdigit():
            wife = wife_manager.get_wife_by_index(int(wife_name))
        else:
            wife = wife_manager.get_wife_by_name(wife_name)
        if wife is not None:
            msg = str(MessageSegment.text(
                f"老婆:{wife_name}\n描述:{wife.description}\n作者:{wife.author_nickname}") + MessageSegment.image(
                Path(wife.filename)))
            await show_wife.finish(message=msg)
        else:
            await show_wife.finish(f"查看老婆失败,不存在老婆:{wife_name}")
    else:
        logger.info(f"命令格式错误:{msg}")
        await show_wife.finish("正确格式为:查看老婆 <名称>")


@roll_wife.handle()
async def roll_wife_handle(event: MessageEvent):
    msg = event.raw_message
    pattern = r'抽老婆\s*(\S*)'
    match = re.match(pattern, msg)
    if match is not None:
        roller_name = event.sender.nickname if match.group(1) == "" else match.group(1)
        wife, path = wife_manager.roll_wife(roller_name)
        msg = str(MessageSegment.text(f"{roller_name}抽到了{wife.name}") + MessageSegment.image(Path(wife.filename)))
        await roll_wife.finish(message=msg, at_sender=True)
