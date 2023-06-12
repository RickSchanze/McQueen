from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    record_min_count: int = 50
    record_max_count: int = 70
    reply_min_count: int = 50
    reply_max_count: int = 70
