from abc import abstractmethod
from typing import List
from .config import Config
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger
import src.plugins.globals as utils

# TODO: 扩展各种过滤器与处理器
class Record:
    sender_qq: int
    sender_nickname: str
    content: str

    def __init__(self, sender_qq: int, sender_nickname: str, content: str):
        self.sender_qq = sender_qq
        self.sender_nickname = sender_nickname
        self.content = content

    def __str__(self):
        return f'Record({self.sender_qq}, {self.sender_nickname}, {self.content})'

    def __repr__(self):
        return f'Record({self.sender_qq}, {self.sender_nickname}, {self.content})'


class RecordFilter:
    reason = '未知原因'

    @abstractmethod
    def filter(self, message: GroupMessageEvent) -> bool:
        pass


record_filters: List[RecordFilter] = []


class MessageProcessor:
    priority: int

    @abstractmethod
    def process(self, message: GroupMessageEvent) -> bool:
        """
        处理消息,返回True则不会继续处理之后的消息
        """
        pass

    @staticmethod
    def register_processor(priority: int):
        def _register_processor(cls):
            p = cls()
            p.priority = priority
            message_processors.append(p)
            message_processors.sort(key=lambda x: x.priority, reverse=True)
        return _register_processor


message_processors: List[MessageProcessor] = []


@MessageProcessor.register_processor(priority=100)
class RecordProcessor(MessageProcessor):

    def process(self, message: GroupMessageEvent) -> bool:
        pass


class GroupRecords:
    group_id: int
    content: List[Record]
    allow: bool = False
    __now_record_count: int = 0
    __now_reply_count: int = 0

    def __init__(self, group_id: int, content: List[Record], allow: bool):
        self.group_id = group_id
        self.content = content
        self.allow = allow

    def add_record(self, record: Record):
        self.content.append(record)

    def __str__(self):
        return f'GroupRecords({self.group_id}, {self.content}, {self.allow})'

    def __repr__(self):
        return f'GroupRecords({self.group_id}, {self.content}, {self.allow})'


def _filter(message: GroupMessageEvent) -> bool:
    if message is not GroupMessageEvent:
        logger.error(f'消息{message.message_id}不是GroupMessageEvent类型')
        return False
    for record_filter in record_filters:
        if not record_filter.filter(message):
            logger.info(f'消息{message.message_id}被过滤器{record_filter}过滤, 原因: {record_filter.reason}')
            return False
    return True


def _process(message: GroupMessageEvent):
    if _filter(message):
        for message_processor in message_processors:
            if message_processor.process(message):
                logger.info(f'消息{message.message_id}被处理器{message_processor}处理')
                return


class RecordManager:
    records: List[GroupRecords]

    def __init__(self, config: Config):
        self.data_path = utils.get_data_path('record')
        self.pic_path = utils.create_directory(self.data_path, 'pictures')
        self.data_file = utils.create_file(self.data_path, 'records.json')
        self.record_min_count = config.record_min_count
        self.record_max_count = config.record_max_count
        self.reply_min_count = config.reply_min_count
        self.reply_max_count = config.reply_max_count
        try:
            data = utils.read_file(self.data_file)
            self.records = [GroupRecords(**record) for record in data]
        except Exception as e:
            print(e)
            self.records = []
            self.append(GroupRecords(0, [], False))

    def __str__(self):
        return f'RecordManager({self.records})'

    def __repr__(self):
        return f'RecordManager({self.records})'

    def __del__(self):
        self.save()

    def append(self, record: GroupRecords):
        self.records.append(record)
        self.save()

    def append_record_to_group(self, group_id: int, record: Record):
        for group_record in self.records:
            if group_record.group_id == group_id:
                group_record.add_record(record)
                break
        else:
            self.append(GroupRecords(group_id, [record], True))

    def save(self):
        save_json = [record.__dict__ for record in self.records]
        utils.write_file(self.data_file, save_json)

    @staticmethod
    def register_filter(cls):
        record_filters.append(cls())
