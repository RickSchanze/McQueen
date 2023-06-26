import json
import re
import random
from typing import Optional
import httpx

from nonebot import get_driver
from nonebot.plugin import PluginMetadata

from .config import Config
from pathlib import Path
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER

global_config = get_driver().config
config = Config.parse_obj(global_config)

data_path = Path.cwd() / config.data_path
config_path = Path.cwd() / config.config_path
work_path = Path.cwd()

PERMISSION_ADMIN = SUPERUSER | GROUP_ADMIN | GROUP_OWNER
PERMISSION_SUPERUSER = SUPERUSER

__usage__ = r"""
指令	                权限	    需要@	   范围	    说明
open [数量] [名称]	群员	    否	       群聊	开启武器箱
cases	            群员	    否	       群聊	查看所有武器箱
svs	                群员	    否	       群聊	查看所有纪念包
s_skins	            群员	    否	       群聊	搜索皮肤
效果图
"""

__plugin_meta__ = PluginMetadata(
    name="csgo开箱模拟器",
    description="无成本体验csgo的开箱!",
    usage=__usage__
)


def create_folder(prefix: Path, folder: Optional[str] = None) -> Optional[Path]:
    """
    在prefix文件夹下创建folder文件夹
    @rtype: object
    @param prefix:
    @param folder:
    @return: 创建好的folder(Path)或者None
    """
    if folder is None:
        if not prefix.exists():
            prefix.mkdir(parents=True)
        return prefix

    if not prefix.is_dir():
        return None
    path = prefix / folder
    if not path.exists():
        path.mkdir(parents=True)
    return path


def create_file(prefix: Path, file: Optional[str] = None) -> Optional[Path]:
    """
    在prefix文件夹下创建file文件
    @param prefix:
    @param file: 若为None，则直接创建prefix文件
    @return: 创建好的file(Path)或者None
    """
    if file is None:
        if not prefix.is_file():
            return None
        if not prefix.exists():
            prefix.touch()
        return prefix
    if not prefix.is_dir():
        return None
    path = prefix / file
    if not path.exists():
        path.touch()
    return path


def extract_picture_from_cqmessage(message: str) -> Optional[str]:
    """
    从CQ:Image的消息里提取出图像链接
    @param message:
    @return: 没有则返回None
    """
    match = re.match(r'.*\[CQ:image.*?url=(\S+)].*', message)
    if match is not None:
        return match.group(1)
    return None


def extract_whole_picture(message: str) -> Optional[str]:
    """
    从CQ:Image的消息里提取出整个CQ:Image消息
    @param message:
    @return:
    """
    match = re.match(r'.*(\[CQ:image.*?url=\S+]).*', message)
    if match is not None:
        return match.group(1)
    return None


async def download_picture(url: str, path: Path) -> bool:
    """
    使用httpx异步下载图片
    @param url:
    @param path:
    @return:
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            print(url)
            r = await client.get(url)
            if r.is_success:
                with path.open('wb') as f:
                    f.write(r.content)
                return True
            else:
                logger.error(f"下载图片{url}失败,状态码:{r.status_code}")
                return False
        except Exception as e:
            logger.error(f"下载图片{url}失败,原因:{e}")
            return False


def replace_cqimage_with_path(msg: str, url: str, path: Path) -> str:
    """
    将CQ:Image消息中的url替换为path
    @param msg:
    @param url:
    @param path:
    @return:
    """
    return msg.replace(url, str(path))


def get_random_file_path(path: Path) -> Path:
    """
    从给定文件夹里随机获取一个文件
    注意：子文件夹里面的也会遍历
    :param path:
    :return:
    """
    if path.is_dir():
        while True:
            rtnpath = random.choice(list(path.iterdir()))
            if rtnpath.is_file():
                return rtnpath


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        d = o.__dict__.copy()
        keys = d.keys()
        to_del = config.json_donot_encode
        for de in to_del:
            if de in keys:
                del d[de]
        return d
