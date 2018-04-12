import sys
import threading
from time import sleep
import datetime
# import telebot

from body import Context
import update_timetable
import common
import requests
from Type import Type
# import config

# todo: register next step handler
# todo: add markdown


def check_update_system():
    import Timetable
    import IO
    import time

    s_t = time.time()
    t = Timetable.Timetable()
    # b = t.update()
    b = update_timetable.t_update(t)
    print(b, time.time() - s_t)
    if b:
        s_t = time.time()
        IO.FileIO.write_json("data/tt.json", t)
        print("Written", time.time() - s_t)
        s_t = time.time()
        t.restore(IO.FileIO.read_json("data/tt.json"))
        IO.FileIO.write_json("data/tt1.json", t)
        # input()
        print(time.time() - s_t)
    else:
        print("update failed")


def thread_start():
    while True:
        try:
            context.bot.polling(none_stop=False)
        except KeyboardInterrupt:
            exit(0)
        except requests.ConnectionError:
            print("connection error")
        except requests.ReadTimeout:
            print("read timeout error")
        except BaseException as e:
            context.write_error(e)
            sleep(3)


def thread_send():
    while True:
        try:
            if len(common.pool_to_send) != 0:
                context.send_message(common.pool_to_send[0])
                common.pool_to_send = common.pool_to_send[1:]
                sleep(1 / 30)
            if len(common.pool_to_edit) != 0:
                context.edit_message(common.pool_to_edit[0])
                common.pool_to_edit = common.pool_to_edit[1:]
                sleep(1 / 30)
            sleep(1 / 30)
        except KeyboardInterrupt:
            exit(0)
        except BaseException as e:
            common.logger.error(e, exc_info=True)


def thread_update(my_context):  # syns changes every 30 min, timetable - every 4 hours
    def changes_notify():
        def gen_changes(class_id):
            try:
                changes_cell = my_context.db.timetable.changes.changes[my_context.db.timetable.changes.ch_ind[class_id]]
            except KeyError:
                return False
            return "Свежие изменения для " + my_context.db.timetable.c_n[changes_cell.class_ind] + " на " + \
                   my_context.db.timetable.d_n[my_context.db.timetable.changes.change_day] + ":\n" + \
                   '\n'.join(c_d for c_d in changes_cell.change_data) + \
                   "\nВсегда можно отказаться от этих уведомлений в настройках (если я их сделал)"

        def gen_all_changes():
            return "Свежие изменения на " + my_context.db.timetable.d_n[my_context.db.timetable.changes.change_day] + \
                   " для всех" + '\n\n'.join(
                my_context.db.timetable.c_n[changesCell.class_ind] + '\n'.join(c_d for c_d in changesCell.change_data)
                for changesCell in my_context.db.timetable.changes.changes) + \
                   "\nВсегда можно отказаться от этих уведомлений в настройках (если я их сделал)"
        is_ok = True
        for user in list(my_context.db.timetable.users.values()):
            if (user.type_name != Type.CLASS or my_context.db.timetable.changes.has_changes[user.type_id]) and \
                    user.settings.notify:
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
            c_o = my_context.db.timetable.changes
            b = update_timetable.t_update(my_context.db.timetable, counter == 0)
            counter += 1
            if counter >= 8:
                counter = 0
            if my_context.db.timetable.changes != c_o and b:
                b = b or changes_notify()
            print("updated " + str(counter == 1) if b else "update failed")
            sleep(60 * 30)
        except BaseException as e:
            my_context.write_error(e)
    # Todo: add backups


def thread_time(my_context):
        while True:
            try:
                times = [[9, 25], [10, 20], [11, 15], [12, 10], [13, 10], [14, 10], [15, 10]]

                def set_l(c_h, c_m):
                    for i in range(len(times)):
                        if c_h < times[i][0] and (c_h == times[i][0] and c_m <= times[i][1]):
                            return i
                    return 7

                today = datetime.datetime.today()
                my_context.current_day = today.weekday()
                c_hour = today.hour
                c_hour += 3
                if c_hour > 23:
                    c_hour -= 24
                    my_context.current_day = (my_context.current_day + 1) % 7
                c_minute = today.minute
                my_context.current_lesson = set_l(c_hour, c_minute)
                print(my_context.db.timetable.d_n[my_context.current_day % 6], c_hour, c_minute)
                common.c_day = my_context.current_day
                common.c_les = my_context.current_lesson
                for _ in range(60):
                    c_minute += 2
                    c_hour += c_minute // 60
                    c_minute %= 60
                    set_l(c_hour, c_minute)
                    sleep(120)
            except BaseException as e:
                my_context.write_error(e)
                print("Time thread: error")


if __name__ == '__main__':
    common.DEBUG = len(sys.argv) != 1
    if common.DEBUG:
        requests.get("https://telegram.org")
    context = Context()
    bot_main = threading.Thread(target=thread_start)
    bot_main.daemon = True
    bot_main.start()
    updating = threading.Thread(target=thread_update, args=[context])
    updating.daemon = True
    updating.start()
    timing = threading.Thread(target=thread_time, args=[context])
    timing.daemon = True
    timing.start()
    sending = threading.Thread(target=thread_send)
    sending.daemon = True
    sending.start()
    common.work = True
    # context.send_message(config.father_chat, "test", gen_keyboard())
    while common.work:
        sleep(3)


