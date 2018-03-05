# from main import pool_to_send
from Legacy import Legacy
from Type import Type
from Db import Feedback
import config
import common


def get_command(text):
    if text[0] == '/':
        text = text[1:]
    if ' ' in text:
        return text[:text.find(' ')]
    return text


def cmp(command, text, has_arguments=True):
    if has_arguments:
        return text[:min(len(text), len(command))] == command
    return text == command


def ans_tt(message, db):
    l = Legacy(message, db)
    return db.timetable.get_timetable(l.type_id, l.type, l.day)


def ans_today(message, db):
    l = Legacy(message, db)
    return db.timetable.get_timetable(l.type_id, l.type, common.c_day % 6)


def ans_tomorrow(message, db):
    l = Legacy(message, db)
    if common.c_day >= 5:
        day = 0
    else:
        day = common.c_day + 1
    return db.timetable.get_timetable(l.type_id, l.type, day)


def ans_near(message, db):
    l = Legacy(message, db)
    if common.c_les >= 6:
        if common.c_day >= 5:
            day = 0
        else:
            day = common.c_day + 1
        return db.timetable.d_n[day] + '. 1-й урок. ' + db.get(l.type_id, l.type) + ':\n' + \
               db.timetable.get_timetable_les(l.type, day, 0, l.type_id)
    return db.timetable.d_n[common.c_day] + '. 1-й урок. ' + db.get(l.type_id, l.type) + \
           ':\n' + db.timetable.get_timetable_les(l.type, common.c_day, 0, l.type_id)


def ans_all(message, db):
    l_t = Legacy(message, db).type
    if l_t == Type.ROOM:
        return '\n'.join(str(r + 1) + '. ' + db.timetable.get_room(r) for r in range(len(db.timetable.r_i))
                         if db.timetable.r_i[r] != 'Hz')
    if l_t == Type.TEACHER:
        return '\n'.join(str(t + 1) + '. ' + db.timetable.t_n(t) for t in range(len(db.timetable.t_n)))
    return '\n'.join(str(c + 1) + '. ' + db.timetable.c_n(c) for c in range(len(db.timetable.c_n)))


def ans_long(message, db):
    return "Эта не та команда, которую ты ищешь"


def ans_fb(message, db):
    if ' ' not in message.text:
        return "А как же сообщение?"
    db.add_feedback(db.get_user_id(message.from_user.id), message.text[message.text.index(' ') + 1:])
    common.pool_to_send.append(common.Message('FEEDBACK!'))
    return "Спасибо за обратную связь!"


def ans_examples(message, db):
    return "Итак, сферический в вакууме школьник Выся решил воспользоваться моим ботом. Вот некоторые варианты его " \
           "действий:\n/start - Если вы каким-то образом смогли начать беседу с ботом без этой фразы, то я раз за " \
           "вас, но лучше её всё-таки ввести\n/tt - Маны не читаем, действуем наобум. Но ничего приличного не будет. " \
           "Только расписание для 10е\n/help - Всё-таки лучше прочитать. В дальнейшей работе с ботом пригодится\n/tt " \
           "c 10a - Другое дело. (А то, что учитель у английского и физкультуры ни разу не задан - не баг, а фича. " \
           "Достопочтенные сотрудники отдела компьютеризации именно так настроили)\n/fb Бот на запросы отвечает " \
           "неправильно - Ни здрасьте, ни подробного описания ошибки нету. Не надо так, а то забаню (нет. Мне лень " \
           "вписывать в бота бан-лист) \n/set t 151 -  Учителям надоело каждый раз вводить свои имена? Всего одна " \
           "комманда и вместо кошерного расписания 10е будет выводится заданное расписание (это учитель-заглушка для " \
           "сайта, и у него несколько классов по различным предметам одновременно)\n/near - Какй сейчас будет урок?\n" \
           "/freenow - Вася решил прогулять следущий урок в каком-нибудь свободном кабинете и таким образом решил " \
           "найти его\n/changes - Посмотреть существующие изменения в расписании\n/today - А какие вообще уроки " \
           "сегодня? (Хороший вопрос в 8.59)\n/tomorrow - Так. А на завтра?\n/getme - это точно расписание для моего " \
           "класса?\n/all r - а какие кабинеты тут есть? И их ровно 42?\n/free Вт - Какие свободные кабинеты во " \
           "вторник? (Если писать словами, то временно есть неиллюзорная вероятность неопознания ботом дня недели. " \
           "Временная, конечно)\n/ping - Аналог тыканья палкой - проверить работоспособность бота\n"


