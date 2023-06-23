import json
import random
from pathlib import Path
from typing import List, Callable, Optional
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment, Message
from .config import Config
from src.plugins.globals import create_file, create_folder, data_path, JsonEncoder, extract_picture_from_cqmessage, \
    download_picture, replace_cqimage_with_path, extract_whole_picture


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
        self.max_record_count = self.record_config.repeat_max_record_count
        self.verify_func: List[Callable[[GroupMessageEvent], bool]] = []
        self.last_reply: Optional[Record] = None

    async def process(self, event: GroupMessageEvent, bot: Bot):
        if not isinstance(event, GroupMessageEvent):
            return
        for func in self.verify_func:
            if func(event):
                return

        self.__record_now_count += 1
        self.__reply_now_count += 1

        gr = self.get_group_record(event.group_id)
        if not gr.allow:
            return
        # 该记录一条数据了
        if self.__record_now_count >= self.__record_need_count:
            # 这个是要增加的记录
            url = extract_picture_from_cqmessage(event.raw_message)
            if url is None:
                r = Record(event.sender.user_id, event.sender.nickname, event.raw_message)
                gr.content.append(r)
                logger.info(f"增加记录: {r}")
            else:
                pic_path = self.picture_path / f"{event.message_id}"
                await download_picture(url, pic_path)
                msg = replace_cqimage_with_path(event.raw_message, url, pic_path)
                r = Record(event.sender.user_id, event.sender.nickname, msg)
                gr.content.append(r)
                logger.info(f"增加记录: {r}")
            # 加了之后看看有没有超出限制
            if len(gr.content) > self.max_record_count:
                r = gr.content.pop(0)
                file_path = extract_picture_from_cqmessage(r.content)
                if file_path is not None:
                    Path(file_path).unlink()
            self.save()
            self.__record_now_count = 0
            self.__record_need_count = random.randint(self.__record_random_min, self.__record_random_max)

        # 该回复一条信息了
        if self.__reply_now_count >= self.__reply_need_count:
            if len(gr.content) == 0:
                return
            record = random.choice(gr.content)
            msg = self.create_message(record)
            await bot.send(event, Message(msg))
            self.last_reply = record
            self.__reply_now_count = 0
            self.__reply_need_count = random.randint(self.__reply_random_min, self.__reply_random_max)

    def create_message(self, r: Record) -> str:
        file_path = extract_picture_from_cqmessage(r.content)
        if file_path is not None:
            # 说明有图片消息
            pic_whole = extract_whole_picture(r.content)
            msg = r.content.replace(pic_whole, "{}")
            msg = msg.format(MessageSegment.image(Path(file_path)))
            return msg
        else:
            return r.content

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
        gr = GroupRecord(group_id, [], False)
        self.content.append(gr)
        return gr

    def allow_group(self, group_id: int):
        gr = self.get_group_record(group_id)
        gr.allow = True
        self.save()

    def disallow_group(self, group_id: int):
        gr = self.get_group_record(group_id)
        gr.allow = False
        self.save()
