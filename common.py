import config


class Message:
    def __init__(self, text="", to_user_id=config.father_chat, inline_keyboard=None):
        self.text = text
        self.to_user_id = to_user_id
        self.inline_keyboard = inline_keyboard


DEBUG = True
pool_to_send = [Message() for _ in range(0)]
c_day = 0
c_les = 0