def ans_helpold(message, db):
    return "<type> - Может быть: c - класс, t - учитель, r - кабинет (по умолчанию c)\n[day] - Номер дня в неделе от " \
           "1 до 6 либо ничего если нужно для всей недели\n<id> - Индекс интересующего класса/учителя/кабинета либо " \
           "их непосредственная запись\n\n/ping - Проверка доступности бота\n/all <type> - Список всех классов, " \
           "учителей, комнат\n/bells - Расписание звонков\n/changes [id] - Изменения для всех/определённого класса\n" \
           "/fb <mes> - Сказать мне что-нибудь. Лучше что-нибудь полезное для меня\n/feedback <mes> - Как /fb\n/free" \
           " [day] - Свободные кабинеты в данный день\n/freenow - Свободные кабинеты на ближайшем уроке\n/examples - " \
           "Примеры комманд. Лучше ознакомиться, будет комфортнее работать с ботом\n/getme - Получить type и id для " \
           "этого человека\n/help - Это сообщение\n/near <type> <id> - Следующий урок\n/set <type> <id> - Изменить " \
           "type и id по умолчанию на свой вариант\n/start - Если бот не знает тебя\n/timetable <type> <id> [day] - " \
           "goto /tt\n/today <type> <id> - Расписание на сегодня\n/tomorrow <type> <id> - Расписание на завтра\n" \
           "/tt <type> <id> [day] - Расписание\n/changelog - информация об последних обновлениях бота\n\nНапример, " \
           "\"/tt c 10e\" выдаст расписание для 10е, а \"/tt r 206 4\" выдаст расписание для 206 кабинета в четверг\n" \
           "Если ввести данные некорректно, то бот может ответить как угодно, но во многих случаях не обязательно " \
           "вводить <type>, а <id> в случае инициалов учителя может быть неполным, если можно однозначно опеределить " \
           "учителя\nИ ещё: пересылать сообщения тоже можно, но будет учитываться текст только в пересылаемом " \
           "сообщение\n\nВсе данные о расписании берутся с сайта http://lyceum.urfu.ru"


def ans_free(message, db):
    l = Legacy(message, db)
    if l.day == 7:
        return db.timetable.free_rooms.form(db.timetable)
    return db.timetable.free_rooms.form(db.timetable, l.day)


def ans_freenow(message, db):
    return db.timetable.d_n[common.c_day] + '. ' + \
           db.timetable.free_rooms.form(db.timetable, min(common.c_day, 5), min(common.c_les, 6))


def ans_changes(message, db):
    l = Legacy(message, db)
    if l.type == Type.CLASS:
        return db.timetable.changes.get_changes(db.timetable, l.type_id)
    return db.timetable.changes.get_changes(db.timetable)


def ans_set(message, db):
    l = Legacy(message, db)
    return db.set_user(db.get_user_id(message.from_user.id), l.type, l.type_id)


def ans_getme(message, db):
    u_id = db.get_user_id(message.from_user.id)
    if u_id == -1:
        return "Я тебя не знаю"
    ind = db.users[u_id].type_id
    t = db.users[u_id].type_name
    return ("Класс, " + db.timetable.c_n[ind]) if t == Type.CLASS else ((("Комната, ") + db.timetable.get_room_long(ind)) if t == Type.ROOM else ("Учитель, " + db.timetable.t_n))


def ans_bells(message, db):
    return "1. 9:00 - 9.40\n2. 9:50 - 10.30\n3. 10:45 - 11.25\n4. 11:40 - 12.20\n5. 12:35 - 13.15\n6. 13:15 - 14.15\n" \
           "7. 14:15 - 15.15"


def ans_sudo_update(message, db):
    return "Ok" if db.timetable.update() else "Not ok"


def ans_sudo_write(message, db):
    return str(db.write_all())


def ans_sudo_get(message, db):
    def sub(user_id):
        return str(db.users[user_id].username) + ' (' + str(db.users[user_id].user_id) + ')'

    def stat(fb_stat):
        if fb_stat == Feedback.FBType.UNREAD:
            return "unread"
        if fb_stat == Feedback.FBType.DENIED:
            return "denied"
        if fb_stat == Feedback.FBType.SOLVED:
            return "solved"
        if fb_stat == Feedback.FBType.SOLVING:
            return "solving"
        if fb_stat == Feedback.FBType.WAITING:
            return "waiting"
        return "unknown"

    if len(db.feedback) == 0:
        return "Empty"

    if ' ' in message.text:
        n = message.text.split()[1]
        if not n.isdecimal():
            return "Wrong num"
        n = int(n)
        if n >= len(db.feedback):
            return "It's too big!"
        db.feedback[n].condition = Feedback.FBType.WAITING
        return str(n) + '. ' + sub(db.feedback[n].user_internal_id) + ' - ' + stat(db.feedback[n].condition) + '\n' + \
               db.feedback[n].text

    return '\n'.join(str(fb) + '. ' + sub(db.feedback[fb].user_internal_id) + ' - ' + stat(db.feedback[fb].condition)
                     for fb in range(len(db.feedback)))


