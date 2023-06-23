from nonebot import get_driver, get_loaded_plugins

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

plugins = get_loaded_plugins()

# TODO: 扩展此插件

