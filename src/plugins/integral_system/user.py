class User:
    nickname: str
    qq: int
    integral: int

    def __init__(self, nickname: str, qq: int, integral: int):
        self.nickname = nickname
        self.qq = qq
        self.integral = integral

    def __str__(self):
        return f'User({self.nickname}, {self.qq}, {self.integral})'

    def __repr__(self):
        return f'User({self.nickname}, {self.qq}, {self.integral})'

    def integral_append(self, num: int):
        self.integral += num

    def integral_sub(self, num: int):
        self.integral -= num

    def integral_clear(self):
        self.integral = 0

    def update_name(self, name: str):
        self.nickname = name
