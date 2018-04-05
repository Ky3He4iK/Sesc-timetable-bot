import config
import telebot


class Message:
    def __init__(self, text="", to_user_id=config.father_chat, inline_keyboard=None, silent=False):
        """
        :param text: str
        :param to_user_id: int
        :param inline_keyboard: keyboard
        :param silent: bool
        """
        self.text = text
        self.to_user_id = to_user_id
        self.inline_keyboard = inline_keyboard
        self.silent = silent


class Edit:
    def __init__(self, chat_id=config.father_chat, message_id=1, text="", inline_keyboard=None):
        self.chat_id = chat_id
        self.message_id = message_id
        self.text = text
        self.inline_keyboard = inline_keyboard


def gen(l_b_h=9, l_b_m=0, l_n=0):
    ans = str(l_n + 1) + '. ' + str(l_b_h) + ":" + str(l_b_m) + ' - '
    l_b_h += (l_b_m + 40) // 60
    l_b_m = (l_b_m + 40) % 60
    ans + str(l_b_h + (l_b_m + 40) // 60) + ':' + str(l_b_m)
    if l_n != 6:
        ans += '. Перемена ' + str(brake_len[l_n]) + ' минут\n' + gen(l_b_h + (l_b_m + brake_len[l_n]) // 60,
                                                                      (l_b_m + brake_len[l_n]) % 60, l_n + 1)
    return ans


brake_len = [10, 15, 15, 15, 20, 20]

bells = '\n'.join(["9:00 - 9.40", "9:50 - 10.30", "10:45 - 11.25", "11:40 - 12.20", "12:35 - 13.15", "13:35 - 14.15",
                   "14:35 - 15.15"])
b_m = gen()

DEBUG = True
pool_to_send = [Message() for _ in range(0)]
pool_to_edit = [Edit() for _ in range(0)]
c_day = 0
c_les = 0
logger = telebot.logger
# logger.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
