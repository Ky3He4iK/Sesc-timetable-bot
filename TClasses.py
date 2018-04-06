import common
from Type import *


class Class:
    def __init__(self, ind, name):
        self.ind = ind
        self.name = name

    def __lt__(self, other):
        return self.name < other.name


class Room:
    def __init__(self, ind, name):
        self.ind = ind
        self.name = name

    def __lt__(self, other):
        return self.ind < other.ind


class Day:
    def __init__(self, ind, name):
        self.ind = ind
        self.name = name

    def __lt__(self, other):
        return self.ind < other.ind


class Teacher:
    def __init__(self, ind, name):
        self.ind = ind
        self.name = name

    def __lt__(self, other):
        return self.name < other.name


class TTDay:
    def __init__(self, class_count=0):
        self.day = [self.TTLesson(class_count) for _ in range(7)]  # array of TTL

    def __dict__(self):
        return {'day': [d.__dict__() for d in self.day]}

    class TTLesson:
        def __init__(self, class_count=0):
            self.lesson = [self.TTLClass() for _ in range(class_count)]  # array of classes

        def __dict__(self):
            return {'lesson': [d.__dict__() for d in self.lesson]}

        class TTLClass:
            def __init__(self):
                self.group = []  # array of lessons

            def __dict__(self):
                return {'group': [d.__dict__() for d in self.group]}

            class TTCell:
                def __init__(self, class_ind=-1, room_ind=-1, teacher_ind=-1, subject=-1, group_ind=0):
                    self.class_ind = class_ind
                    self.room_ind = room_ind
                    self.teacher_ind = teacher_ind
                    self.subject = [subject]
                    self.group_ind = group_ind

                def __lt__(self, cell):
                    return self.group_ind < cell.group_ind

                def __dict__(self):
                    return {
                        'class_ind': self.class_ind,
                        'room_ind': self.room_ind,
                        'teacher_ind': self.teacher_ind,
                        'subject': self.subject,
                        'group_ind': self.group_ind
                    }

                def restore(self, original):
                    self.class_ind = original['class_ind']
                    self.room_ind = original['room_ind']
                    self.teacher_ind = original['teacher_ind']
                    self.subject = original['subject']
                    self.group_ind = original['group_ind']
                    return self

            def restore(self, original):
                self.group = [self.TTCell().restore(origin) for origin in
                              original['group']]
                return self

        def restore(self, original):
            self.lesson = [self.TTLClass().restore(origin) for origin in original['lesson']]
            return self

    def restore(self, original):
        self.day = [self.TTLesson().restore(origin) for origin in original['day']]
        return self


class FreeRoomsAll:
    def __init__(self):
        self.all = [self.FreeRoomsDay() for _ in range(6)]  # array of FRD

    def set(self, timetable):
        for day in range(6):
            for les in range(7):
                busy = [False for _ in range(len(timetable.rooms))]
                for c in timetable.all[day].day[les].lesson:
                    for g in c.group:
                        busy[g.room_ind] = True
                self.all[day].day[les].lesson = [timetable.rooms[k].ind for k in range(len(busy)) if not busy[k]]

    def __dict__(self):
        return {
            'all': [a.__dict__() for a in self.all]
        }

    class FreeRoomsDay:
        def __init__(self):
            self.day = [self.FreeRoomsLesson() for _ in range(7)]  # array of FRL

        def __dict__(self):
            return {
                'day': [d.__dict__() for d in self.day]
            }

        class FreeRoomsLesson:
            def __init__(self):
                self.lesson = []  # array of string

            def __dict__(self):
                return {
                    'lesson': self.lesson
                }

            def restore(self, original):
                self.lesson = original['lesson']
                return self

        def restore(self, original):
            self.day = [self.FreeRoomsLesson().restore(origin) for origin in
                        original['day']]
            return self

    def restore(self, original):
        self.all = [self.FreeRoomsDay().restore(origin) for origin in original['all']]
        return self

    def form(self, timetable, day=7, les=-1):
        if day == 7:
            return '\n\n'.join(self.form(timetable, d, -1) for d in range(6))
        if les == -1:
            return timetable.d_n[day] + ':\n' + '\n'.join(self.form(timetable, day, l) for l in range(7))
        return '```\n' + str(les + 1) + '. ' + ', '.join(self.all[day].day[les].lesson) + '```'

    def get_free_today(self, timetable):
        return self.form(timetable, common.c_day % 6)

    def get_free_tomorrow(self, timetable):
        return self.form(timetable, ((common.c_day + 1) % 6) if common.c_day != 6 else 0)

    def get_free_near(self, timetable):
        if common.c_day > 5:
            c_d, c_l = 0, 0
        elif common.c_les > 6:
            c_d, c_l = common.c_day + 1, 0
        else:
            c_d, c_l = common.c_day, common.c_les
        return self.form(timetable, c_l, c_d % 6)

    def get_free(self, timetable, day=7, les=-1):
        return self.form(timetable, day, les)

    def get_free_pres(self, timetable, presentation, day=7):
        if presentation == Presentation.ALL_WEEK:
            return self.get_free(timetable)
        if presentation == Presentation.NEAR:
            return self.get_free_near(timetable)
        if presentation == Presentation.TOMORROW:
            return self.get_free_tomorrow(timetable)
        if presentation == Presentation.TODAY:
            return self.get_free_today(timetable)
        return self.get_free(timetable, day)


