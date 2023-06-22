from nonebot import get_driver
from nonebot.message import event_postprocessor
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent

from .config import Config
from .RecordManager import RecordManager

global_config = get_driver().config
config = Config.parse_obj(global_config)

record_manager = RecordManager(config)
print(record_manager.content)
record_manager.save()

@event_postprocessor
async def record_processor(bot: Bot, event: Event):
    if not isinstance(event, GroupMessageEvent):
        return
