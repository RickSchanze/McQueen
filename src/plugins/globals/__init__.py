from nonebot import get_driver
from pathlib import Path
from .config import Config
import json

global_config = get_driver().config
config = Config.parse_obj(global_config)

# Common Path
work_directory = Path.cwd()
data_directory = work_directory / "data"
config_directory = work_directory / "config"
if not data_directory.exists():
    data_directory.mkdir()

if not config_directory.exists():
    config_directory.mkdir()


# extern path
def get_data_path(plugin_name: str) -> Path:
    data_path = data_directory / plugin_name
    if not data_path.exists():
        data_path.mkdir()
    return data_path


def get_config_path(plugin_name: str) -> Path:
    config_path = config_directory / plugin_name
    if not config_path.exists():
        config_path.mkdir()
    return config_path


def create_file(path: Path, name: str) -> Path:
    config_file = path / name
    if not config_file.exists():
        config_file.touch()
    return config_file


def create_directory(path: Path, name: str) -> Path:
    directory = path / name
    if not directory.exists():
        directory.mkdir()
    return directory


def read_file(path: Path, use_json: bool = True):
    with path.open('r', encoding='utf-8') as f:
        if use_json:
            return json.load(f)
        else:
            return f.read()


def write_file(path: Path, data, use_json: bool = True):
    with path.open('w', encoding='utf-8') as f:
        if use_json:
            json.dump(data, f, indent=4)
        else:
            f.write(data)
