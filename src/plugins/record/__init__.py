from nonebot import get_driver
from .record import RecordManager
from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

record_manager = RecordManager(config)

