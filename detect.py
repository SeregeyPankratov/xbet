import sqlite3


class SQLighter:

    def __init__(self, database='test.db'):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()


class SQLUser(SQLighter):

    def user_exists(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM `user` WHERE `referal` > 0').fetchall()

    def referal(self, chat_id):
        with self.connection:
            return self.cursor.execute('SELECT * FROM `user` WHERE `ref_user` = ?', (chat_id,)).fetchall()

    def cor(self, corect, chat_id):
        with self.connection:
            return self.cursor.execute("UPDATE `user` SET `corect` = ? WHERE `chat_id` = ?", (corect, chat_id,))

    def new(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM `user` WHERE `referal` != 0 AND `referal` > `corect`').fetchall()


# all = SQLUser().user_exists()
#
# for x in range(0, len(all)):
#     ref = len(SQLUser().referal(all[x][2]))
#     upda = SQLUser().cor(ref, (all[x][2]))


no = SQLUser().new()

print(no)


