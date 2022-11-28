from asyncio.log import logger
from pathlib import Path
import random
from nonebot import get_driver, on_command, on_message
from nonebot.adapters.onebot.v11 import Message, Event, Bot, GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
import re, json

global_config = get_driver().config
# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

            
    
############################################################################
class RecordWord:
    def __init__(self, group_id, records, can_record_and_reply: bool = False, init: bool=True) -> None:
        """参数说明
        group_id:这个类对象代表的群号
        all_records:从前的记录
        lens: 记录长度
        record_order:当前是对记录第几个消息
        reply_order:当前对发送是第几个消息
        to_record:在第几个消息时记录
        to_reply:在第几个消息时发送
        Args:
            group_id (_type_): _description_
            json_file (_type_): _description_
        """
        self.group_id = str(group_id)
        self.all_records = [False, " "]
        if init:
            self.all_records = records
        self.lens = len(self.all_records)
        self.record_order = 0
        self.reply_order = 0
        self.to_record = random.randint(20, 40)
        self.to_reply = random.randint(30, 80)
        self.can_record_and_reply = can_record_and_reply
        
    def record_order_increment(self):
        self.record_order += 1
        
    def reply_order_increment(self):
        self.reply_order += 1
        
    def can_reply(self):
        return self.reply_order >= self.to_reply
    
    def can_record(self):
        return self.record_order >= self.to_record
    
    def reply(self):
        self.to_reply = random.randint(30, 80)
        self.reply_order = 0
        return self.get_a_word()

    def record(self):
        self.lens += 1
        self.to_record = random.randint(20, 40)
        self.record_order = 0
    
    def get_a_word(self):
        index = random.randint(1, self.lens - 1)
        while "reply" in self.all_records[index] or "at" in self.all_records[index]:
            index = (index + 1) % self.lens
        return self.all_records[index]
    
    def set_can_replay(self, key, can:bool):
        self.all_records[0] = can
        self.can_record_and_reply = can
        records[key] = self.all_records
        
    def append(self, message):
        self.all_records.append(message)
####################################################################################

work_directory = Path.absolute(Path.cwd())
json_path = work_directory / "data" / "record"

record_path = json_path / "record.json"
from ...utils import Utils
picture = Utils(json_path / "pictures")

json_file = None

with open(record_path, encoding='utf-8') as f:
    records = json.load(f)

change_can_open = on_command("开启复读", permission=GROUP_OWNER, priority=1, block=True)
change_can_close = on_command("关闭复读", permission=GROUP_OWNER, priority=1, block=True)
update = on_message(priority=100)

record_list = {}

for key, value in records.items():
    record_list[key] = RecordWord(key, value, can_record_and_reply=value[0])
        
        
@change_can_close.handle()
async def change_can_close_handler(bot: Bot, event: Event):
    group_id = str(event.group_id)
    record: RecordWord = record_list[group_id]
    record.set_can_replay(group_id, False)
    with open(record_path, 'w', encoding='utf-8') as f:
        json.dump(records, f,ensure_ascii=False, indent=4)
    await bot.send(event=event, message="已关闭学习复读")
    
@change_can_open.handle()
async def change_can_open_handler(bot: Bot, event: Event):
    group_id = str(event.group_id)
    record: RecordWord = record_list[group_id]
    record.set_can_replay(group_id, True)
    with open(record_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)
    await bot.send(event=event, message="已开启学习复读")

@update.handle()
async def update_handler(bot: Bot, event: Event):
    message = event.raw_message
    group_id = str(event.group_id)
    
    if group_id not in record_list.keys():
        record_list[group_id] = RecordWord(group_id, None, init=False)
        record_list[group_id].set_can_replay(group_id, False)
        with open(record_path, 'w', encoding='utf-8') as f:
            json.dump(records, f,ensure_ascii=False, indent=4)
            
    record = record_list[group_id]
    
    if record.can_record_and_reply:
        record.record_order_increment()
        record.reply_order_increment()
        if record.can_record():
            is_picture = picture.get_picture_urls(message=message)
            if is_picture != -1:
                try:
                    pattern = '\[CQ:image,file=(.*?)\]'
                    a, b = re.search(pattern, message).span()
                    to_record = message.replace(message[a:b], picture.get_a_picture(picture.len))
                    await picture.get_and_write(message)
                    record.append(to_record)
                    with open(record_path, 'w', encoding='utf-8') as f:
                        json.dump(records, f,ensure_ascii=False, indent=4)
                except Exception as e:
                    logger.error("增加失败")
            else:
                record.append(message)
                with open(record_path, 'w', encoding='utf-8') as f:
                    json.dump(records, f,ensure_ascii=False, indent=4)
            record.record()
                
        if record.can_reply():
            await bot.send(event=event, message=Message(record.reply()))
                    