class Changes:
    def __init__(self, class_count=0):
        self.change_day = -1
        self.changes = [self.ChangesCell() for _ in range(0)]
        self.ch_ind = {}
        self.has_changes = [False for _ in range(class_count)]

    def __dict__(self):
        return {
            'change_day': self.change_day,
            'changes': [c.__dict__() for c in self.changes],
            'has_changes': self.has_changes,
            'ch_ind': self.ch_ind
        }

    class ChangesCell:
        def __init__(self, class_ind=None, change_data=None):
            self.class_ind = class_ind
            self.change_data = change_data

        def restore(self, original):
            self.class_ind = original['class_ind']
            self.change_data = original['change_data']
            return self

        def __dict__(self):
            return {
                'class_ind': self.class_ind,
                'change_data': self.change_data
            }

    def restore(self, original):
        self.change_day = original['change_day']
        self.has_changes = original['has_changes']
        self.changes = [self.ChangesCell().restore(origin) for origin in original['changes']]
        try:
            self.ch_ind = original['ch_ind']
        except KeyError:
            for class_ch_ind in range(len(self.changes)):
                self.ch_ind[self.changes[class_ch_ind].class_ind] = class_ch_ind
        return self

    def get_changes_pres(self, timetable, presentation, ind=-1):
        if presentation == Presentation.ALL_CLASSES:
            return self.get_changes(timetable)
        if presentation == Presentation.CURRENT_CLASS:
            return self.get_changes(timetable, ind)
        return self.get_changes(timetable, ind)

    def get_changes(self, timetable, class_ind=None, inline=False):
        if self.change_day == -1:
            return "Нет данных об изменениях"
        if class_ind is None:
            ans = ''
            for change_cell in self.changes:
                ans += timetable.c_n[change_cell.class_ind] + ':\n'
                for i in range(len(change_cell.change_data)):
                    ans += ('├ ' if i != len(change_cell.change_data) - 1 else '└ ') + change_cell.change_data[i] + '\n'
                ans += '\n'
            ans = timetable.d_n[self.change_day] + ":\n" + ans
            if not inline:
                ans = "Изменения на " + ans
            return '```\n' + ans + '\n```'
        elif self.has_changes[class_ind]:
            for change_cell in self.changes:
                if change_cell.class_ind == class_ind:
                    ans = ''
                    for ch_d in change_cell.change_data:
                        ans += ch_d + '\n'
                    if inline:
                        return timetable.d_n[self.change_day] + ":\n" + ans
                    return "```\nИзменения на " + timetable.d_n[self.change_day] + " для " + \
                           timetable.c_n[class_ind] + ":\n" + ans + '\n```'
            common.pool_to_send.append(str(class_ind) + " - класс Шредингера в плане изменений")
            return "так_блэт.пнг\nЭтого не должно призойти!\nШредингер будет доволен"
        else:
            return "Нету изменений для " + timetable.c_n[class_ind]