mes = {'content_type': 'text', 'message_id': 97, 'from_user':  # usual mes
    {'id': 351693351, 'is_bot': False, 'first_name': 'Misha', 'username': 'Ky3He4iK', 'last_name': None,
     'language_code': 'ru-RU'},
       'date': 1517232939, 'chat':
           {'type': 'private', 'last_name': None, 'first_name': 'Misha', 'username': 'Ky3He4iK', 'id': 351693351,
            'title': None, 'all_members_are_administrators': None, 'photo': None, 'description': None,
            'invite_link': None, 'pinned_message': None, 'sticker_set_name': None, 'can_set_sticker_set': None},
       'forward_from_chat': None, 'forward_from': None, 'forward_date': None, 'reply_to_message': None,
       'edit_date': None, 'author_signature': None, 'text': '/ping',
       'entities': ['<telebot.types.MessageEntity object at 0x00000000071F8E80>'], 'caption_entities': None,
       'audio': None, 'document': None, 'photo': None, 'sticker': None, 'video': None, 'video_note': None,
       'voice': None, 'caption': None, 'contact': None, 'location': None, 'venue': None, 'new_chat_member': None,
       'new_chat_members': None, 'left_chat_member': None, 'new_chat_title': None, 'new_chat_photo': None,
       'delete_chat_photo': None, 'group_chat_created': None, 'supergroup_chat_created': None,
       'channel_chat_created': None, 'migrate_to_chat_id': None, 'migrate_from_chat_id': None, 'pinned_message': None,
       'invoice': None, 'successful_payment': None}
mes1 = {'content_type': 'text', 'message_id': 101, 'from_user':  # forward mes
    {'id': 351693351, 'is_bot': False, 'first_name': 'Misha', 'username': 'Ky3He4iK', 'last_name': None,
     'language_code': 'ru-RU'},
        'date': 1517233236, 'chat':
    {'type': 'private', 'last_name': None, 'first_name': 'Misha', 'username': 'Ky3He4iK', 'id': 351693351,
     'title': None, 'all_members_are_administrators': None, 'photo': None, 'description': None, 'invite_link': None,
     'pinned_message': None, 'sticker_set_name': None, 'can_set_sticker_set': None},
        'forward_from_chat': None, 'forward_from':
            {'id': 351693351, 'is_bot': False, 'first_name': 'Misha', 'username': 'Ky3He4iK', 'last_name': None,
             'language_code': 'ru-RU'},
        'forward_date': 1517233172, 'reply_to_message': None, 'edit_date': None,
        'author_signature': None, 'text': 'zz', 'entities': None, 'caption_entities': None, 'audio': None,
        'document': None, 'photo': None, 'sticker': None, 'video': None, 'video_note': None, 'voice': None,
        'caption': None, 'contact': None, 'location': None, 'venue': None, 'new_chat_member': None,
        'new_chat_members': None, 'left_chat_member': None, 'new_chat_title': None, 'new_chat_photo': None,
        'delete_chat_photo': None, 'group_chat_created': None, 'supergroup_chat_created': None,
        'channel_chat_created': None, 'migrate_to_chat_id': None, 'migrate_from_chat_id': None, 'pinned_message': None,
        'invoice': None, 'successful_payment': None}
mes2 = {'content_type': 'text', 'message_id': 104, 'from_user':  # reply mes
    {'id': 351693351, 'is_bot': False, 'first_name': 'Misha', 'username': 'Ky3He4iK', 'last_name': None,
     'language_code': 'ru-RU'},
        'date': 1517233629, 'chat':
            {'type': 'private', 'last_name': None, 'first_name': 'Misha', 'username': 'Ky3He4iK', 'id': 351693351,
             'title': None, 'all_members_are_administrators': None, 'photo': None, 'description': None,
             'invite_link': None, 'pinned_message': None, 'sticker_set_name': None, 'can_set_sticker_set': None},
        'forward_from_chat': None, 'forward_from': None, 'forward_date': None, 'reply_to_message':
            {'content_type': 'text', 'message_id': 98, 'from_user': '<telebot.types.User object at 0x000000000723C668>',
             'date': 1517233057, 'chat': '<telebot.types.Chat object at 0x000000000723C438>', 'forward_from_chat': None,
             'forward_from': None, 'forward_date': None, 'reply_to_message': None, 'edit_date': None,
             'author_signature': None, 'text': 'Pong!', 'entities': None, 'caption_entities': None, 'audio': None,
             'document': None, 'photo': None, 'sticker': None, 'video': None, 'video_note': None, 'voice': None,
             'caption': None, 'contact': None, 'location': None, 'venue': None, 'new_chat_member': None,
             'new_chat_members': None, 'left_chat_member': None, 'new_chat_title': None, 'new_chat_photo': None,
             'delete_chat_photo': None, 'group_chat_created': None, 'supergroup_chat_created': None,
             'channel_chat_created': None, 'migrate_to_chat_id': None, 'migrate_from_chat_id': None,
             'pinned_message': None, 'invoice': None, 'successful_payment': None},
        'edit_date': None, 'author_signature': None, 'text': 'lll\nkll', 'entities': None, 'caption_entities': None,
        'audio': None, 'document': None, 'photo': None, 'sticker': None, 'video': None, 'video_note': None,
        'voice': None,  'caption': None, 'contact': None, 'location': None, 'venue': None, 'new_chat_member': None,
        'new_chat_members': None, 'left_chat_member': None, 'new_chat_title': None, 'new_chat_photo': None,
        'delete_chat_photo': None, 'group_chat_created': None, 'supergroup_chat_created': None,
        'channel_chat_created': None, 'migrate_to_chat_id': None, 'migrate_from_chat_id': None, 'pinned_message': None,
        'invoice': None, 'successful_payment': None}
# photo, stickers and files ignored
