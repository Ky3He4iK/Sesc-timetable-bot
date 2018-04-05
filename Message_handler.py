from telebot import types

from Type import *
import common
import config


def kb_button(text="Назад", data=([2, 0] + [-1] * 6)):
    return types.InlineKeyboardButton(text=text, callback_data='.'.join(str(d) for d in data))


def callback(user_id, data, db, mes_id=None):
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

    # data = extract_id_from_text(call.data)
    cur_state = data
    text = "Чем могу помочь?"
    keyboard = None
    print(data)
    if data[0] == 1:
        if data[1] == 0:
            text = "Выбирите тип"
        elif data[1] == Type.CLASS:
            text = '\n'.join('/c_' + str(num + 1) + ' : ' + db.timetable.c_n[num]
                             for num in range(len(db.timetable.c_n)))
        elif data[1] == Type.TEACHER:
            text = '\n'.join('/t_' + str(num + 1) + ' : ' + db.timetable.c_n[num]
                             for num in range(len(db.timetable.t_n)))
        elif data[1] == Type.ROOM:
            text = '\n'.join('/r_' + str(num + 1) + ' : ' + db.timetable.c_n[num]
                             for num in range(len(db.timetable.r_i)))
        cur_state = data[2:4] + [-1] * 6
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(kb_button("Класс", [1, Type.CLASS] + data[2:4] + [-1] * 4),
                     kb_button("Учитель", [1, Type.TEACHER] + data[2:4] + [-1] * 4),
                     kb_button("Кабинет", [1, Type.ROOM] + data[2:4] + [-1] * 4))

    elif data[0] == 2:
        if data[1] == 1:
            text = "Расписание звонков:\n" + common.bells
        elif len(data) > 2:
            if data[-1] == -1:
                return callback(user_id, [1, 2] + [-1] * 6, db, mes_id)
            db.users[user_id].settings.type_name = data[2]
            db.users[user_id].settings.type_id = data[3]
        elif data[1] == 3:
            text = "Ну что же ты так?("

    elif data[0] == 3:
        u_settings = db.users[user_id].settings
        ind_type = [data[5], data[4]]  # why reverse? Just for lulz!
        day = data[6]

        if day == -1:
            day = 7
        if ind_type[0] == -1:
            ind_type[0] = u_settings.type_id
        if ind_type[1] == -1:
            ind_type[1] = u_settings.type_name
        pr = u_settings.default_presentation
        if data[1] != 0:
            pr = data[1]
        text = db.timetable.get_timetable(pr, ind_type[1], ind_type[0], day)
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
        d_p = db.users[user_id].settings.default_presentation_changes
        if data[1] != 0:
            d_p = data[1]
        if d_p == Presentation.OTHER and data[5] != -1:
            text = db.timetable.changes.get_changes(db.timetable, data[5])
        else:
            text = db.timetable.changes.get_changes(db.timetable, d_p, db.users[user_id].settings.type_id)
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        k_bs = [kb_button("Все классы", [4, Presentation.ALL_CLASSES, -1, -1, -1, -1, -1, Presentation.ALL_CLASSES]),
                kb_button("Определенный класс", [9, 0, 4, Presentation.OTHER, -1, -1, -1, Presentation.OTHER]),
                kb_button("\"Мой\" класс", [4, Presentation.CURRENT_CLASS, -1, -1, -1, -1, -1,
                                            Presentation.CURRENT_CLASS])]
        if db.users[user_id].settings.type_name == Type.CLASS:
            keyboard.add(k_bs[0], k_bs[1], k_bs[2])
        else:
            keyboard.add(k_bs[0], k_bs[1])
        keyboard.add(kb_button())

    elif data[0] == 5:
        dp = db.users[user_id].settings.default_presentation
        if data[1] != 0:
            dp = data[1]
        if data[6] == -1:
            data[6] = 7
        text = db.timetable.free_rooms.get_free_pres(db.timetable, dp, data[6])
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(kb_button("Сегодня", [5, Presentation.TODAY] + [-1] * 5 + [Presentation.TODAY]),  # 2
                     kb_button("Сейчас", [5, Presentation.NEAR] + [-1] * 5 + [Presentation.NEAR]),  # 4
                     kb_button("Завтра", [5, Presentation.TOMORROW] + [-1] * 5 + [Presentation.TOMORROW]),  # 3
                     kb_button("На неделю", [5, Presentation.ALL_WEEK] + [-1] * 5 + [Presentation.ALL_WEEK]),  # 1
                     kb_button("Конкретный день", [8, 0, 5, data[1]] + [-1] * 3 + [data[1]]))  # 1
        keyboard.add(kb_button())

    elif data[0] == 6:
        if data[1] == 0 or data[1] == 1:
            if data[1] == 1:
                db.users[user_id].settings.notify = not \
                    db.users[user_id].settings.notify
            u_s = db.users[user_id].settings
            text = "Ты, " + ("Ученик " if u_s.type_name == Type.CLASS else
                             ("Учитель, " if u_s.type_name == Type.TEACHER else "Кабинет №")) + \
                   db.get(u_s.type_id, u_s.type_name) + "\n" + ("Получаешь" if u_s.notify else "Получаешь") + \
                   " уведомления об изменениях\nВывод по умолчанию:\n- Расписание: " + \
                   presentation_to_string(u_s.default_presentation) + "\n- Изменения: " + \
                   presentation_to_string(u_s.default_presentation_changes) + "\n- Свободные кабинеты: " + \
                   presentation_to_string(u_s.default_presentation_rooms) + "\nВыбирай, что хочешь изменить"
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            keyboard.add(kb_button("Оповещения вкл/выкл", [6, 1] + [-1] * 6),
                         kb_button("Изменить себя", [1, 0, 6, 0] + [-1] * 4),
                         kb_button("Расписание по дефолту", [6, 2] + [-1] * 6),
                         kb_button("Изменения по дефолту", [6, 3] + [-1] * 6),
                         kb_button("Свободные кабинеты по дефолту", [6, 4] + [-1] * 6))
            keyboard.add(kb_button())

        elif data[1] == 2:
            if data[7] != -1:
                db.users[user_id].settings.default_presentation = data[7]
                return callback(user_id, [6, 0] + [-1] * 6, db, mes_id)
            text = "Выбирай!"
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            keyboard.add(kb_button("Вся неделя", [6, 2] + [-1] * 5 + Presentation.ALL_WEEK),
                         kb_button("Текущий день", [6, 2] + [-1] * 5 + Presentation.TODAY),
                         kb_button("Следущий день", [6, 2] + [-1] * 5 + Presentation.TOMORROW),
                         kb_button("Ближайший урок", [6, 2] + [-1] * 5 + Presentation.NEAR))
            keyboard.add(kb_button())

        elif data[1] == 3:
            if data[7] != -1:
                db.users[user_id].settings.default_presentation_changes = data[7]
                return callback(user_id, [6, 0] + [-1] * 6, db, mes_id)
            text = "Выбирай!"
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            k_bs = [kb_button("Все классы", [6, 3] + [-1] * 5 + [Presentation.ALL_CLASSES]),
                    kb_button("\"Мой\" класс", [6, 3] + [-1] * 5 + [Presentation.CURRENT_CLASS])]
            if db.users[user_id].settings.type_name == Type.CLASS:
                keyboard.add(k_bs[0], k_bs[1])
            else:
                keyboard.add(k_bs[0])
            keyboard.add(kb_button())

        if data[1] == 4:
            if data[7] != -1:
                db.users[user_id].settings.default_presentation_rooms = data[7]
                return callback(user_id, [6, 0] + [-1] * 6, db, mes_id)
            text = "Выбирай!"
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            keyboard.add(kb_button("Вся неделя", [6, 4] + [-1] * 5 + [Presentation.ALL_WEEK]),
                         kb_button("Текущий день", [6, 4] + [-1] * 5 + [Presentation.TODAY]),
                         kb_button("Следующий день", [6, 4] + [-1] * 5 + [Presentation.TOMORROW]),
                         kb_button("Ближайший урок", [6, 4] + [-1] * 5 + [Presentation.NEAR]))
            keyboard.add(kb_button())

    elif data[0] == 7:
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(kb_button("Информация о боте", [7, 1] + [-1] * 6),
                     kb_button("Помощь", [7, 2] + [-1] * 6),
                     kb_button("Обратная связь", [7, 3] + [-1] * 6),
                     kb_button())
        if data[1] == 1:
            text = "Тут должна будет быть инфа о боте, когда-нибдь запилю"
        elif data[1] == 2:
            text = config.help_mes
        elif data[1] == 3:
            text = "Ты хочень что-то рассказать о боте? Или просто по-общаться со мной? Давай! Напиши что-нибудь!"
        elif data[1] == 0:
            text = "Da-da?"

    elif data[0] == 8:
        text = "У тебя шикарный выбор"
        d = data[2:4] + [-1] * 2 + data[4:6]
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(kb_button("Пн", d + [0, data[7]]),
                     kb_button("Вт", d + [1, data[7]]),
                     kb_button("Ср", d + [2, data[7]]),
                     kb_button("Чт", d + [3, data[7]]),
                     kb_button("Пт", d + [4, data[7]]),
                     kb_button("Сб", d + [5, data[7]]),
                     kb_button("Вся неделя", d + [7, data[7]]))

    elif data[0] == 9:
        d = data[2:4] + [-1] * 6
        text = '\n'.join('/c_' + str(num + 1) + ' : ' + db.timetable.c_n[num] for num in range(len(db.timetable.c_n)))
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(kb_button("Обратно", d))
        cur_state = d

    if mes_id is None:
        common.pool_to_send.append(common.Message(text=text, to_user_id=user_id, inline_keyboard=keyboard))
    else:
        common.pool_to_edit.append(common.Edit(text=text, chat_id=user_id, inline_keyboard=keyboard, message_id=mes_id))
    db.users[user_id].settings.current_state = cur_state


