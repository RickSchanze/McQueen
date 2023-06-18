import json
import random
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from nonebot.log import logger
from .Wife import Wife
from .wifeconfig import WifeConfig
from src.plugins.globals import create_file, create_folder, work_path, JsonEncoder, download_picture
from nonebot.adapters.onebot.v11 import MessageSegment


class WifeManager:
    def __init__(self, config: WifeConfig):
        self.wives = []
        self.wife_config = config
        # 保存wife图片的文件夹
        self.picture_path: Optional[Path] = None
        # 保存wife数据的文件夹
        self.content_path: Optional[Path] = None
        # 保存wife数据的文件
        self.content_file: Optional[Path] = None
        # 抽签数据保存的文件
        self.roll_data_file: Optional[Path] = None
        # 抽签数据本身
        self.roll_data: Dict[str, int] = {}
        # 老婆数据本身
        self.wives_content: List[Wife] = []
        self.load_content()
        self.load_roll_data()

    ##########初始化阶段使用的函数#############

    def load_content(self):
        """Load or Create the path for wife"""
        self.content_path = create_folder(work_path, self.wife_config.wife_data_path)
        self.picture_path = create_folder(work_path, self.wife_config.wife_picture_path)
        self.content_file = create_file(self.content_path, self.wife_config.wife_content_file)
        with self.content_file.open('r', encoding='utf-8') as f:
            wifes = json.load(f)
            for wife in wifes:
                self.wives_content.append(Wife(**wife))

    def load_roll_data(self):
        self.roll_data_file = create_file(self.content_path, self.wife_config.wife_roll_file)
        try:
            with self.roll_data_file.open('r', encoding='utf-8') as f:
                self.roll_data = json.load(f)
        except Exception as e:
            logger.error(f"读取抽老婆数据失败,原因:{e},将重置抽老婆数据")
            self.roll_data = {}

    ########################################

    def save_roll(self):
        with self.roll_data_file.open('w', encoding='utf-8') as f:
            json.dump(self.roll_data, f, ensure_ascii=False, indent=4, cls=JsonEncoder)

    def save_wives_content(self):
        with self.content_file.open('w', encoding='utf-8') as f:
            json.dump(self.wives_content, f, ensure_ascii=False, indent=4, cls=JsonEncoder)

    def append_wife(self, wife: Wife):
        self.wives_content.append(wife)
        self.save_wives_content()

    def remove_wife(self, wife: Wife | str):
        if isinstance(wife, str):
            for w in self.wives_content:
                if w.name == wife:
                    Path(w.filename).unlink()
                    self.wives_content.remove(w)
        elif isinstance(wife, Wife):
            Path(wife.filename).unlink()
            self.wives_content.remove(wife)
        self.save_wives_content()

    def get_wife_by_name(self, name: str) -> Optional[Wife]:
        """
        通过名字获取老婆
        @param name:
        @return: 没有则None
        """
        for wife in self.wives_content:
            if wife.name == name:
                return wife
        return None

    def get_wife_by_index(self, index: int) -> Optional[Wife]:
        """
        通过index获取老婆
        @param index:
        @return: 没有则None
        """
        if index < len(self.wives_content):
            return self.wives_content[index]
        return None

    def roll_wife(self, roller: str) -> Tuple[Wife, Path] | None:
        """
        抽老婆
        @param roller:
        @return: 第一个参数是抽到老婆的信息，第二个参数是老婆图片的完整路径
        """
        if len(self.wives_content) == 0:
            return None
        if roller in self.roll_data.keys():
            wife_index = self.roll_data[roller]
            wife = self.get_wife_by_index(wife_index)
            return wife, self.picture_path / wife.filename
        else:
            wife_index = random.randint(0, len(self.wives_content) - 1)
            wife = self.get_wife_by_index(wife_index)
            self.roll_data[roller] = wife_index
            self.save_roll()
            return wife, self.picture_path / wife.filename

    async def prepare_wife_data(self, wife_name, wife_url) -> Optional[Path]:
        """
        返回老婆图片转换为CQ码后的字符串
        @param wife_name:
        @param wife_url:
        @return:
        """
        wife_path = self.picture_path / wife_name
        if await download_picture(wife_url, wife_path):
            print(wife_path)
            return wife_path
        return None