def ans_sudo_ans(message, db):
    text = message.text.split(' ')
    if len(text) < 3:
        return "/sudosay <id> <text>"
    if text[1].isdecimal():
        ind = int(text[1])
        db.feedback[ind].condition = Feedback.FBType.WAITING
        return common.pool_to_send.append(common.Message(' '.join(text[2:]), db
                                                         .users[db.feedback[ind].user_internal_id].user_id))
    return "Wrong id"


def ans_sudo_say(message, db):
    text = message.text.split(' ')
    if len(text) < 3:
        return "/sudosay <id> <text>"
    if text[1].isdecimal():
        ind = int(text[1])
        if db.get_user_id(ind) == -1:
            return "Wrong id"
        return common.pool_to_send.append(common.Message(' '.join(text[2:]), ind))
    return "Wrong id"


def ans_sudo_send(message, db):
    if message.text == '/sudosay':
        return "What message?"
    text = message.text[message.text.index(' ') + 1:]
    for u in db.users:
        try:
            common.pool_to_send.append(common.Message(text, u.user_id))
        except BaseException as e:
            print(e.with_traceback(e.__traceback__))
            common.pool_to_send.append(common.Message(str(e) + ' ' + str(e.args)))
            common.pool_to_send.append(common.Message("Error at " + str(u.user_id) + '\\' + str(u.username)))
        common.pool_to_send.append(common.Message('Finished'))


def ans_sudo_default(message, db):
    return "/sudoupdate [any]\n/sudowrite\n/sudoget\n/sudoans <id> <text> - ans to feedback\n" \
           "/sudosay <id> <text> - say by id\n/sudosend <text> - send to all"


def ans_default(message, db):
    return "Не знаю я такой команды"


def ans_changelog(message, db):
    return "Версия 1.1.0\n- Восстановлена полноценная работа бота\n- Исправлено указание наличия изменений при " \
           "выдаче расписания класса\n- Исправление мелких косяков и добавление багов\n" \
           "Версия 2.0\nСмена ужасного кода на чуть получше, подготовка к клавам, понижена стабильность"


def legacy_hub(message, db):
    txt = get_command(message.text)
    if cmp("tt", txt) or cmp("timetable", txt):
        return ans_tt(message, db)
    if cmp("today", txt):
        return ans_today(message, db)
    if cmp("tomorrow", txt):
        return ans_tomorrow(message, db)
    if cmp("near", txt):
        return ans_near(message, db)
    if cmp("all", txt):
        return ans_all(message, db)
    if cmp("sudo", txt):
        if message.from_user.username != 'Ky3He4iK' or message.from_user.id != config.father_chat:
            return ans_default(message, db)
        txt = txt[4:]
        if cmp("update", txt):
            return ans_sudo_update(message, db)
        if cmp("write", txt):
            return ans_sudo_write(message, db)
        if cmp("ans", txt):
            return ans_sudo_ans(message, db)
        if cmp("get", txt):
            return ans_sudo_get(message, db)
        if cmp("say", txt):
            return ans_sudo_say(message, db)
        if cmp("send", txt):
            return ans_sudo_send(message, db)
        return ans_sudo_default(message, db)
    if cmp("long", txt):
        return ans_long(message, db)
    if cmp("feedback", txt) or cmp("fb", txt):
        return ans_fb(message, db)
    if cmp("freenow", txt):
        return ans_freenow(message, db)
    if cmp("getme", txt):
        return ans_getme(message, db)
    if cmp("helpold", txt):
        return ans_helpold(message, db)
    if cmp("examples", txt):
        return ans_examples(message, db)
    if cmp("free", txt):
        return ans_free(message, db)
    if cmp("changes", txt):
        return ans_changes(message, db)
    if cmp("set", txt):
        return ans_set(message, db)
    if cmp("bells", txt):
        return ans_bells(message, db)
    if cmp("changelog", txt):
        return ans_changelog(message, db)
    return ans_default(message, db)
