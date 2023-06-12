from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    integral_sign_in: int = 5
    integral_normal_chat: int = 1
    integral_command: int = 3

