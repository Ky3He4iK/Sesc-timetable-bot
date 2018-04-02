from telebot import types

from Type import *
import common
import config


def kb_button(text="Назад", data=([2, 0] + [-1] * 6)):
    return types.InlineKeyboardButton(text=text, callback_data='.'.join(str(d) for d in data))


def callback(call, db):
    def extract_id_from_text(callback_text):
        return [int(s) for s in callback_text.split('.')]

    def presentation_to_string(presentation):
        if presentation == Presentation.CURRENT_CLASS:
            return "для своего класса"
        if presentation == Presentation.ALL_CLASSES:
            return "для всех"
        if presentation == Presentation.ALL_WEEK:
            return "на неделю"
        if presentation == Presentation.NEAR:
            return "ближайший урок"
        if presentation == Presentation.TOMORROW:
            return "завтра"
        if presentation == Presentation.TODAY:
            return "на сегодня"

    data = extract_id_from_text(call.data)
    cur_state = ".".join(str(d) for d in data)
    text = "Чем могу помочь?"
    keyboard = None
    print(data)
    if data[0] == 1:
        d = '.'.join(str(i) for i in data[1:])
        text = "todo " + d  # todo: yes

    elif data[0] == 2:  # todo strip to format
        if data[1] == 1:
            text = "Расписание звонков:\n" + common.bells
        elif len(data) > 2:
            if data[-1] == -1:
                call.data = "1.2.-1.-1.-1.-1.-1.-1"
                return callback(call, db)
            db.users[call.from_user.id].settings.type_name = data[2]
            db.users[call.from_user.id].settings.type_id = data[3]
        elif data[1] == 3:
            text = "Ну что же ты так?("

    elif data[0] == 3:
        u_settings = db.users[call.from_user.id].settings
        ind_type = [data[5], data[4]]  # why reverse? Just for lulz!
        day = data[6]

        if day == -1:
            day = 7
        if ind_type[0] == -1:
            ind_type[0] = u_settings.type_id
        if ind_type[1] == -1:
            ind_type[1] = u_settings.type_name

        if day == 7:
            if data[1] == Presentation.ALL_WEEK or (data[1] == 0 and
                                                    u_settings.default_presentation == Presentation.ALL_WEEK):
                text = db.timetable.get_timetable(ind_type[0], ind_type[1])
            elif data[1] == Presentation.TODAY or (data[1] == 0 and
                                                   u_settings.default_presentation == Presentation.TODAY):
                text = db.timetable.get_timetable_today(ind_type[0], ind_type[1])
            elif data[1] == Presentation.TOMORROW or (data[1] == 0 and
                                                      u_settings.default_presentation == Presentation.TOMORROW):
                text = db.timetable.get_timetable_tomorrow(ind_type[0], ind_type[1])
            elif data[1] == Presentation.NEAR or (data[1] == 0 and
                                                  u_settings.default_presentation == Presentation.NEAR):
                text = db.timetable.get_timetable_near(ind_type[0], ind_type[1])
            elif data[1] == Presentation.OTHER or (data[1] == 0 and
                                                   u_settings.default_presentation == Presentation.OTHER):
                text = db.timetable.get_timetable(ind_type[0], ind_type[1], data[-1])
        else:
            text = db.timetable.get_timetable(ind_type[0], ind_type[1], day)
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        ending = ind_type[::-1] + [day, data[1]]
        keyboard.add(kb_button("Сегодня", [3, Presentation.TODAY, -1, -1, ind_type[1], ind_type[0], day, data[1]]),  # 2
                     kb_button("Сейчас", [3, Presentation.NEAR, -1, -1, -1, -1, -1, -1]),  # 4
                     kb_button("Завтра", [3, Presentation.TOMORROW, -1, -1, -1, -1, -1, -1]),  # 3
                     kb_button("На неделю", [3, Presentation.ALL_WEEK, -1, -1, -1, -1, -1, -1]),  # 1
                     kb_button("Конкретный день", [8, 0, 3, 7] + ending),
                     kb_button("Другое расписание", [1, 0, 3, data[1]] + ending),

                     kb_button("Назад", [2, 0] + [-1] * 6))

    elif data[0] == 4:
        d_p = db.users[call.from_user.id].settings.default_presentation_changes
        if data[1] == Presentation.ALL_CLASSES or (data[1] == 0 and d_p == Presentation.ALL_CLASSES):
            text = db.timetable.changes.get_changes(db.timetable)
        elif data[1] == Presentation.CURRENT_CLASS or (data[1] == 0 and d_p == Presentation.ALL_CLASSES):
            text = db.timetable.changes.get_changes(db.timetable, db.users[call.from_user.id].settings.type_id)
        elif data[1] == Presentation.OTHER and data[5] != -1:
            text = db.timetable.changes.get_changes(db.timetable, data[5])
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        k_bs = [kb_button("Все классы", [4, Presentation.ALL_CLASSES, -1, -1, -1, -1, -1, 5]),
                kb_button("Определенный класс", [9, 0, 4, Presentation.OTHER, -1, -1, -1, 1]),
                kb_button("\"Мой\" класс", [4, Presentation.CURRENT_CLASS, -1, -1, -1, -1, -1, 6])]
        if db.users[call.from_user.id].settings.type_name == Type.CLASS:
            keyboard.add(k_bs[0], k_bs[1], k_bs[2])
        else:
            keyboard.add(k_bs[0], k_bs[1])
        keyboard.add(kb_button())

    elif data[0] == 5:  # todo strip to format
        dp = db.users[call.from_user.id].settings.default_presentation
        if data[1] == Presentation.ALL_WEEK or (data[1] == 0 and dp == Presentation.ALL_WEEK):
            text = db.timetable.free_rooms.get_free(db.timetable)
        elif data[1] == Presentation.TODAY or (data[1] == 0 and dp == Presentation.TODAY):
            text = db.timetable.free_rooms.get_free_today(db.timetable)
        elif data[1] == Presentation.TOMORROW or (data[1] == 0 and dp == Presentation.TOMORROW):
            text = db.timetable.free_rooms.get_free_tomorrow(db.timetable)
        elif data[1] == Presentation.NEAR or (data[1] == 0 and dp == Presentation.NEAR):
            text = db.timetable.free_rooms.get_free_near(db.timetable)
        elif data[6] != -1:
            text = db.timetable.free_rooms.get_free(db.timetable, data[6])

        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(kb_button("Сегодня", [5, Presentation.TODAY] + [-1] * 5 + [Presentation.TODAY]),  # 2
                     kb_button("Сейчас", [5, Presentation.NEAR] + [-1] * 5 + [Presentation.NEAR]),  # 4
                     kb_button("Завтра", [5, Presentation.TOMORROW] + [-1] * 5 + [Presentation.TOMORROW]),  # 3
                     kb_button("На неделю", [5, Presentation.ALL_WEEK] + [-1] * 5 + [Presentation.ALL_WEEK]),  # 1
                     kb_button("Конкретный день", [8, 0, 5, data[1]] + [-1] * 3 + [data[1]]))  # 1
        keyboard.add(kb_button())

    elif data[0] == 6:  # todo strip to format
        if data[1] == 0 or data[1] == 1:
            u_s = db.users[call.from_user.id].settings
            text = "Ты, " + ("Ученик " if u_s.type_name == Type.CLASS else
                             ("Учитель, " if u_s.type_name == Type.TEACHER else "Кабинет №")) + \
                   db.get(u_s.type_id, u_s.type_name) + "\n" + ("Получаешь" if u_s.notifications else "Получаешь") + \
                   " уведомления об изменениях\nВывод по умолчанию:\n- Расписание: " + \
                   presentation_to_string(u_s.default_presentation) + "\n- Изменения: " + \
                   presentation_to_string(u_s.default_presentation_changes) + "\n- Свободные кабинеты: " + \
                   presentation_to_string(u_s.default_presentation_rooms) + "\nВыбирай, что хочешь изменить"
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            keyboard.add(types.InlineKeyboardButton(text="Оповещения вкл/выкл", callback_data="6.1"),
                         types.InlineKeyboardButton(text="Изменить себя", callback_data="1.6.0"),
                         types.InlineKeyboardButton(text="Расписание по дефолту", callback_data="6.2.0"),
                         types.InlineKeyboardButton(text="Изменения по дефолту", callback_data="6.3.0"),
                         types.InlineKeyboardButton(text="Свободные кабинеты по дефолту", callback_data="6.4.0"))
            keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="2.0"))
            if data[1] == 1:
                db.users[call.from_user.id].settings.notifications = not \
                    db.users[call.from_user.id].settings.notifications
        elif len(data) > 2:
            if data[1] == 3:
                if data[2] != 0:
                    db.users[call.from_user.id].settings.default_presentation_changes = data[2]
                    call.data = "6.0"
                    return callback(call, db)
                text = "Выбирай!"
                keyboard = types.InlineKeyboardMarkup(row_width=3)
                k_bs = [types.InlineKeyboardButton(text="Все классы", callback_data="6.3.5"),
                        types.InlineKeyboardButton(text="Мой класс", callback_data="6.3.6")]
                if db.users[call.from_user.id].settings.type_name == Type.CLASS:
                    keyboard.add(k_bs[0], k_bs[1])
                else:
                    keyboard.add(k_bs[0])
                keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="2.0"))
            elif data[1] == 2:
                if data[2] != 0:
                    db.users[call.from_user.id].settings.default_presentation = data[2]
                    call.data = "6.0"
                    return callback(call, db)
                text = "Выбирай!"
                keyboard = types.InlineKeyboardMarkup(row_width=3)
                keyboard.add(types.InlineKeyboardButton(text="Вся неделя", callback_data="6.2.1"),
                             types.InlineKeyboardButton(text="Текущий день", callback_data="6.2.2"),
                             types.InlineKeyboardButton(text="Следующий день", callback_data="6.2.3"),
                             types.InlineKeyboardButton(text="Ближайший урок", callback_data="6.2.4"))
                keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="2.0"))
            elif data[1] == 4:
                if data[2] != 0:
                    db.users[call.from_user.id].settings.default_presentation_rooms = data[2]
                    call.data = "6.0"
                    return callback(call, db)
                text = "Выбирай!"
                keyboard = types.InlineKeyboardMarkup(row_width=3)
                keyboard.add(types.InlineKeyboardButton(text="Вся неделя", callback_data="6.4.1"),
                             types.InlineKeyboardButton(text="Текущий день", callback_data="6.4.2"),
                             types.InlineKeyboardButton(text="Следующий день", callback_data="6.4.3"),
                             types.InlineKeyboardButton(text="Ближайший урок", callback_data="6.4.4"))
                keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="2.0"))
    elif data[0] == 7:  # todo strip to format
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(types.InlineKeyboardButton(text="Информациа о боте", callback_data="7.1"),
                     types.InlineKeyboardButton(text="Помощь", callback_data="7.2"),
                     types.InlineKeyboardButton(text="Обратная связь", callback_data="7.3"),
                     types.InlineKeyboardButton(text="Назад", callback_data="2.0"))
        if data[1] == 1:
            text = "Тут должна будет быть инфа о боте, когда-нибдь запилю"
        elif data[1] == 2:
            text = config.help_mes
        elif data[1] == 3:
            text = "Ты хочень что-то рассказать о боте? Или просто по-общаться со мной? Давай! Напиши что-нибудь!"
        elif data[1] == 0:
            text = "Da-da?"
    elif data[0] == 8:  # todo strip to format
        text = "У тебя шикарный выбор"
        d = '.'.join(str(i) for i in data[1:])
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(types.InlineKeyboardButton(text="Пн", callback_data=d + ".0"),
                     types.InlineKeyboardButton(text="Вт", callback_data=d + ".1"),
                     types.InlineKeyboardButton(text="Ср", callback_data=d + ".2"),
                     types.InlineKeyboardButton(text="Чт", callback_data=d + ".3"),
                     types.InlineKeyboardButton(text="Пт", callback_data=d + ".4"),
                     types.InlineKeyboardButton(text="Сб", callback_data=d + ".5"))
        # register next step handler
    elif data[0] == 9:  # todo strip to format
        d = '.'.join(str(i) for i in data[1:])
        text = '\n'.join('/c_' + str(num + 1) + ' : ' + db.timetable.c_n[num] for num in range(len(db.timetable.c_n)))
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(types.InlineKeyboardButton(text="Отмена", callback_data=d + ".-1"))
        cur_state = d
    common.pool_to_edit.append(common.Edit(text=text, chat_id=call.from_user.id, inline_keyboard=keyboard,
                                           message_id=call.message.message_id))
    db.users[call.from_user.id].settings.current_state = cur_state


