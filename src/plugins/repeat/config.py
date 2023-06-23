from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    repeat_record_random_min: int = 50
    repeat_record_random_max: int = 80
    repeat_reply_random_min: int = 50
    repeat_reply_random_max: int = 80
    repeat_max_record_count: int = 300

