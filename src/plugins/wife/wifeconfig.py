from pydantic import BaseModel, Extra


class WifeConfig(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    wife_data_path: str = "data/wifes"
    wife_picture_path: str = "data/wifes/pictures"
    wife_roll_file: str = "roll.json"
    wife_content_file: str = "content.json"
