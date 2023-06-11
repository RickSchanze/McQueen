from pydantic import BaseModel, Extra


class EchoConfig(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
