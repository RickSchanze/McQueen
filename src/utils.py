import random
from pathlib import Path
from nonebot.log import logger
from asyncio import Lock
import httpx

class Utils:
    def __init__(self, path) -> None:
        self.path = Path(path)
        self.files = []
        
        for file in self.path.iterdir():
            self.files.append(str(file.name))
            
        self.len = len(self.files)
        self.files.sort()

    def picture_write_to_file(self, data):
        """将图片文件保存至本地
        图片文件需要为二进制
        自动以"1.jpg" 类似格式进行保存
        Args:
            data (_type_): 二进制图片文件
            path (_type_): _description_
            subfix (str): 文件后缀: ".png, .jpg"等
        """
        try:
            with open(str(self.path / str(self.len)), 'wb') as f:
                f.write(data)
                self.len += 1
                self.files.append(str(self.len - 1))
        except Exception as e:
            logger.info(f"保存失败:原因:\n{e}")
    
    async def get_picture(self, url: str):
        async with httpx.AsyncClient() as client:
            try:
                picture = await client.get(url)
                return picture.content
            except Exception as e:
                logger.log(f"获取消息图片失败:原因:\n{e}")
    
    def get_a_picture_path(self):
        index = random.randint(0, (self.len - 1))
        real_path = str(self.path / str(index))
        real_path = real_path.replace('\\', '/')
        return index, f'[CQ:image,file=file:///{real_path}]'
    
    def get_a_picture_name(self):
        index = random.randint(0, (self.len - 1))
        return self.files[index]
    
    def get_picture_urls(self, message: str):
        url = message.find('url=')
        if url == -1:
            return -1;
        else:
            return message[url + 4:]
        
    def get_a_picture(self, index):
        real_path = str(self.path / str(index))
        real_path = real_path.replace('\\', '/')
        return f'[CQ:image,file=file:///{real_path}]'
        
    async def get_and_write(self, url: str):
        urls = self.get_picture_urls(url)
        data = await self.get_picture(urls)
        self.picture_write_to_file(data)

        
util = Utils(Path(__file__).parent.parent / "data"/ "pictures")
    