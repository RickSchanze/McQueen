class Wife:
    def __init__(self, name: str, description: str, author: int, filename: str, author_nickname: str):
        self.name = name
        self.description = description
        self.author = author
        self.filename = filename
        self.author_nickname = author_nickname

    def __repr__(self):
        return f"<Wife name={self.name} author={self.author} filename={self.filename}>"
