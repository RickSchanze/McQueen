import json
import re
from typing import Optional
import httpx

from nonebot import get_driver

from .config import Config
from pathlib import Path
from nonebot.log import logger

global_config = get_driver().config
config = Config.parse_obj(global_config)

data_path = Path.cwd() / config.data_path
config_path = Path.cwd() / config.config_path
work_path = Path.cwd()


def create_folder(prefix: Path, folder: str) -> Optional[Path]:
    """
    在prefix文件夹下创建folder文件夹
    @rtype: object
    @param prefix:
    @param folder:
    @return: 创建好的folder(Path)或者None
    """
    if not prefix.is_dir():
        return None
    path = prefix / folder
    if not path.exists():
        path.mkdir(parents=True)
    return path


def create_file(prefix: Path, file: str) -> Optional[Path]:
    """
    在prefix文件夹下创建file文件
    @param prefix:
    @param file:
    @return: 创建好的file(Path)或者None
    """
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
    match = re.match(r'\[CQ:image.*?url=(\S+)]', message)
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


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        d = o.__dict__.copy()
        keys = d.keys()
        to_del = config.json_donot_encode
        for de in to_del:
            if de in keys:
                del d[de]
        return d
