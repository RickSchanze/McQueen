from nonebot import get_driver, on_command
from nonebot.message import event_postprocessor
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, Message
from nonebot.rule import to_me
from .config import Config
from .RecordManager import RecordManager
from src.plugins.globals import PERMISSION_ADMIN

global_config = get_driver().config
config = Config.parse_obj(global_config)

record_manager = RecordManager(config)
enable_record = on_command("开启复读", permission=PERMISSION_ADMIN, block=True, rule=to_me())
disable_record = on_command("关闭复读", permission=PERMISSION_ADMIN, block=True, rule=to_me())
last_reply = on_command("上一条", aliases={"上一句"}, permission=PERMISSION_ADMIN, block=True, rule=to_me())


@record_manager.register_verify_func
def do_not_record_at(event: GroupMessageEvent):
    if event.raw_message.count('[CQ:at') > 0:
        return True
    return False


@record_manager.register_verify_func
def do_not_record_reply(event: GroupMessageEvent):
    if event.raw_message.count("[CQ:reply") > 0:
        return True
    return False


@record_manager.register_verify_func
def do_not_record_multy_pic(event: GroupMessageEvent):
    if event.raw_message.count("[CQ:image") > 1:
        return True
    return False


@record_manager.register_verify_func
def do_not_record_video(event: GroupMessageEvent):
    if event.raw_message.count("[CQ:video") > 0:
        return True
    return False


@record_manager.register_verify_func
def do_not_record_self(event: GroupMessageEvent):
    if event.user_id == event.self_id:
        return True
    return False


@event_postprocessor
async def record_processor(bot: Bot, event: Event):
    if not isinstance(event, GroupMessageEvent):
        return
    await record_manager.process(event, bot)


@enable_record.handle()
async def enable_record_handle(event: Event):
    if not isinstance(event, GroupMessageEvent):
        return
    record_manager.allow_group(event.group_id)
    await enable_record.finish("已开启复读")


@disable_record.handle()
async def disable_record_handle(event: Event):
    if not isinstance(event, GroupMessageEvent):
        return
    record_manager.disallow_group(event.group_id)
    await disable_record.finish("已关闭复读")


@last_reply.handle()
async def last_reply_handle(event: Event):
    if not isinstance(event, GroupMessageEvent):
        return
    if record_manager.last_reply is None:
        await last_reply.finish("没有记录")
    else:
        msg = record_manager.create_message(record_manager.last_reply)
        await last_reply.finish(
            Message(f"上一次复读的内容是：\n{msg}\n是{record_manager.last_reply.sender_nickname}说的"))
