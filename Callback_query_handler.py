from telebot import types

import common
import IO


def main(call, db):
    IO.FileIO.write("call_query.txt", str(call.__dict__), True)
    print(call.__dict__)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Нажми меня", callback_data="test")
    keyboard.add(callback_button)
    common.pool_to_send.append(common.Message(""))
