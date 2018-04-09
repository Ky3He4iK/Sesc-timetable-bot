from Type import *
import TClasses
import common


class Timetable:
    def __init__(self, temp=False):
        self.all = []  # array of TTD
        self.changes = None
        self.changes_raw = None
        self.free_rooms = TClasses.FreeRoomsAll()
        if temp:
            self.classes = []
            self.days = []
            self.rooms = []
            self.teachers = []
        else:
            self.t_n = []
            self.c_n = []
            self.d_n = []
            self.r_n = []
            self.r_i = []
            self.trap = -1  # it's a trap!.gif

    def set_tt_base(self, class_count):
        self.all = [TClasses.TTDay(class_count) for _ in range(6)]

    def __dict__(self):
        return {
            'all': [d.__dict__() for d in self.all],
            'changes': self.changes.__dict__(),
            'free_rooms': self.free_rooms.__dict__(),
            't_n': self.t_n,
            'c_n': self.c_n,
            'd_n': self.d_n,
            'r_n': self.r_n,
            'r_i': self.r_i,
            'trap': self.trap
        }

    @staticmethod
    def bin_search_crutch(arr, destination, is_name=True, start=0, end=-1):  # Знаю, костыль, но всё же
        end = len(arr) if end == -1 else end
        while end - start > 0:
            center = (end + start) // 2
            t_e = arr[center].name if is_name else arr[center].ind
            if t_e < destination:
                start = center + 1
            elif t_e > destination:
                end = center
            else:
                return center
        for i in range(len(arr)):
            if (is_name and arr[i].name == destination) or arr[i].ind == destination:
                return i
        return -1

    @staticmethod
    def bin_search_crutch_second(arr, destination, start=0, end=-1):  # Знаю, ещё больший костыль, но всё же
        if end == -1:
            end = len(arr)
        while end - start > 0:
            center = (end + start) // 2
            t_e = arr[center]
            if t_e < destination:
                start = center + 1
            elif t_e > destination:
                end = center
            else:
                return center
        for i in range(len(arr)):
            if arr[i] == destination:
                return i
        return -1

    def restore(self, original):
        self.all = [TClasses.TTDay().restore(origin) for origin in original['all']]
        self.changes = TClasses.Changes().restore(original['changes'])
        self.free_rooms = TClasses.FreeRoomsAll().restore(original['free_rooms'])
        self.t_n = original['t_n']
        self.c_n = original['c_n']
        self.d_n = original['d_n']
        self.r_n = original['r_n']
        self.r_i = original['r_i']
        self.trap = original['trap']
        return self

    def get_room(self, room_ind):
        if self.r_i[room_ind] == 'F':
            return 'спортзале'
        if self.r_i[room_ind] == 'S':
            return 'каб. ин.яз.'
        if self.r_i[room_ind] == 'Hz':
            return '███'
        return self.r_i[room_ind]

    def get_room_long(self, room_ind):
        if self.r_i[room_ind] == 'F':
            return 'Cпортзал'
        if self.r_i[room_ind] == 'S':
            return 'Kаб. ин.яз.'
        if self.r_i[room_ind] == 'Hz':
            return '███'
        return self.r_i[room_ind]

    def get_timetable_les(self, tt_type, day_ind, lesson, ind):
        """
        :param tt_type:
        :param day_ind:
        :param lesson:
        :param ind:
        :return:
        """
        def group_to_str(tt_cell):
            if tt_cell.room_ind != self.trap:
                class_s = (self.c_n[tt_cell.class_ind] + ' ' if tt_type != Type.CLASS else "")
                group_s = ('(' + str(tt_cell.group_ind) + ') ' if tt_cell.group_ind != 0 else "")
                sub = '|'.join(tt_cell.subject)
                teacher = (' - ' + str(self.t_n[tt_cell.teacher_ind]) if tt_type != Type.TEACHER else "")
                room = (' в ' + self.get_room(tt_cell.room_ind) if tt_type != Type.ROOM else "")
                return class_s + group_s + sub + teacher + room
            else:
                return 'ACCESS DENIED'

        answer = str(lesson + 1) + ': '
        lessons = [TClasses.TTDay.TTLesson.TTLClass.TTCell() for _ in range(0)]
        if tt_type == Type.CLASS:
            lessons = self.all[day_ind].day[lesson].lesson[ind].group
        else:
            for cl in self.all[day_ind].day[lesson].lesson:
                for group in cl.group:
                    if (tt_type == Type.TEACHER and group.teacher_ind == ind) or \
                            (tt_type == Type.ROOM and group.room_ind == ind):
                        lessons.append(group)
        if len(lessons) == 0:
            answer += '\0--------------------\n'
        else:
            lessons.sort()
            answer += '\n   '.join(group_to_str(les) for les in lessons) + '\n'
            '''if tt_type != Type.CLASS:
                cl, g_i, s_i, t_i, r_i = [], [], [], [], []
                for group in lessons:
                    if group.class_ind not in cl:
                        cl.append(group.class_ind)
                        g_i.append(group.group_ind)
                    if group.subject not in s_i:
                        s_i.append(group.subject)
                    if group.teacher_ind not in t_i:
                        t_i.append(group.teacher_ind)
                    if group.room_ind not in r_i:
                        r_i.append(group.room_ind)
                has_trap = self.trap in r_i
                cl = replace(cl, Type.CLASS)
                t_i = replace(cl, Type.TEACHER)
                r_i = replace(cl, Type.ROOM)
                if has_trap:
                    cl = replace_scp(cl)
                    g_i = [0 for _ in g_i]
                    s_i = replace_scp(s_i)
                    t_i = replace_scp(t_i)
                    r_i = replace_scp(r_i)
                answer += '|'.join(str((self.c_n[int(cl[i])]) if type(cl[i]) is int else cl[i]) +
                                   ('(' + str(g_i[i]) + ')' if g_i[i] != 0 else '') for i in
                                   range(len(cl))) + ' - ' + '|'.join(s for s in s_i)
                # Какая-то чёрная магия генераторов. НЕ ТРОГАТЬ! (я сам не знаю как это работает)
                # (так то знаю, но это не точно)
                if tt_type != Type.TEACHER:
                    answer += ' - ' + '|'.join(self.t_n[i] for i in t_i)
                if tt_type != Type.ROOM:
                    answer += ' в ' + '|'.join(self.get_room(i) for i in r_i)
                answer += '\n'
            else:
                for group in lessons:
                    if group.group_ind != 0:
                        answer += '(' + str(group.group_ind) + ') - '
                    answer += ', '.join(group.subject if group.subject is not None else 'null') + ' - ' + \
                              self.t_n[group.teacher_ind] + ' в '
                    if group.room_ind != self.trap:
                        answer += self.get_room(group.room_ind) + '\n'
                    else:
                        answer += '███' + '\n'''
        return answer

    def get_timetable_today(self, ind, tt_type):
        return self.get_timetable(ind, tt_type, common.c_day % 6)

    def get_timetable_tomorrow(self, ind, tt_type):
        return self.get_timetable(ind, tt_type, ((common.c_day + 1) % 6) if common.c_day != 6 else 0)

    def get_timetable_near(self, ind, tt_type):
        if common.c_day > 5:
            c_d, c_l = 0, 0
        elif common.c_les > 6:
            c_d, c_l = (common.c_day + 1) % 6, 0
        else:
            c_d, c_l = common.c_day, common.c_les
        title = (self.c_n[ind] if tt_type == Type.CLASS else "") + \
                (self.get_room_long(ind) if tt_type == Type.ROOM else "") + \
                (self.t_n[ind] if tt_type == Type.TEACHER else "") + '. ' + self.d_n[c_d] + '\n'
        return '```\n' + title + self.get_timetable_les(tt_type, c_d % 6, c_l, ind) + '\n```'

    def get_timetable(self, ind, tt_type, day=7):
        def get_timetable_title():
            ans = "Расписание для "
            if tt_type == Type.CLASS:
                ans += self.c_n[ind]
            elif tt_type == Type.ROOM:
                ans += '███' if ind == self.trap else self.get_room_long(ind)
            elif tt_type == Type.TEACHER:
                ans += self.t_n[ind]
            else:
                ans += "чего-то"
            ans += " на " + ("всю неделю" if day == 7 else self.d_n[day])
            return ans + '\n\n'

        def get_timetable_main(day_ind):
            if day_ind == 7:
                return '\n'.join(get_timetable_main(d) for d in range(6))
            ans = self.d_n[day_ind] + '\n'
            h_l = False
            tt_a = []
            last_les = -1
            for les in range(7):
                tt_s = self.get_timetable_les(tt_type, day_ind, les, ind)
                if '\0' not in tt_s:
                    h_l = True
                    last_les = les
                tt_a.append(tt_s)
            if h_l:
                return ans + ''.join(tt_a[:last_les + 1]) + '\n'
            return ''

        if ind == -1:
            return "Что-то пошло не так\n"
        if tt_type == Type.ROOM and ind == self.trap:
            return "`ACCESS DENIED`"
        tt = get_timetable_main(day)
        text = get_timetable_title() + ('Нету расписания\n' if tt == '' else tt)
        if tt_type == Type.CLASS and self.changes.has_changes[ind]:
                text += 'Есть изменения\n' + self.changes.get_changes(self, ind, True)
        elif len(self.changes.changes) != 0:
            text += "Есть изменения."
        return '```\n' + text + '\n```'

    def get_timetable_pres(self, presentation, tt_type=Type.CLASS, ind=-1, day=7):
        if presentation == Presentation.TODAY:
            return self.get_timetable_today(ind, tt_type)
        if presentation == Presentation.TOMORROW:
            return self.get_timetable_tomorrow(ind, tt_type)
        if presentation == Presentation.NEAR:
            return self.get_timetable_near(ind, tt_type)
        if presentation == Presentation.ALL_WEEK:
            return self.get_timetable(ind, tt_type)
        return self.get_timetable(ind, tt_type, day)

    def check_has(self, tt_type, ind):
        if tt_type == Type.CLASS:
            return 0 < ind < len(self.c_n)
        if tt_type == Type.TEACHER:
            return 0 < ind < len(self.t_n)
        if tt_type == Type.ROOM:
            return 0 < ind < len(self.r_i)
        return False
