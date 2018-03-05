from Type import Type


class Legacy:
    def __init__(self, message, db=None):  # type 0 - class, 1 - room, 2 - teacher; day: 7 if for all week
        self.type = Type.CLASS
        self.type_id = 10
        self.day = 7
        text = message.text
        p = text.find(' ')
        if p == -1 or db is None:
            return
        text = text[min(p + 1, len(text)):]
        # if db is None:
        # u_id = -1
        # else:
        u_id = db.get_user_id(message.from_user.id)
        if u_id != -1:
            self.type = db.users[u_id].type_name
            self.type_id = db.users[u_id].type_id
        if len(text) == 0:
            return
        if text[0] == 'r':
            self.type = Type.ROOM
        elif text[0] == 't':
            self.type = Type.TEACHER
        elif text[0] == ' ':
            if len(text) == 1:
                return
            if text[1] == 'r':
                self.type = Type.ROOM
            elif text[1] == 't':
                self.type = Type.TEACHER
            elif text[1] == 'c':
                self.type = Type.CLASS
            else:
                aa = text.split(' ')
                if len(aa) > 0:
                    self.day = db.get_day_id(aa[0])
                    if self.day == -1:
                        self.day = 7
                    else:
                        text = text[:text.find(' ')]
                for i in range(3):
                    self.type_id = db.get_id(text, i)
                    if self.type_id != -1:
                        self.type = i
                        return
        text = text[min(2, len(text)):]
        s_t = text.split(' ')
        if len(s_t) == 0:
            return
        elif len(s_t) == 1:
            self.type_id = db.get_id(s_t, self.type)
        else:
            tmp = db.get_day_id(s_t[-1])
            if tmp == -1:
                self.day = 7
                text = ' '.join(s_t)
            else:
                self.day = tmp
                text = ' '.join(s_t[:-1])
            self.type_id = db.get_id(text, self.type)