def message(msg, db):
    print('Message!')
    if msg.text == '/start':
        if msg.from_user.id not in db.users:
            db.add_user(msg)
            common.pool_to_send.append(common.Message(text="User added"))
            text = "Привет, " + str(msg.from_user.first_name) + \
                   "!\nЯ буду показывать тебе расписание, но сначала я должен узнать немного о тебе"
            keyboard = types.InlineKeyboardMarkup().add(kb_button("Дальше"), [1, 0, 2, 0] + [-1] * 4)
            db.users[msg.from_user.id].settings.current_state = [1, 0, 2, 0] + [-1] * 4
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
    elif msg.text == '/sudowrite' and msg.from_user.id == config.father_chat:
        db.write_all()
    elif msg.text[0] == '/':
        if (msg.text.startswith('/c_') or msg.text.startswith('/t_') or msg.text.startswith('/r_')) and \
                msg.text[3:].isdecimal():
            tp = Type.CLASS if msg.text[1] == 'c' else (Type.TEACHER if msg.text[1] == 't' else Type.ROOM)
            ind = int(msg.text[3:])
            if db.timetable.check_has(tp, ind):
                data = db.users[msg.from_user.id].settings.current_state
                data[4], data[5] = tp, ind
                callback(user_id=msg.from_user.id, db=db, data=data)


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
