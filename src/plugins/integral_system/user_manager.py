from enum import Enum
from typing import List
from src.plugins.globals import get_data_path, get_config_path, create_file, read_file, write_file

from .user import User
from .config import Config


class TriggerEvent(Enum):
    NormalChat = 0
    Command = 1
    SignIn = 2


class UserManager:
    users: List[User]

    def __init__(self, config: Config):
        self.data_path = get_data_path('integral_system')
        self.config_path = get_config_path('integral_system')
        self.data_file = create_file(self.data_path, 'users.json')
        self.config = config
        try:
            data = read_file(self.data_file)
            self.users = [User(**user) for user in data]
        except Exception:
            self.users = []

    def get_user(self, qq: int) -> User | None:
        for user in self.users:
            if user.qq == qq:
                return user
        return None

    def add_user(self, user: User):
        self.users.append(user)
        write_file(self.data_file, [user.__dict__ for user in self.users])

    def trigger(self, qq: int, event: TriggerEvent, nickname: str):
        """
        触发积分系统的更新
        :param qq: qq号
        :param event: 积分事件
        :param nickname: 昵称
        """
        user = self.get_user(qq)
        if user is None:
            raise Exception('用户不存在')
        else:
            match event:
                case TriggerEvent.NormalChat:
                    user.integral_append(self.config.integral_normal_chat)
                case TriggerEvent.Command:
                    user.integral_append(self.config.integral_command)
                case TriggerEvent.SignIn:
                    user.integral_append(self.config.integral_sign_in)
            user.update_name(nickname)
            write_file(self.data_file, [user.__dict__ for user in self.users])

    def __del__(self):
        write_file(self.data_file, [user.__dict__ for user in self.users])
