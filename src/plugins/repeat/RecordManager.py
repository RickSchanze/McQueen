import json
import random
from typing import List, Callable
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from .config import Config
from src.plugins.globals import create_file, create_folder, data_path, JsonEncoder, extract_picture_from_cqmessage, \
    download_picture


class Record:
    def __init__(self, sender_qq: int, sender_nickname: str, content: str):
        self.sender_qq = sender_qq
        self.sender_nickname = sender_nickname
        self.content = content

    def __repr__(self):
        return f"<Record sender_qq={self.sender_qq} sender_nickname={self.sender_nickname} content={self.content}>"


class GroupRecord:
    def __init__(self, group_id: int, content: List[Record], allow: bool):
        self.allow = allow
        self.group_id = group_id
        self.content = content

    def __repr__(self):
        return f"<GroupRecord allow={self.allow} group_id={self.group_id} content={self.content}>"


class RecordManager:
    def __init__(self, record_config: Config):
        self.record_config = record_config
        self.__reply_random_min = self.record_config.repeat_reply_random_min
        self.__reply_random_max = self.record_config.repeat_reply_random_max
        self.__record_random_min = self.record_config.repeat_record_random_min
        self.__record_random_max = self.record_config.repeat_record_random_max
        self.__reply_need_count = random.randint(self.__reply_random_min, self.__reply_random_max)
        self.__record_need_count = random.randint(self.__record_random_min, self.__record_random_max)
        self.__reply_now_count = 0
        self.__record_now_count = 0
        self.data_path = create_folder(data_path, "repeat")
        self.picture_path = create_folder(self.data_path, "picture")
        self.content_file = create_file(self.data_path, "content.json")
        self.content = self.load()
        self.verify_func: List[Callable[[GroupMessageEvent], bool]] = []

    async def process(self, event: GroupMessageEvent, bot: Bot):
        if not isinstance(event, GroupMessageEvent):
            return
        for func in self.verify_func:
            if func(event):
                return

        self.__record_now_count += 1
        self.__reply_now_count += 1
        # TODO: 完成处理函数，先完成globals里的东西
        if self.__record_now_count >= self.__record_need_count:
            gr = self.get_group_record(event.group_id)
            url = extract_picture_from_cqmessage(event.raw_message)
            if url is None:
                gr.content.append(Record(event.sender.user_id, event.sender.nickname, event.raw_message))
            else:
                await download_picture(url, self.picture_path / f"{event.sender.nickname}_{event.message_id}")

    def load(self) -> List[GroupRecord]:
        try:
            with self.content_file.open("r", encoding='utf-8') as f:
                content = json.load(f)
                rtn = []
                for group in content:
                    gr = GroupRecord(group["group_id"], [], group["allow"])
                    for record in group["content"]:
                        gr.content.append(Record(record["sender_qq"], record["sender_nickname"], record["content"]))
                    rtn.append(gr)
                return rtn
        except Exception as e:
            logger.warning(f"加载失败，使用新建配置:{e}")
            return []

    def save(self):
        with self.content_file.open('w', encoding='utf-8') as f:
            json.dump(self.content, cls=JsonEncoder, indent=4, fp=f, ensure_ascii=False)

    def register_verify_func(self, func):
        self.verify_func.append(func)

    def get_group_record(self, group_id: int):
        for group in self.content:
            if group.group_id == group_id:
                return group
        return GroupRecord(group_id, [], False)
