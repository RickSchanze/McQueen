from typing import List

from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    data_path: str = "data"
    config_path: str = "config"
    json_donot_encode: List[str] = ["now_record_index", "now_reply_index", "to_record", "to_reply", "last_reply"]
