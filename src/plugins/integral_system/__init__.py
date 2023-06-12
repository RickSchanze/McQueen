from nonebot import get_driver

from .config import Config
from .user_manager import UserManager

global_config = get_driver().config
config = Config.parse_obj(global_config)

user_manager = UserManager(config)
