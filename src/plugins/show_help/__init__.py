from nonebot import get_driver, get_loaded_plugins, on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.rule import to_me
from .config import Config
from pathlib import Path
from nonebot import require

require("nonebot_plugin_htmlrender")

from nonebot_plugin_htmlrender import get_new_page

global_config = get_driver().config
config = Config.parse_obj(global_config)

get_help = on_command("help", aliases={"帮助"}, rule=to_me())

dir_path = Path(__file__).parent


@get_help.handle()
async def get_help_handler():
    gen_html_str()
    async with get_new_page(viewport={"width": 650, "height": 120}) as page:
        await page.goto("file:///" + str(dir_path / "template.html"), wait_until="networkidle")
        pic = await page.screenshot(full_page=True, path=str(dir_path / "help.png"))
    await get_help.finish(message=MessageSegment.image(pic), at_sender=True)


def gen_html_str() -> str:
    plugins = get_loaded_plugins()
    str_inner = """<div class="content">
    <div class="name">{}</div>
    <div class="description">{}</div>
    <pre class="usage">{}</pre>
  </div>"""
    str_insert = ""
    for plugin in plugins:
        if plugin.metadata is not None and plugin.metadata.name not in config.help_excluded:
            name = plugin.metadata.name
            usage = plugin.metadata.usage
            description = plugin.metadata.description
            str_insert += str_inner.format(name, description, usage)
    str_html = f"""
    <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Title</title>
  <style>
    .container {{
    display: flex;
      width: 620px;
      flex-direction: column;
      background: linear-gradient(to right, #BB73DF, #FF8DDB);
      border-radius: 10px;
    }}

    .title {{
    width: 620px;
      font-size: 30px;
      background: linear-gradient(to right, #BB73DF, #FF8DDB);
      text-align: center;
      height: 40px;
      border-radius: 10px;
    }}

    .content {{
    display: flex;
      flex-direction: column;
      margin-bottom: 10px;
      padding: 10px;
      background: linear-gradient(to right, #0DCDA4C7, #C2FCD4C7);
      width: 590px;
      border-radius: 20px;
      margin-top: 5px;
      margin-left: 5px;
      margin-right: 5px;
    }}

    pre {{
    font-size: 12px;
      padding: 3px;
      margin: 0;
      background: #f0f0f06b;
      line-height: 20px;
      /* 行距 */
      width: 583px;
      overflow: auto;
      /* 超出宽度出现滑动条 */
      overflow-Y: hidden;
      /* 作用是隐藏IE的右侧滑动条 */
      border-radius: 10px;
      font-family: 'Microsoft Yahei';
    }}

    .content .name {{
    font-size: 30px;
      font-weight: bold;
      color: blueviolet;
    }}

    .content .description {{
    font-style: italic;
      font-size: 20px;
    }}
  </style>
</head>
<body>
<div class="container">
  <div class="title">帮助</div>
    {str_insert}
</div>
</body>
</html>
    """
    with (dir_path / "template.html").open('w', encoding='utf-8') as f:
        f.write(str_html)
    return str_html
