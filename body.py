import telebot
import requests
import datetime
import logging
from time import sleep
from telebot import types

from Db import Db
import common
import config
import Message_handler


class Context:
    def __init__(self):
        def set_default_keyboard():
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            keyboard.add(types.InlineKeyboardButton(text="Расписание", callback_data="3.0" + ".-1" * 6),
                         types.InlineKeyboardButton(text="Изменения", callback_data="4.0" + ".-1" * 6),
                         types.InlineKeyboardButton(text="Свободные", callback_data="5.0" + ".-1" * 6),
                         types.InlineKeyboardButton(text="Звонки", callback_data="2.1" + ".-1" * 6),
                         types.InlineKeyboardButton(text="Настройки", callback_data="6.0" + ".-1" * 6),
                         types.InlineKeyboardButton(text="Прочее", callback_data="7.0" + ".-1" * 6))
            return keyboard

        self.db = Db()
        self.current_day, self.current_lesson = 0, 0
        self.bot = telebot.TeleBot(config.token_debug if common.DEBUG else config.token)
        config.default_keyboard = set_default_keyboard()

        @self.bot.message_handler(commands=['ping'])
        def _reply_ping(message):
            self.bot.send_message(message.chat.id, "Pong!")
            self.on_user_message(message.from_user.id, message)

        @self.bot.message_handler(content_types=['text'], func=lambda message: message.text[0] == '/')
        def _reply(message):
            self.on_user_message(message.from_user.id, message)
            try:
                Message_handler.message(message, self.db)
            except BaseException as e:
                self.bot.send_message(message.chat.id, "Что-то полшо не так")
                self.write_error(e, message)

        @self.bot.message_handler()
        def _reply_default(message):
            self.on_user_message(message.from_user.id, message)
            try:
                Message_handler.message(message, self.db)
            except BaseException as e:
                self.bot.send_message(message.chat.id, "Что-то пошло не так")
                self.write_error(e, message)

        @self.bot.callback_query_handler(func=lambda call: True)
        def test_callback(call):
            common.logger.info(call)
            try:
                Message_handler.callback(user_id=call.from_user.id, data=self.extract_data_from_text(call.data),
                                         mes_id=call.message.message_id, db=self.db)
            except BaseException as e:
                self.write_error(e)
                self.bot.send_message(call.from_user.id, "Чак Норрис, перелогинься. Ты заставляешь падать ̶м̶о̶и̶ "
                                                         "̶л̶у̶ч̶ш̶и̶е̶ ̶к̶о̶с̶т̶ы̶л̶и̶ мой почти идеальный код")

    def on_user_message(self, user_chat_id, mess):
        if user_chat_id in self.db.users:
            self.db.users[user_chat_id].last_access = datetime.datetime.today().timestamp()
            self.db.users[user_chat_id].username = mess.chat.username
            self.db.users[user_chat_id].first_name = mess.chat.first_name
        common.logger.info(mess)

    def write_error(self, err, mess=None):
        self.send_to_father("An exception occupied!")
        logging.error(err, exc_info=True)
        common.logger.error(err)
        print(str(err), err.args, err.__traceback__)
        f = open("data/Error-bot-" + datetime.datetime.today().strftime("%y%m%d-%Hh") + '.log', 'a')
        text = 'unknown message' if mess is None else (str(mess.text) + '\n' + str(mess.chat.id) + ':' +
                                                       str(mess.from_user.username))
        f.write(datetime.datetime.today().strftime("%M:%S-%f") + str(err) + ' ' + str(err.args) + '\n' + text + '\n\n')
        f.close()

    @staticmethod
    def rfind_space(text):
        text = text[:4094]
        end_p = text.rfind('\n')
        end_p = text.rfind(' ') if end_p < 3800 else end_p
        end_p = 4094 if end_p < 3600 else end_p
        return end_p

    def send_message(self, message):
        if message.to_user_id is None:
            print(message.text + '\nmarkdown: ', message.markdown, '\n', message.inline_keyboard, sep='')
            return True
        try:
            if message.text is None or len(str(message.text)) == 0:
                return False
            text = str(message.text)
            if message.inline_keyboard is None:
                message.inline_keyboard = config.default_keyboard
            if message.inline_keyboard == -1:
                message.inline_keyboard = None
            while len(text) > 4094:
                end_p = self.rfind_space(text)
                self._really_send_edit(chat_id=message.to_user_id, text=text[:end_p], silent=message.silent,
                                       markdown=("Markdown" if message.markdown else None))
                text = text[end_p:]
                sleep(1 / 30)
            if len(text) != 0:
                self._really_send_edit(chat_id=message.to_user_id, text=text, silent=message.silent,
                                       markdown=("Markdown" if message.markdown else None),
                                       reply_markup=message.inline_keyboard)
            return True
        except requests.exceptions.ConnectionError:
            pass
        except BaseException as e:
            self.write_error(e)
        return False

    def _really_send_edit(self, chat_id=config.father_chat, text="", reply_markup=None,
                          markdown=None, send_not_edit=True, mes_id=-1, silent=False):
        if send_not_edit:
            return self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=markdown,
                                         disable_notification=silent)
        return self.bot.edit_message_text(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=markdown,
                                          message_id=mes_id)

    def edit_message(self, edit):
        if edit.chat_id is None:
            print(edit.text + '\nmarkdown: ', edit.markdown, '\n', edit.inline_keyboard, sep='')
            return
        try:
            if edit.text is None or len(str(edit.text)) == 0:
                return False
            text, was = str(edit.text), False
            if edit.inline_keyboard is None:
                edit.inline_keyboard = config.default_keyboard
            if edit.inline_keyboard == -1:
                edit.inline_keyboard = None
            while len(text) > 4094:
                end_p = self.rfind_space(text)
                c_k = edit.inline_keyboard if end_p >= len(text) - 1 else None
                self._really_send_edit(send_not_edit=not was, chat_id=edit.chat_id, text=text[:end_p],
                                       reply_markup=c_k,
                                       markdown=("Markdown" if edit.markdown else None), mes_id=edit.message_id)
                text = text[end_p:]
                sleep(1 / 30)
            if len(text) != 0:
                self._really_send_edit(send_not_edit=was, chat_id=edit.chat_id, text=text,
                                       reply_markup=edit.inline_keyboard,
                                       markdown=("Markdown" if edit.markdown else None), mes_id=edit.message_id)
            return True
        except requests.exceptions.ConnectionError:
            pass
        except telebot.apihelper.ApiException as e:
            print(e)
        except BaseException as e:
            if e.args != ("A request to the Telegram API was unsuccessful. The server returned HTTP 400 Bad Request. "
                          "Response body:\n[b\\'{\"ok\":false,\"error_code\":400,\"description\":\""
                          "Bad Request: message is not modified\"}\\']"):
                self.write_error(e)
        return False

    @staticmethod
    def send_to_father(text):
        common.send_message(text=text, fast=True)

    @staticmethod
    def extract_data_from_text(text):
        return [int(s) for s in text.split('.')]
