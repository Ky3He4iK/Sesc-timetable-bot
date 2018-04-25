import IO
import Timetable
import update_timetable
from Type import *
import common


class User:
    class Settings:
        def __init__(self, type_name=Type.CLASS, type_id=10, notify=True, current_state=0,
                     default_presentation=Presentation.ALL_WEEK, default_presentation_changes=Presentation.ALL_CLASSES,
                     default_presentation_rooms=Presentation.ALL_WEEK):
            self.type_name = type_name
            self.type_id = type_id
            self.notify = notify
            self.current_state = current_state
            self.default_presentation = default_presentation  # 0 - all week; 1 - current day; 2 - near lesson
            self.default_presentation_changes = default_presentation_changes  # 4 - all changes; 5 - for one class
            # (only if type is class)
            self.default_presentation_rooms = default_presentation_rooms  # 0 - all days; 1 - current day; 2 - next day;

            # 3 - near lesson

        def __dict__(self):
            return {
                'type_name': self.type_name,
                'type_id': self.type_id,
                'notify': self.notify,
                'current_state': self.current_state,
                'default_presentation': self.default_presentation,
                'default_presentation_changes': self.default_presentation_changes,
                'default_presentation_rooms': self.default_presentation_rooms
            }

        def restore(self, original):
            self.type_name = original['type_name']
            self.type_id = original['type_id']
            self.notify = original['notify']
            self.current_state = original['current_state']
            self.default_presentation = original['default_presentation']
            self.default_presentation_changes = original['default_presentation_changes']
            self.default_presentation_rooms = original['default_presentation_rooms']
            return self

    def __init__(self, internal_id=-1, username=None, user_id=None, type_name=Type.CLASS, type_id=5,
                 first_name=None, last_access=0):
        self.internal_id = internal_id
        self.username = username
        self.user_id = user_id
        self.first_name = first_name
        self.last_access = last_access
        self.settings = self.Settings(type_name, type_id)

    def restore(self, original):
        self.internal_id = original['internal_id']
        self.username = original['username']
        self.user_id = original['user_id']
        if 'last_access' in original:
            self.last_access = original['last_access']
        else:
            self.last_access = 0
        self.settings = self.Settings()
        if 'settings' in original:
            self.settings.restore(original['settings'])
        return self

    def re_set(self, type_name, type_id):
        self.settings.type_id = type_id
        self.settings.type_name = type_name

    def __dict__(self):
        return {
            'internal_id': self.internal_id,
            'username': self.username,
            'user_id': self.user_id,
            'first_name ': self.first_name,
            'last_access': self.last_access,
            'settings': self.settings.__dict__()
        }


class Feedback:
    class FBType:
        DENIED = -1
        UNREAD = 0
        WAITING = 1
        SOLVING = 2
        SOLVED = 3

    def __init__(self, user_chat_id=-1, text=None, self_num=-1):
        self.user_chat_id = user_chat_id
        self.self_num = self_num
        self.text = text
        self.condition = self.FBType.UNREAD

    def restore(self, original):
        self.user_chat_id = original['user_chat_id']
        self.self_num = original['self_num']
        self.text = original['text']
        self.condition = original['condition']
        return self

    def __dict__(self):
        return {
            'user_chat_id': self.user_chat_id,
            'self_num': self.self_num,
            'text': self.text,
            'condition': self.condition
        }


