from telebot import types

import common
import IO


def main(call, db):
    IO.FileIO.write("call_query.txt", str(call.__dict__), True)
    print(call.__dict__)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Do not touch", callback_data="touched")
    keyboard.add(callback_button)
    common.pool_to_edit.append(common.Edit(text="new text", chat_id=call.from_user.id, inline_keyboard=keyboard,
                                           message_id=call.message.message_id))


mes1 = {'photo': None, 'sticker': None, 'edit_date': None, 'new_chat_photo': None, 'document': None, 'contact': None,
        'entities': None, 'migrate_from_chat_id': None, 'content_type': 'text', 'caption': None, 'audio': None,
        'left_chat_member': None, 'author_signature': None, 'video': None, 'reply_to_message': None,
        'new_chat_title': None, 'text': '/asd', 'pinned_message': None, 'venue': None, 'message_id': 349,
        'forward_from_chat': None, 'from_user': {'is_bot': False, 'first_name': 'M█sha', 'username': 'Ky3He4iK',
                                                 'language_code': 'en-US', 'id': 351693351, 'last_name': None},
        'new_chat_members': None, 'connected_website': None, 'channel_chat_created': None, 'caption_entities': None,
        'media_group_id': None, 'new_chat_member': None, 'invoice': None, 'delete_chat_photo': None,
        'forward_date': None, 'group_chat_created': None, 'video_note': None, 'successful_payment': None,
        'supergroup_chat_created': None, 'forward_from': None, 'chat':
            {'photo': None, 'id': 351693351, 'sticker_set_name': None, 'type': 'private', 'username': 'Ky3He4iK',
             'title': None, 'last_name': None, 'can_set_sticker_set': None, 'invite_link': None, 'first_name': 'M█sha',
             'all_members_are_administrators': None, 'pinned_message': None, 'description': None},
        'migrate_to_chat_id': None, 'location': None, 'date': 1520367454, 'voice': None
        }
call1 = {'chat_instance': '3806880537022758485', 'message': {
    'photo': None, 'sticker': None, 'edit_date': None, 'new_chat_photo': None, 'document': None,
    'new_chat_members': None, 'contact': None, 'entities': None, 'migrate_from_chat_id': None, 'content_type': 'text',
    'forward_from_chat': None, 'invoice': None, 'left_chat_member': None, 'author_signature': None, 'video': None,
    'reply_to_message': None, 'new_chat_title': None, 'delete_chat_photo': None, 'pinned_message': None, 'venue': None,
    'connected_website': None, 'chat': None, 'from_user': None, 'message_id': 350, 'caption': None,
    'caption_entities': None, 'media_group_id': None, 'new_chat_member': None, 'audio': None, 'text': 'text',
    'forward_date': None, 'group_chat_created': None, 'video_note': None, 'successful_payment': None,
    'channel_chat_created': None, 'supergroup_chat_created': None, 'forward_from': None, 'migrate_to_chat_id': None,
    'location': None, 'date': 1520367600, 'voice': None}, 'data': 'test', 'from_user':
    {'is_bot': False, 'first_name': 'M█sha', 'username': 'Ky3He4iK', 'language_code': 'en-US', 'id': 351693351,
     'last_name': None}, 'game_short_name': None, 'id': '1510511443156897768', 'inline_message_id': None}
