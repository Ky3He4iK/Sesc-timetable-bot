import sys
import datetime
import threading
from time import sleep
# import telebot

from body import Context
import update_timetable
import common
import requests
# import config

# todo register next step handler
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
            print("exception error")
        except BaseException as e:
            context.write_error(e)
            sleep(3)


def send_to_father(text):
    return context.send_to_father(text)


if __name__ == '__main__':
    common.DEBUG = len(sys.argv) != 1
    if common.DEBUG:
        requests.get("https://telegram.org")
    context = Context()
    bot_main = threading.Thread(target=thread_start)
    bot_main.daemon = True
    bot_main.start()
    # context.send_message(config.father_chat, "test", gen_keyboard())
    while True:
        try:
            if len(common.pool_to_send) != 0:
                context.qsend_message(common.pool_to_send[0].to_user_id, common.pool_to_send[0].text,
                                      silent=common.pool_to_send[0].silent,
                                      inline_keyboard=common.pool_to_send[0].inline_keyboard)
                common.pool_to_send = common.pool_to_send[1:]
                sleep(1 / 30)
            if len(common.pool_to_edit) != 0:
                context.edit_message(common.pool_to_edit[0].chat_id, common.pool_to_edit[0].text,
                                     common.pool_to_edit[0].message_id, common.pool_to_edit[0].inline_keyboard)
                common.pool_to_edit = common.pool_to_edit[1:]
                sleep(1 / 30)
            sleep(1 / 30)
        except KeyboardInterrupt:
            exit(0)
        except BaseException as err:
            common.logger.error(err, exc_info=True)
            print(str(err), err.args, err.__traceback__)
            print(err.with_traceback(err.__traceback__))
            f = open("data/Error-bot-" + datetime.datetime.today().strftime("%y%m%d-%Hh") + '.log', 'a')
            f.write(
                datetime.datetime.today().strftime("%M:%S-%f") + str(err) + ' ' + str(err.args) + '\n\n')
            f.close()


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
# foto, stickers and files ignored
