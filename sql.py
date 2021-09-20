import sqlite3


class SQLighter:

    def __init__(self, database='database.db'):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()


class SQLUser(SQLighter):

    def user_exists(self, chat_id):
        """Проверяем, есть ли юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `user` WHERE `chat_id` = ?', (chat_id,)).fetchall()
            return bool(len(result))

    def add_user(self, chat_id, name, date, ref_user=None):
        """Добавляем нового юзера"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `user` (`chat_id`, `name`, `date`, `ref_user`)"
                                       "VALUES(?,?,?,?)", (chat_id, name, date, ref_user))

    def get_name_user(self, chat_id):
        """Получаем имя юзера"""
        with self.connection:
            return self.cursor.execute("SELECT `name` FROM `user` WHERE `chat_id`=?", (chat_id,)).fetchall()[-1][-1]

    def get_ref_user(self, chat_id):
        """Получаем кто реферал у юзера"""
        with self.connection:
            return self.cursor.execute("SELECT `ref_user` FROM `user` WHERE `chat_id`=?", (chat_id,)).fetchall()[-1][-1]

    def get_balance(self, chat_id):
        """Получаем баланс"""
        with self.connection:
            return int(self.cursor.execute("SELECT `balance` FROM `user` WHERE `chat_id`=?",
                                           (chat_id,)).fetchall()[-1][-1])

    def get_referal(self, chat_id):
        """Получаем количество рефералов"""
        with self.connection:
            return self.cursor.execute("SELECT `referal` FROM `user` WHERE `chat_id`=?", (chat_id,)).fetchall()

    def get_bonus(self, chat_id):
        """проверяем получил ли бонус"""
        with self.connection:
            return self.cursor.execute("SELECT `bonus` FROM `user` WHERE `chat_id`=?", (chat_id,)).fetchall()[-1][-1]

    def referal_update(self, chat_id):
        """Добовляем реферала"""
        with self.connection:
            return self.cursor.execute("UPDATE `user` SET `referal` = `referal` + 1, `balance` = `balance`+ 500 "
                                       "WHERE `chat_id` = ?", (chat_id,))

    def get_all_user(self):
        """Получаем количество юзеров"""
        with self.connection:
            select = self.cursor.execute("SELECT `id` FROM `user`").fetchall()
            return len(select)

    def get_user_to_day(self, date):
        """Получаем количество юзеров за день"""
        with self.connection:
            select = self.cursor.execute("SELECT `id` FROM `user` WHERE `date`=?", (date,)).fetchall()
            return len(select)

    def get_referal_to_day(self, date, ref_user):
        """Получаем количество зарегистрированных рефералов"""
        with self.connection:
            select = self.cursor.execute("SELECT `id` FROM `user` WHERE `date`=? AND `ref_user`=?", (date, ref_user)).fetchall()
            return len(select)

    def upload_balance(self, chat_id, balance):
        """Списание баланса"""
        with self.connection:
            return self.cursor.execute("UPDATE `user` SET `balance` = ? WHERE `chat_id` = ?", (balance, chat_id,))

    def upload_bonus(self, chat_id):
        """Получил бонус"""
        with self.connection:
            return self.cursor.execute("UPDATE `user` SET `bonus` = 1 WHERE `chat_id` = ?", (chat_id,))
