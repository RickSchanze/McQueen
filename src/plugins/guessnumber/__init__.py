from nonebot.log import logger
from pathlib import Path
import random
from typing import List
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, Event, Bot, GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
import re, json
from nonebot.rule import to_me

work_directory = Path.absolute(Path.cwd())
json_path = work_directory / "data" / "guessnumber"
json_file = json_path / "config.json"

group_number = {}
group_times = {}

with open(json_file, 'r', encoding='utf-8') as f:
     allow_groups: List[str] = json.load(f)
     

allow_guess_number = on_command("开启猜数", rule=to_me(), permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
begin_guess_number = on_command("开始猜数", rule=to_me())     
forbid_guess_number = on_command("关闭猜数", rule=to_me(), permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
end_guess_number = on_command("结束猜数", rule=to_me(), permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
guess_number = on_command("我猜")

def generate_a_number(num: int) -> List[int]:
    """
    生成一个num位随机数，且这个随机数四个数字各不相同
    """
    if num >= 10:
        return 'None'
    num_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    rtn = random.sample(num_list, num)
    print(f"这次生成的数位{''.join(rtn)}")
    return rtn
    
@allow_guess_number.handle()
async def allow_guess_number_handle(bot: Bot, event: Event):
    group_id = str(event.group_id)
    if group_id not in allow_groups:
        allow_groups.append(group_id)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(allow_groups, f, ensure_ascii=False)
        await bot.send(event=event, message="已开启猜数游戏！", at_sender=True)
        
@begin_guess_number.handle()
async def begin_guess_number_handle(bot: Bot, event: Event):
    group_id = str(event.group_id)
    if group_id not in allow_groups:
        return
    if group_id not in group_number.keys():
        group_number[group_id] = generate_a_number(4)
        group_times[group_id] = 0
        await bot.send(event=event, message="已开始猜数游戏！输入'我猜+数字'进行游戏", at_sender=True)
    else:
        await bot.send(event=event, message="猜数游戏已在进行！输入'我猜+数字'进行游戏", at_sender=True)
        
@end_guess_number.handle()
async def end_guess_number_handle(bot: Bot, event: Event):
    group_id = str(event.group_id)
    if group_id not in allow_groups:
        return
    if group_id in group_number.keys():
        del group_number[group_id]
        del group_times[group_id]
        await bot.send(event=event, message="停止猜数！", at_sender=True)
    else:
        await bot.send(event=event, message="未开启猜数！", at_sender=True)
        
@forbid_guess_number.handle()
async def forbid_guess_number_handle(bot: Bot, event: Event):
    group_id = str(event.group_id)
    if group_id not in allow_groups:
        return
    else:
        allow_groups.remove(group_id)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(allow_groups, f, ensure_ascii=False)
        await bot.send(event=event, message="已关闭猜数！", at_sender=True)
        
@guess_number.handle()
async def guess_number_handle(bot: Bot, event: Event):
    group_id = str(event.group_id)
    message = event.get_plaintext()
    if group_id not in group_number:
        return
    if len(message) != 6:
        return
    
    numbers = [message[2], message[3], message[4], message[5]]
    right_num = 0
            
    for i in range(4):
        if numbers[i] == group_number[group_id][i]:
            right_num += 1
            
    if right_num == 4:
        await bot.send(event=event, message="您答对啦！", at_sender=True)
        del group_number[group_id]
        del group_times[group_id]
    else:
        if group_times[group_id] != 5:
            group_times[group_id] += 1
            await bot.send(event=event, message=f"很抱歉，您猜的不对，但是您猜的数中有{right_num}位是对的！还有{6 - group_times[group_id]}次机会", at_sender=True)
            try:
                await bot.set_group_ban(group_id=int(event.group_id), user_id=int(event.get_user_id()), duration=30)
            except:
                logger.error("禁言失败")
        else:
            k = ''
            right_number = k.join(group_number[group_id])
            await bot.send(event=event, message=f"很抱歉，您猜的不对，正确的数是{right_number},本轮游戏结束！", at_sender=True)   
            del group_number[group_id]
            del group_times[group_id]     
            