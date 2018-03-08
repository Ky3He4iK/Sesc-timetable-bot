import telebot
import datetime
import logging
from threading import Thread
from time import sleep
from telebot import types

from Db import Db
import common
import config
from Type import Type
import Callback_query_handler
import update_timetable
# from old import legacy_hub


class Context:
    def __init__(self):
        def set_default_keyboard():
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            callback_buttons = [types.InlineKeyboardButton(text="Timetable", callback_data="4.0 tt"),
                                types.InlineKeyboardButton(text="Changes", callback_data="5.0 changes"),
                                types.InlineKeyboardButton(text="Free rooms", callback_data="6.0 free"),
                                types.InlineKeyboardButton(text="Bells", callback_data="3.1 bells"),
                                types.InlineKeyboardButton(text="Settings", callback_data="7.0 settings"),
                                types.InlineKeyboardButton(text="Another", callback_data="8.0 another")]
            keyboard.add(callback_buttons[0], callback_buttons[1], callback_buttons[2], callback_buttons[3],
                         callback_buttons[4], callback_buttons[5])
            return keyboard

        self.DEBUG = common.DEBUG
        self.db = Db()
        self.current_day = 0
        self.current_lesson = 0
        if common.DEBUG:
            self.bot = telebot.TeleBot(config.token_debug)
        else:
            self.bot = telebot.TeleBot(config.token)
        self.updating = Thread(target=self.thread_update)
        self.updating.daemon = True
        self.updating.start()
        self.timing = Thread(target=self.thread_time)
        self.timing.daemon = True
        self.timing.start()
        config.default_keyboard = set_default_keyboard()

        @self.bot.message_handler(commands=['ping'])
        def _reply_ping(message):
            common.logger.info(message)
            self.bot.send_message(message.chat.id, "Pong!")
            self.on_user_message(self.db.find_user(message.from_user.id))

        @self.bot.message_handler(content_types=['text'], func=lambda message: message.text[0] == '/')
        def _reply(message):
            common.pool_to_send.append(common.Message("text", message.from_user.id))
            common.logger.info(message)
            if common.DEBUG:
                return
            try:
                self.mes_proc(message)
            except BaseException as e:
                self.bot.send_message(message.chat.id, "Чак Норрис, перелогинься. Ты заставляешь падать ̶м̶о̶и̶ "
                                                       "̶л̶у̶ч̶ш̶и̶е̶ ̶к̶о̶с̶т̶ы̶л̶и̶ мой почти идеальный код обработки"
                                                       " ошибок")
                self.send_to_father("An GREAT ERROR occupied")
                self.write_error(e, message)

        @self.bot.message_handler(func=lambda message: True)
        def _reply_default(message):
            self.on_user_message(self.db.find_user(message.from_user.id))

        @self.bot.callback_query_handler(func=lambda call: True)
        def test_callback(call):
            common.logger.info(call)
            Callback_query_handler.main(call, self.db)

    def on_user_message(self, user_id):
        if user_id != -1:
            self.db.users[user_id].last_access = datetime.datetime.today().timestamp()

    def write_error(self, err, mess=None):
        self.send_to_father("An exception occupied!")
        logging.error(err, exc_info=True)
        print(str(err), err.args, err.__traceback__)
        print(err.with_traceback(err.__traceback__))
        f = open("Error-bot-" + datetime.datetime.today().strftime("%y%m%d-%Hh") + '.log', 'a')
        if mess is None:
            text = 'HZ CHTO ETO'
        else:
            text = str(mess.text) + '\n' + str(mess.chat.id) + ':' + str(mess.from_user.username)
        f.write(datetime.datetime.today().strftime("%M:%S-%f") + str(err) + ' ' + str(err.args) + '\n' + text + '\n\n')
        f.close()

    def qsend_message(self, chat_id, text, inline_keyboard=None, silent=False):
        try:
            text = str(text)
            if len(text) == 0:
                return False
            if inline_keyboard is None:
                inline_keyboard = config.default_keyboard
            while len(text) > 4094:
                end_p = text[:4094].rfind('\n')
                if end_p < 3800:
                    end_p = text[:4094].rfind(' ')
                    if end_p < 3600:
                        end_p = 4094
                self.bot.send_message(chat_id, text[:end_p], disable_notification=silent)
                text = text[end_p:]
                sleep(0.01)
            if len(text) != 0:
                self.bot.send_message(chat_id, text, reply_markup=inline_keyboard, disable_notification=silent)
                sleep(0.01)
            return True
        except BaseException as e:
            self.write_error(e)
            return False

    def edit_message(self, chat_id, text, message_id, inline_keyboard=None):
        try:
            text = str(text)
            if len(text) != 0:
                if inline_keyboard is None:
                    inline_keyboard = config.default_keyboard
                try:
                    self.bot.edit_message_text(text[:4096], chat_id, message_id, reply_markup=inline_keyboard)
                except telebot.apihelper.ApiException as e:
                    print(e.function_name, e.result, e.args)
                    return False
                sleep(0.01)
                return True
        except BaseException as e:
            self.write_error(e)
        return False

    @staticmethod
    def send_to_father(text):
        common.pool_to_send = [common.Message(text=text)] + common.pool_to_send

    def mes_proc(self, message):
        try:
            print('Message!')
            if message.text[0] == '/':
                if message.text == '/start':
                    if self.db.find_user(message.from_user.id) == -1:
                        self.db.add_user(message)
                        self.send_to_father("user added")
                        text = "Привет, " + str(message.from_user.first_name) + \
                               "!\nЧтобы настроить выдачу расписания зайди в прочее"

                        # TODO: write a normal start message and add set class on startup
                    else:
                        text = str(message.from_user.first_name) + ", ты уже зарегистрирован"
                elif message.text == '/menu':
                    text = "Типа главное меню //TODO: write normal texts"  # TODO: ну ты понел
                elif message.text == '/help':
                    text = config.help_mes
                else:
                    text = "Старые команды не работают"
                common.pool_to_send.append(common.Message(text=text, to_user_id=message.from_user.id,
                                                          inline_keyboard=None))
                # TODO: do
            else:
                common.pool_to_send.append(common.Message(text="...", to_user_id=message.from_user.id,
                                                          inline_keyboard=None))
            self.on_user_message(self.db.find_user(message.from_user.id))
        except Exception as e:
            common.pool_to_send.append(common.Message(text="так_блэт.пнг\nКостыли не выдержали и бот упал\nЯ бы "
                                                           "добавил ещё парочку, но ̶м̶н̶е̶ ̶л̶е̶н̶ь̶ у меня лапки :3",
                                                      to_user_id=message.from_user.id, inline_keyboard=None))
            self.write_error(e, message)
            return None
        # todo: add sudoadd for users

    def thread_time(self):
        while True:
            try:
                times = [[9, 25], [10, 20], [11, 15], [12, 10], [13, 10], [14, 10], [15, 10]]

                def set_l(c_h, c_m):
                    for i in range(len(times)):
                        if c_h < times[i][0] and (c_h == times[i][0] and c_m <= times[i][1]):
                            return i
                    return 7

                today = datetime.datetime.today()
                self.current_day = today.weekday()
                c_hour = today.hour
                c_hour += 3
                if c_hour > 23:
                    c_hour -= 24
                    self.current_day = (self.current_day + 1) % 7
                c_minute = today.minute
                self.current_lesson = set_l(c_hour, c_minute)
                print(self.db.timetable.d_n[self.current_day % 6], c_hour, c_minute)
                common.c_day = self.current_day
                common.c_les = self.current_lesson
                for _ in range(60):
                    c_minute += 2
                    c_hour += c_minute // 60
                    c_minute %= 60
                    set_l(c_hour, c_minute)
                    sleep(120)
            except BaseException as e:
                self.write_error(e)
                print("Time thread: error")

    def thread_update(self):  # syns changes every 30 min, timetable - every 4 hours
        def changes_notify():
            def gen_changes(class_id):
                try:
                    changes_cell = self.db.timetable.changes.changes[self.db.timetable.changes.ch_ind[class_id]]
                except KeyError:
                    return False
                return "Свежие изменения для " + self.db.timetable.c_n[changes_cell.class_ind] + " на " + \
                       self.db.timetable.d_n[self.db.timetable.changes.change_day] + ":\n" + \
                       '\n'.join(c_d for c_d in changes_cell.change_data) + \
                       "\nВсегда можно отказаться от этих уведомлений в настройках (если я их сделал)"

            def gen_all_changes():
                return "Свежие изменения на " + self.db.timetable.d_n[self.db.timetable.changes.change_day] + \
                       " для всех" + '\n\n'.join(
                    self.db.timetable.c_n[changesCell.class_ind] + '\n'.join(c_d for c_d in changesCell.change_data)
                    for changesCell in self.db.timetable.changes.changes) + \
                       "\nВсегда можно отказаться от этих уведомлений в настройках (если я их сделал)"
            is_ok = True
            for user in self.db.timetable.users:
                if (user.type_name != Type.CLASS or self.db.timetable.changes.has_changes[user.type_id]) and \
                        user.notifications:
                    if user.type_name == Type.CLASS:
                        text = gen_changes(user.type_id)
                        is_ok = is_ok and (text is not False)
                    else:
                        text = gen_all_changes()
                        is_ok = is_ok and (text is not False)
                    if text is not False:
                        common.pool_to_send.append(common.Message(text=text, to_user_id=user.user_id,
                                                                  inline_keyboard=None, silent=True))
            return is_ok

        counter = 0
        while True:
            try:
                c_o = self.db.timetable.changes
                b = update_timetable.t_update(self.db.timetable, counter == 0)
                counter += 1
                if counter >= 8:
                    counter = 0
                if self.db.timetable.changes != c_o and b:
                    b = b or changes_notify()
                if not b:
                    print("update failed")
                sleep(60 * 30)
            except BaseException as e:
                self.write_error(e)
        # Todo: add backups
