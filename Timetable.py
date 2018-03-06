from Type import Type
import TClasses


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
            self.trap = -1  # it's a trap!

    def set_tt_base(self, class_count):
        self.all = [TClasses.TTDay(class_count) for _ in range(6)]

    def __dict__(self):
        return {'all': [d.__dict__() for d in self.all],
                'changes': self.changes.__dict__(),
                'changes_raw': self.changes_raw,
                'free_rooms': self.free_rooms.__dict__(),
                't_n': self.t_n,
                'c_n': self.c_n,
                'd_n': self.d_n,
                'r_n': self.r_n,
                'r_i': self.r_i,
                'trap': self.trap
                }

    @staticmethod
    def bin_search_crutch(arr, dest, is_name=True, start=0, end=-1):  # Знаю, костыль, но всё же
        if end == -1:
            end = len(arr)
        while end - start > 0:
            center = (end + start) // 2
            t_e = arr[center]
            if is_name:
                t_e = t_e.name
            else:
                t_e = t_e.ind
            if t_e < dest:
                start = center + 1
            elif t_e > dest:
                end = center
            else:
                return center
        for i in range(len(arr)):
            if is_name:
                if arr[i].name == dest:
                    return i
            elif arr[i].ind == dest:
                    return i
        return -1

    @staticmethod
    def bin_search_crutch_second(arr, dest, start=0, end=-1):  # Знаю, костыль, но всё же
        if end == -1:
            end = len(arr)
        while end - start > 0:
            center = (end + start) // 2
            t_e = arr[center]
            if t_e < dest:
                start = center + 1
            elif t_e > dest:
                end = center
            else:
                return center
        for i in range(len(arr)):
            if arr[i] == dest:
                return i
        return -1

    def restore(self, original):
        self.all = [TClasses.TTDay().restore(origin) for origin in original['all']]
        self.changes = TClasses.Changes().restore(original['changes'])
        self.changes_raw = original['changes_raw']
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
        '''def replace(arr, type_a):
            if type_a == Type.CLASS:
                return [self.c_n[i] for i in arr]
            if type_a == Type.TEACHER:
                return [self.t_n[i] for i in arr]
            if type_a == Type.ROOM:
                return [self.r_n[i] for i in arr]

        def replace_scp(arr):
            return ['█' * len(a) for a in arr]'''
        def group_to_str(tt_cell):
            if tt_cell.room_ind != self.trap:
                return (self.c_n[tt_cell.class_ind] + ' ' if tt_type != Type.CLASS else "") + \
                       ('(' + str(tt_cell.group_ind) + ') ' if tt_cell.group_ind != 0 else "") + tt_cell.subject + \
                       (' - ' + str(self.t_n[tt_cell.teacher_ind]) if tt_type != Type.TEACHER else "") + \
                       (' в ' + self.get_room(tt_cell.room_ind) if tt_type != Type.ROOM else "")
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
            answer += '\n'.join(group_to_str(les) for les in lessons)
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

    def get_timetable(self, ind, tt_type, day=7):
        def get_timetable_title():
            # type 0 - class, 1 - room, 2 - teacher; day: 7 if for all week
            ans = "Расписание для "
            if tt_type == Type.CLASS:
                ans += self.c_n[ind]
            elif tt_type == Type.ROOM:
                if ind == self.trap:
                    ans += '███'
                else:
                    ans += self.get_room_long(ind)
            elif tt_type == Type.TEACHER:
                ans += self.t_n[ind]
            else:
                ans += "чего-то"
            ans += " на "
            if day == 7:
                ans += "всю неделю"
            else:
                ans += self.d_n[day]
            return ans + '\n\n'

        def get_timetable_main(day_ind):
            if day_ind == 7:
                return '\n'.join(get_timetable_main(d) for d in range(6))
            ans = self.d_n[day_ind]
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
        title = get_timetable_title()
        tt = get_timetable_main(day)
        if tt == '':
            text = title + 'Нету расписания\n'
        else:
            text = title + tt
        if type == Type.CLASS:
            if self.changes.has_changes[ind]:
                text += 'Есть изменения\n' + self.changes.get_changes(self, ind, True)
        elif len(self.changes.changes) != 0:
            text += "Есть изменения."
        return text
