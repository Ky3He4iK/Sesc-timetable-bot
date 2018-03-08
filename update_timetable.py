from Timetable import Timetable
import TClasses
import IO
import config
import logging


def t_update(timetable, full=True):
    try:
        tt_t = Timetable(True)

        def get_token():
            m_token = IO.InternetIO.get("http://lyceum.urfu.ru/n/?p=tmtbl")
            if m_token is None:
                raise Exception("No internet connection")
            m_token = m_token[m_token.find("<script>var tmToken=\"") + len("<script>var tmToken=\""):]
            return m_token[:m_token.find("\"</script>")]

        token = get_token()

        def set_base():
            def extract_by_str(string, tt_class):
                ans = []
                a = string.split("</option>")[:-1]
                for ss in a:
                    d_i = ss[ss.find("value='") + len("value='"):]
                    ans.append(tt_class(d_i[: d_i.find("'")], ss[ss.rfind(">") + 1:]))
                ans.sort()
                return ans

            page = IO.InternetIO.get("http://lyceum.urfu.ru/n/?p=tmtbl")
            if page is None:
                raise Exception("No internet connection")
            page = page[page.find("<div class=\"tmtbl\""): page.find("<script>var tmToken=")]
            arr = page.split("tmtbl")
            tt_t.classes = extract_by_str(arr[3], TClasses.Class)
            tt_t.teachers = extract_by_str(arr[4], TClasses.Teacher)
            tt_t.rooms = extract_by_str(arr[5], TClasses.Room)
            tt_t.rooms.append(TClasses.Room('F', "Каф. ин. яз"))
            tt_t.rooms.append(TClasses.Room('Hz', 'ACCESS DENIED'))
            tt_t.rooms.sort()
            tt_t.days = extract_by_str(arr[6], TClasses.Day)

            tt_t.set_tt_base(len(tt_t.classes))

        set_base()
        defaults = [Timetable.bin_search_crutch(tt_t.rooms, 'S', False),
                    Timetable.bin_search_crutch(tt_t.rooms, 'F', False),
                    Timetable.bin_search_crutch(tt_t.rooms, 'Hz', False),
                    Timetable.bin_search_crutch(tt_t.teachers, "Сотрудник И. С.")]

        def set_class(class_ind, day_ind):
            def set_class_lesson(class_ind_int, d_ind, les_data):
                def set_class_lesson_sub(lesson_data, group, cl_ind):
                    if ' ' not in lesson_data:
                        if lesson_data == "Физкультура":
                            room = defaults[0]
                        else:
                            room = defaults[1]
                        subject = lesson_data
                    else:
                        arr = lesson_data.split(" ")
                        if len(arr) > 2:
                            print(arr)
                        room = Timetable.bin_search_crutch(tt_t.rooms, arr[1], False)
                        if room == -1:
                            room = defaults[2]
                        subject = arr[0]
                    return TClasses.TTDay.TTLesson.TTLClass.TTCell(cl_ind, room, defaults[3], subject, group)

                # les_data = ' '
                if les_data.rfind("<td>") == -1:
                    return
                les_num = int(les_data[len("<td>"):len("<td>") + 1]) - 1
                if les_data.find("width") == -1:
                    begin = les_data.index("<td colspan=2>") + len("<td colspan=2>")
                    les_d = les_data[begin: les_data.index("</td></tr>")]
                    temp = set_class_lesson_sub(les_d, 0, class_ind_int)
                    tt_t.all[d_ind].day[les_num].lesson[class_ind_int].group.append(temp)
                else:
                    aaa = les_data.split("<td width=47%>")[1:]
                    for i in range(len(aaa)):
                        l_data = aaa[i][:aaa[i].index("</td>")]
                        if "&times" not in l_data:
                            temp = set_class_lesson_sub(l_data, i + 1, class_ind_int)
                            tt_t.all[d_ind].day[les_num].lesson[class_ind_int].group.append(temp)

            url1 = config.base_url + token + "&tmrType=0&tmrClass=" + tt_t.classes[class_ind].ind
            url = url1 + "&tmrTeach=0&tmrRoom=0&tmrDay=" + str(day_ind + 1)
            ans = IO.InternetIO.get(url)
            if ans is None:
                raise Exception("No internet connection")
            if ans == "Err\n":
                raise Exception("update failed", class_ind, day_ind, ans)
            ans_sub = ans[ans.index("<tr>") + len("<tr>"):].split("<tr>")
            for les in ans_sub:
                set_class_lesson(class_ind, day_ind, les)

        def set_teacher(teacher_ind):
            def set_teacher_day(day_info, teach_ind):
                def set_teacher_day_sub(l_data, t_ind, d_ind):
                    c = l_data[l_data.rfind("</td>") - 1]
                    if c == ';':
                        return
                    elif c == '1':
                        group = 1
                    elif c == '2':
                        group = 2
                    else:
                        group = 0
                    l_data = l_data[:l_data.rfind("<td>") - len("</td>")]
                    if '<td>' not in l_data:
                        return
                    les_num = int(l_data[len("<td>"): len("<td>") + 1]) - 1
                    l_data = l_data[l_data.find("</td>") + len("</td><td>"):]
                    m_arr = l_data.split("</td><td>")
                    subject = m_arr[0]
                    for cl_ in range(len(tt_t.classes)):
                        if m_arr[1] == tt_t.classes[cl_].name:
                            class_ind = cl_
                            break
                    else:
                        class_ind = -1  # TODO: add binary search
                    if group == 2 and len(tt_t.all[d_ind].day[les_num].lesson[class_ind].group) != 1:
                        group_i = 1
                    else:
                        group_i = 0
                    if d_ind < 0 or les_num < 0 or group_i < 0 or d_ind >= len(tt_t.all) or les_num >= len(
                            tt_t.all[d_ind].day) or class_ind >= len(
                            tt_t.all[d_ind].day[les_num].lesson) or group_i >= len(
                            tt_t.all[d_ind].day[les_num].lesson[class_ind].group):
                        # От создателя if'а с 64 условиями в 1 строке
                        print("Хьюстон, у нас проблемы", d_ind, les_num, group_i, t_ind)
                    t_cell = tt_t.all[d_ind].day[les_num].lesson[class_ind].group[group_i]
                    t_cell.teacher_ind = t_ind
                    if subject not in t_cell.subject:
                        t_cell.subject.append(subject)
                    tt_t.all[d_ind].day[les_num].lesson[class_ind].group[group_i] = t_cell

                arr = day_info.split("<tr>")
                day_ind = timetable.bin_search_crutch(tt_t.days, arr[0][:arr[0].find("</h3>")], True)
                for arr_sub in arr[1:]:
                    set_teacher_day_sub(arr_sub, teach_ind, day_ind)

            url = config.base_url + token + "&tmrType=1&tmrClass=&tmrTeach=" + tt_t.teachers[teacher_ind].ind
            ans = IO.InternetIO.get(url + "&tmrRoom=0&tmrDay=0")
            if ans is None:
                raise Exception("No internet connection")
            if ans == "Err\n":
                raise Exception("Fail while updating teachers\n", teacher_ind, ans)
            if "Уроков не найдено" in ans:
                return
            ans = ans[ans.index("<h3>") + len("<h3>"): ans.index("<details><summary>")]
            for sub_s in ans.split("<h3>"):
                set_teacher_day(sub_s, teacher_ind)

        def get_changes_raw():
            url = config.base_url + token + "&tmrType=1&tmrClass=&tmrTeach=" + tt_t.teachers[0].ind
            ans = IO.InternetIO.get(url + "&tmrRoom=0&tmrDay=0")
            if ans is None:
                raise Exception("No internet connection")
            if ans == "Err\n":
                raise Exception("Fail while updating teachers\n", 0, ans)
            return ans[ans.find("</summary>") + len("</summary>"):]

        def set_changes():
            def get_day_specialized(day):
                if len(day) == 0:
                    return -1
                day = day[0].upper() + day[1:-1].lower()
                for i in range(len(config.day_names)):
                    if config.day_names[i][:-1] == day:
                        return i
                return 7

            def set_changes_sub(lesson_ch, cl_ind):
                if cl_ind == -1:
                    return
                tt_t.changes.has_changes[cl_ind] = True
                tmp = []
                for sub_ch in lesson_ch.split("<p>"):
                    if len(sub_ch) < 2:
                        continue
                    tmp.append(sub_ch[:sub_ch.find("</p>")])
                tt_t.changes.changes.append(TClasses.Changes.ChangesCell(cl_ind, tmp))

            changes_raw = get_changes_raw()
            tt_t.changes = TClasses.Changes(len(tt_t.classes))
            temp = changes_raw[changes_raw.find("НА ") + len("НА "):]
            tt_t.changes.change_day = get_day_specialized(temp[:temp.find(' ') - 1])
            ind = changes_raw.find("</h3>") + len("</h3>")
            changes_raw = changes_raw[ind:].replace("&nbsp;&mdash;", "-")
            arr = changes_raw.split("<h6>")
            for les_ch in arr:
                if len(les_ch) != 0:
                    if "</h6>" in les_ch:
                        class_ind = Timetable.bin_search_crutch(tt_t.classes, les_ch[:les_ch.index('</h6>')])
                        set_changes_sub(les_ch[les_ch.find("<p>"):], class_ind)
                    else:
                        print("Error occuped while setting changes:", les_ch)

        def gen_ch_ind():
            for class_ch_ind in range(len(tt_t.changes.changes)):
                tt_t.changes.ch_ind[tt_t.changes.changes[class_ch_ind].class_ind] = class_ch_ind

        if full:
            for cl in range(len(tt_t.classes)):
                for d in range(len(tt_t.days)):
                    set_class(cl, d)
            for t in range(len(tt_t.teachers)):
                set_teacher(t)
            tt_t.free_rooms.set(tt_t)
        set_changes()
        gen_ch_ind()
        timetable.changes = tt_t.changes
        if full:
            timetable.free_rooms = tt_t.free_rooms
            timetable.all = tt_t.all
            timetable.t_n = [t.name for t in tt_t.teachers]
            timetable.c_n = [c.name for c in tt_t.classes]
            timetable.d_n = [d.name for d in tt_t.days]
            timetable.r_n = [r.name for r in tt_t.rooms]
            timetable.r_i = [r.ind for r in tt_t.rooms]
            timetable.trap = timetable.r_i.index('Hz')
        return True
    except BaseException as e:
        print(str(e), e.args, e.__traceback__)
        logging.error(e, exc_info=True)
        return False
