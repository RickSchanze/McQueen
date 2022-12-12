from email import utils
from nonebot.log import logger
import json
from pathlib import Path
from nonebot import require
require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import get_new_page
from nonebot.permission import SUPERUSER
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Message, Event, Bot, GROUP_ADMIN, GROUP_OWNER
from ...utils import util


work_directory = Path.cwd()
json_path = work_directory / "data" / "cybersensoji"
json_file = json_path / "config.json"
pictures_file = json_path / "pictures.json"
history_file = json_path / "history.json"

if (not json_path.exists()):
    json_path.mkdir()
json_file.touch(exist_ok=True)


with open(json_file, 'r') as f:
    config_ = json.load(f)
    
with open(history_file, 'r') as f:
    history = json.load(f)


from nonebot import get_driver
from .message import message_sign
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot import on_command, load_plugins
import json, random


global_config = get_driver().config

# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass
from ...utils import util

_sub_plugins = set()
_sub_plugins |= load_plugins(
    str((Path(__file__).parent / "plugins").
    resolve()))

def order_to_html(order):
    str_to_transfer = message_sign[order].split('\n')
    color: str = '#efefefc2'
    background = "../../../data/pictures/" + str(util.get_a_picture_name())
    str_left = f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        @font-face {{
            font-family: "fangsong";
            src: url(../../../data/fonts/simfang.ttf);
        }}
        
        @font-face {{
            font-family: "xinwei";
            src: url(../../../data/fonts/STXINWEI.TTF);
        }}
        
        @font-face {{
            font-family: "kaiti";
            src: url(../../../data/fonts/STKAITI.TTF);
        }}
    
        .main {{
            display: flex;
            flex-direction: column;
            width: 700px;
            background-image: url({background});
            background-size: cover;
            box-shadow: 5px 5px 20px #c37272;
            margin-left: 13px;
        }}

        /* left begin */
        /* 诗词，以及吉凶 */
        .up {{
            display: flex;
            flex-direction: row;
            width: 700px;
            background-color: {color};
        }}

        .all {{
            font-family: "fangsong";
            font-size: 70px;
            width: 200px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: space-around;
            flex-direction: column;
        }}

        .poem {{
            font-size: 20px;
        }}

        .poem p {{
            line-height: 15px;
            color: red;
            font-size: 20px;
        }}

        /* 诗词，吉凶 end */
        /* 诗词注解 */
        .bottom {{
            width: 700px;
        }}

        .explanation {{
            font-family: "xinwei";
            font-size: 30px;
            text-align: center;
            width: 700px;
            padding-bottom: 20px;
            padding-top: 20px;
            background-color: {color};
        }}

        .bottom {{
            display: flex;
            flex-direction: row;
            background-color: {color};
        }}

        .one-line .poe {{
            color:blueviolet;
            font-family: "kaiti";
            font-size: 30px;
        }}

        .one-line .exp {{
            color: black;
            font-size: 15px;
        }}

        li {{
            color: brown;
            font-size: 20px;
            margin: 10px;
        }}

        .upright {{
            width: 400px;
        }}

        .botright {{
            margin-left: 50px;;
        }}
        
        .placeholder {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .one-line {{
            height: 120px;
        }}
        
        .botleft {{
            width: 500px;
        }}
        
        .maincover {{
            width: 750px;  
        }}

    </style>
</head>

<body>
<div class="maincover">
    <div class="main">
        <div class="up">
            <div class="upleft"></div>
            <div class="all">{str_to_transfer[0]}</div>
            <div class="placeholder">
            <div class="poem">
                <p>{str_to_transfer[1]}</p>
                <p>{str_to_transfer[2]}</p>
                <p>{str_to_transfer[3]}</p>
                <p>{str_to_transfer[4]}</p>
            </div>
            </div>
            <div class="upright">

                <ul>
    """
    str_middle = ""
    for i in range(13, len(str_to_transfer)):
        str_middle += f"""
        
                    <li>
                        <div class="title">{str_to_transfer[i]}</div>

                    </li>
        """
    
    str_right = f"""
    </ul>
            </div>
        </div>
        <div class="explanation">诗词释义</div>
            <div class="bottom">
            <div class="botleft">
                <div class="one-line">
                    <div class="poe">{str_to_transfer[5]}</div><br />
                    <div class="exp">{str_to_transfer[6]}</div><br />
                </div>
                <div class="one-line">
                    <div class="poe">{str_to_transfer[7]}</div><br />
                    <div class="exp">{str_to_transfer[8]}</div><br />
                </div>
            </div>
            <div class="botright">
                <div class="one-line">
                    <div class="poe">{str_to_transfer[9]}</div><br />
                    <div class="exp">{str_to_transfer[10]}</div><br />
                </div>
                <div class="one-line">
                    <div class="poe">{str_to_transfer[11]}</div><br />
                    <div class="exp">{str_to_transfer[12]}</div><br />
                </div>
            </div>
        </div>
    </div>
    </div>
</body>

</html>
    """
    html = str_left + str_middle + str_right
    with open(str(Path(__file__).parent / "template.html"), 'w', encoding='utf-8') as f:
        f.write(html)
    

draw_by_lot = on_command("抽签", priority=50)
@draw_by_lot.handle()
async def draw_by_lot_handle(bot: Bot, event: Event):
    qq = event.get_user_id()
    length = len(message_sign)
    order = random.randint(0, length)
    if not str(qq) in config_.keys():
        config_[str(qq)] = order
    else:
        order = config_[str(qq)]
    
    order_to_html(order=order)
    
    with open(json_file, 'w') as f:
        json.dump(config_, f, ensure_ascii=False, indent=4)
    
    level = message_sign[order][0: message_sign[order].find('\n')]
    if str(qq) not in [item["qq"] for item in history]:
        history.append({"qq": str(qq), level: 0})
    
    if not is_level_in(level, history[get_qq_in_history(str(qq))]):
        history[get_qq_in_history(str(qq))][level] = 0
    
    history[get_qq_in_history(str(qq))][level] += 1
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    
    try:
        async with get_new_page(viewport={"width": 300, "height": 300}) as page:
            await page.goto(
                "file://" + (str(Path.absolute(Path(__file__).parent) / "template.html")),
                wait_until="networkidle",
                )
            
            pic = await page.screenshot(full_page=True, path="./html2pic.png")
            
        await bot.send(event=event, message=MessageSegment.image(pic), at_sender=True)
    except Exception as e:
        logger.error(f"抽签失败: {e}")
        

def get_qq_in_history(qq):
    for index, item in enumerate(history):
        if item["qq"] == qq:
            return index
    return -1
        
def is_level_in(level, person):
    return level in person.keys()
        
couqian_refresh = on_command("刷新抽签", permission=SUPERUSER)
@couqian_refresh.handle()
async def couqian_refresh_handle(bot:Bot, event:Event):
    try:
        global config_
        config_ = {}
        with open(json_file, 'w') as f:
            json.dump(config_, f, ensure_ascii=False, indent=4)
        await bot.send(event, "刷新成功")
    except:
        await bot.send(event, "刷新失败") 
        
@scheduler.scheduled_job("cron", hour=00, minute=00, misfire_grace_time=60)
async def _():
    global config_
    config_ = {}
    with open(json_file, 'w') as f:
        json.dump(config_, f, ensure_ascii=False, indent=4)
        

append_url = on_command("增加图片", permission=GROUP_ADMIN | GROUP_OWNER)
@append_url.handle()
async def append_url_handler(bot: Bot, event:Event):
    url = event.raw_message
    try:
        await util.get_and_write(url)
    except Exception as e:
        logger.info(f"增加失败:{e}")

history_reply = on_command("抽签历史", priority=20, block=True)
@history_reply.handle()
async def reply(bot: Bot, event: Event):
    qq = str(event.get_user_id())
    isin = get_qq_in_history(qq)
    if isin == -1:
        await bot.send(event=event, message="您还没有记录哦", at_sender=True)
        return
    string = "您的抽签记录为:\n"
    for key in history[isin].keys():
        if key != "qq":
            string += f"{key}: {history[isin][key]}次\n"
    await bot.send(event=event, message=string, at_sender=True)