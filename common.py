import config
import telebot


class Message:
    def __init__(self, text="", to_user_id=config.father_chat, inline_keyboard=None, silent=False, markdown=False):
        self.text = text
        self.to_user_id = to_user_id
        self.inline_keyboard = inline_keyboard
        self.silent = silent
        self.markdown = markdown


class Edit:
    def __init__(self, chat_id=config.father_chat, message_id=1, text="", inline_keyboard=None, markdown=False):
        self.chat_id = chat_id
        self.message_id = message_id
        self.text = text
        self.inline_keyboard = inline_keyboard
        self.markdown = markdown


def send_message(text="", chat_id=config.father_chat, inline_keyboard=None, silent=False, markdown=False, fast=False):
    mes = Message(text=text, to_user_id=chat_id, inline_keyboard=inline_keyboard, silent=silent, markdown=markdown)
    if fast:
        global pool_to_send
        pool_to_send = [mes] + pool_to_send
    else:
        pool_to_send.append(mes)


def edit_message(chat_id=config.father_chat, message_id=1, text="", inline_keyboard=None, markdown=False, fast=False):
    mes = Edit(chat_id=chat_id, message_id=message_id, text=text, inline_keyboard=inline_keyboard, markdown=markdown)
    if fast:
        global pool_to_edit
        pool_to_edit = [mes] + pool_to_edit
    else:
        pool_to_edit.append(mes)


def gen(l_b_h=9, l_b_m=0, l_n=0):
    ans = str(l_n + 1) + '. ' + ('0' if l_b_h < 10 else '') + str(l_b_h) + ":" + \
          ('0' if l_b_m < 10 else '') + str(l_b_m) + ' - '
    l_b_h += (l_b_m + 40) // 60
    l_b_m = (l_b_m + 40) % 60
    ans += ('0' if l_b_h < 10 else '') + str(l_b_h) + ':' + str(l_b_m)
    return ans + ('.\tПеремена ' + str(brake_len[l_n]) + ' минут\n' +
                  gen(l_b_h + (l_b_m + brake_len[l_n]) // 60,
                      (l_b_m + brake_len[l_n]) % 60, l_n + 1) if l_n != 6 else "")


brake_len = [10, 15, 15, 15, 20, 20]

bells = gen()

DEBUG = True
work = False
pool_to_send = [Message() for _ in range(0)]
pool_to_edit = [Edit() for _ in range(0)]
c_day = 0
c_les = 0
logger = telebot.logger
# logger.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
