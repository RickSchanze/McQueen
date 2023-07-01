from typing import Type, Dict

from nonebot import get_driver, on_command, require
from nonebot.internal.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from .config import Config
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent, MessageEvent, Bot
from pathlib import Path

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import get_new_page
import time
import httpx
from nonebot.log import logger
import re
import markdown

global_config = get_driver().config
config = Config.parse_obj(global_config)

nickname = list(global_config.nickname)[0]
__usage__ = fr"""
{nickname}你[如何|怎么|怎么样]评价<选项1>和<选项2>
  麦昆会给你两个选项的优劣！
  但是麦昆思考的很慢，所以可能得很久！
  而且每{config.eitherchoice_gap_time}秒才能使用一次哦！
"""

__plugin_meta__ = PluginMetadata(
    name="帮你选！",
    description=f"让{nickname}帮你选！",
    usage=__usage__
)

gap_time = config.eitherchoice_gap_time
last_timer: Dict[int, int] = {}

either_choice = on_command("你如何评价", aliases={"你怎么评价", "你怎样评价"}, block=True,
                           rule=to_me())

file_dir = Path(__file__).parent

url = "https://eitherchoice.com/api/prompt/ask"


@either_choice.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    if not isinstance(event, GroupMessageEvent):
        return
    global last_timer
    if event.group_id not in last_timer.keys():
        last_timer[event.group_id] = int(time.time())
    now_time = time.time()
    gap = int(now_time - last_timer[event.group_id])
    print(gap)
    if gap < gap_time:
        return
    last_timer[event.group_id] = int(now_time)
    pattern = r"你(怎么|怎样|如何)评价(.*)和(.*)"
    res = re.search(pattern, event.raw_message)
    if res is not None:
        a = res.group(2)
        b = res.group(3)
        if a != '' and b != '':
            json = {"A": a, "B": b, "allowPublic": "true", "lang": "zh-cn"}
            await get_result(json, either_choice)


async def get_result(json, matcher: Type[Matcher]):
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=json)
        if res.status_code != 200:
            logger.error("请求失败:{res.status_code}")
            await matcher.finish(message="我不知道哦")
        else:
            exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
                    'markdown.extensions.toc']
            mdcontent = res.text
            html = markdown.markdown(mdcontent, extensions=exts)
            html = f"""<!DOCTYPE html>
            <html lang="en">
        
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Document</title>
                <style>
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
        
                    table caption {{
                        font-size: 2em;
                        font-weight: bold;
                        margin: 1em 0;
                    }}
        
                    th,
                    td {{
                        border: 1px solid #999;
                        text-align: center;
                        padding: 20px 0;
                    }}
        
                    table thead tr {{
                        background-color: #008c8c;
                        color: #fff;
                    }}
        
                    table tbody tr:nth-child(odd) {{
                        background-color: #eee;
                    }}
        
                    table tbody tr:hover {{
                        background-color: #ccc;
                    }}
        
                    table tbody tr td:first-child {{
                        color: #f40;
                    }}
        
                    table tfoot tr td {{
                        text-align: right;
                        padding-right: 20px;
                    }}
                </style>
            </head>
        
            <body>
            {html}
            </body>
        
            </html>"""
            with Path(file_dir / "template.html").open('w', encoding='utf8') as f:
                f.write(html)
            async with get_new_page() as page:
                await page.goto(Path(file_dir / "template.html").as_uri(), wait_until="networkidle")
                pic = await page.screenshot(path=Path(file_dir / "result.png"))
                await matcher.finish(message=MessageSegment.image(pic), at_sender=True)