class Db:
    def __init__(self):
        try:
            self.read_all()
            print("Read!")
        except FileNotFoundError:
            print("Files not found. Updating...")
            self.users = {0: User() for _ in range(0)}
            self.feedback = [Feedback() for _ in range(0)]
            self.timetable = Timetable.Timetable()
            update_timetable.t_update(self.timetable)
            self.write_all()
            print("Updated!")

    def write_feedback(self):
        IO.FileIO.write_json("data/feedback.json", [fb.__dict__() for fb in self.feedback])

    def add_feedback(self, user_chat_id=-1, text=None):
        if len(self.feedback) == 0:
            f_n = 0
        else:
            f_n = self.feedback[-1].self_num + 1
        self.feedback.append(Feedback(user_chat_id, text, f_n))
        self.write_feedback()
        common.send_message(text="FEEDBACK", inline_keyboard=-1)

    def remove_feedback(self, feedback_id):
        if 0 <= feedback_id < len(self.feedback):
            self.feedback.pop(feedback_id)
            self.write_feedback()
        else:
            raise ValueError("Too big index", feedback_id)

    def add_user(self, message):
        self.users[message.from_user.id] = User(internal_id=len(self.users), user_id=message.from_user.id)

    def set_user(self, user_chat_id, n_type, n_type_id):
        if n_type_id == -1:
            return "Я тебя не могу узнать. Может ещё разок?"
        self.users[user_chat_id].re_set(n_type, n_type_id)
        if n_type == Type.CLASS:
            if self.timetable.c_n[n_type_id] == '10е':
                return "Добро пожаловать в 10е"
            return "Теперь ты учишься в " + self.timetable.c_n[n_type_id]
        if n_type_id == Type.ROOM:
            return "Теперь ты - представитель в телеграмме комнаты №" + self.timetable.get_room_long(n_type_id) + \
                   ". Тебе не кажется, что ещё надо оффициальную страницу во всех соцсетях запилить?"
        return "Теперь Вы - представитель почётной проффессии - педагог " + self.timetable.t_n[n_type_id]

    def write_all(self):
        IO.FileIO.write_json("data/users.json", {key: self.users[key].__dict__() for key in list(self.users)})
        self.write_feedback()
        IO.FileIO.write_json("data/timetable.json", self.timetable)
        return True

    def read_all(self):
        # self.users = [User().restore(origin) for origin in IO.FileIO.read_json("users.json")]
        self.timetable = Timetable.Timetable().restore(IO.FileIO.read_json("data/timetable.json"))
        self.feedback = [Feedback().restore(origin) for origin in IO.FileIO.read_json("data/feedback.json")]

        u_t = IO.FileIO.read_json("data/users.json")
        self.users = {int(key): User().restore(u_t[key]) for key in list(u_t)}
        return self

    def update(self, fast=False):
        # return self.timetable is not None and self.timetable.update() and self.write_all()
        return self.timetable is not None and update_timetable.t_update(self.timetable, fast=fast) and self.write_all()

    @staticmethod
    def find_sub(string, array):
        t = array.index(string)
        if t != -1 or string is None:
            return t
        t = len(string)
        for i in range(len(array)):
            if array[i] is None:
                continue
            if t <= len(array[i]) and array[i][:t].lower() == string:
                if i < len(array) + 1 and len(array[i + 1]) >= t and array[i + 1][:t].lower() == string:
                    return -1
                return i
        return -1

    def get_day_id(self, day):  # TODO: do
        # TODO: add another kinds of input string
        if day.isdecimal():
            t = int(day) - 1
            if 0 <= t < 6:
                return t
        return self.find_sub(day, self.timetable.d_n)

    def get_room_id(self, room):
        t = self.timetable.r_n.index(room)
        if t == -1:
            if room.isdecimal():
                t = int(room) - 1
                if 0 <= t < len(self.timetable.r_n):
                    return t
            t = self.find_sub(room, self.timetable.r_n)
            if t == -1:
                t = self.find_sub(room, self.timetable.r_i)
        return t

    def get_class_id(self, class_):
        class_ = class_.lower()
        if class_.isdecimal():
            t = int(class_) - 1
            if 0 <= t < len(self.timetable.c_n):
                return t
        return self.find_sub(class_.replace("e", "е").replace("a", "а").replace("b", "б").replace("v", "в").
                             replace("g", "г").replace("d", "д").replace("z", "з").replace("k", "к").replace("c", "к").
                             replace("l", "л").replace("m", "м").replace("n", "н"), self.timetable.c_n)

    def get_teacher_id(self, teacher):
        if teacher.isdecimal():
            t = int(teacher) - 1
            if 0 <= t < len(self.timetable.t_n):
                return t

    def get_id(self, data, type_):  # TODO: do
        if data != '':
            if type_ == Type.CLASS:
                return self.get_class_id(data)
            if type_ == Type.ROOM:
                return self.get_room_id(data)
            if type_ == Type.TEACHER:
                return self.get_teacher_id(data)
            if type_ == Type.DAY:
                return self.get_day_id(data)
        return -1

    def get(self, ind, type_):
        if type_ == Type.CLASS:
            return self.timetable.c_n[ind]
        if type_ == Type.ROOM:
            return self.timetable.r_n[ind]
        if type_ == Type.TEACHER:
            return self.timetable.t_n[ind]
        if type_ == Type.DAY:
            return self.timetable.d_n[ind]
        if type_ == Type.USER:
            return self.users[list(self.users)[ind]]
        return -1