def message(msg, db):
    print('Message!')
    if msg.text == '/start':
        if msg.from_user.id not in db.users:
            db.add_user(msg)
            common.pool_to_send.append(common.Message(text="User added"))
            text = "Привет, " + str(msg.from_user.first_name) + \
                   "!\nЯ буду показывать тебе расписание, но сначала я должен узнать немного о тебе"
            keyboard = types.InlineKeyboardMarkup().\
                add(types.InlineKeyboardButton(text="Дальше", callback_data="1.2.0"))

            # TODO: write a normal start message and add set class on startup
            db.users[msg.from_user.id].settings.current_state = "2.0"
        else:
            text = str(msg.from_user.first_name) + ", ты уже зарегистрирован"
            keyboard = config.default_keyboard
        common.pool_to_send.append(common.Message(text=text, to_user_id=msg.from_user.id, inline_keyboard=keyboard))
    elif msg.text == '/menu':
        if msg.from_user.id in db.users:
            db.users[msg.from_user.id].settings.current_state = "2.0"
            text = "Чем могу быть полезен?"
            common.pool_to_send.append(common.Message(text=text, to_user_id=msg.from_user.id,
                                                      inline_keyboard=config.default_keyboard))
        else:
            msg.text = "/start"
            return message(msg, db)
    elif msg.text == '/help':
        if msg.from_user.id in db.users:
            text = config.help_mes
            common.pool_to_send.append(common.Message(text=text, to_user_id=msg.from_user.id,
                                                      inline_keyboard=config.default_keyboard))
        else:
            msg.text = "/start"
            return message(msg, db)
    elif msg.text == '/sudowrite':
        db.write_all()
    elif db.users[msg.from_user.id].settings.current_state == 0 or \
            db.users[msg.from_user.id].settings.current_state == "0":
        text = "Старые команды не работают. Используй новые с /menu"
        common.pool_to_send.append(common.Message(text=text, to_user_id=msg.from_user.id))
    else:
        text = "Я всё равно не приму 🌚"
        common.pool_to_send.append(common.Message(text=text, to_user_id=msg.from_user.id))


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
