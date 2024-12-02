from sqlite3 import connect
from typing import Union

from pyrogram.filters import create
from pyrogram.types import Message, CallbackQuery, Chat, User

from .state import State


class StateMachine:
    @staticmethod
    def get_id(user_id):
        if isinstance(user_id, Message):
            if user_id.from_user:
                return user_id.from_user.id
            if user_id.sender_chat:
                return user_id.sender_chat.id
        if isinstance(user_id, CallbackQuery):
            return user_id.from_user.id
        if isinstance(user_id, (Chat, User)):
            return user_id.id
        if isinstance(user_id, str):
            return int(user_id)
        return user_id

    def create_table(self):
        sql = """CREATE TABLE IF NOT EXISTS user_states(user_id INTEGER PRIMARY KEY, user_state TEXT)"""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()

    def __init__(self, database: str = ":memory:", state_group=None):
        self.connection = connect(database, check_same_thread=False)
        self.state_group = state_group
        self.create_table()

    def insert_user_state(self, user_id: Union[int, str], state: Union[State, str]):
        sql = """INSERT INTO user_states VALUES (?, ?)"""
        user_id = self.get_id(user_id)
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id, state))
        self.connection.commit()

    def update_user_state(self, user_id: Union[int, str], state: Union[State, str]):
        sql = """UPDATE user_states SET user_state = ? WHERE user_id = ?"""
        user_id = self.get_id(user_id)
        cursor = self.connection.cursor()
        cursor.execute(sql, (state, user_id))
        self.connection.commit()

    def __setitem__(self, user_id: Union[int, str], state: Union[State, str]):
        if isinstance(state, State):
            state = str(state)
        if self[user_id] is None:
            self.insert_user_state(user_id, state)
        else:
            self.update_user_state(user_id, state)

    def select_user_state(self, user_id: Union[int, str]):
        sql = """SELECT user_state FROM user_states WHERE user_id = ?"""
        user_id = self.get_id(user_id)
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()

    def __getitem__(self, user_id: Union[int, str]):
        result = self.select_user_state(user_id)
        if result is None:
            return result
        elif self.state_group is not None and result[0] in self.state_group.get_state_dict():
            return getattr(self.state_group, result[0])
        else:
            return result[0]

    def delete_user_state(self, user_id: Union[int, str]):
        sql = """DELETE from user_states where user_id = ?"""
        user_id = self.get_id(user_id)
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id,))
        self.connection.commit()

    def __delitem__(self, user_id: Union[int, str]):
        if self[user_id] is None:
            raise KeyError("User does not exist")
        self.delete_user_state(user_id)

    def at(self, state: Union[State, str]):
        @create
        def at_state(_, __, update):
            if isinstance(update, Message):
                if not update.from_user and not update.sender_chat:
                    return False
            if hasattr(update, "state"):
                current_state = getattr(update, "state")
            else:
                current_state = self[update]
                setattr(update, "state", current_state)
            return current_state == state
        return at_state

    def change_database(self, database: str = ":memory:"):
        now_connection = connect(database, check_same_thread=False)
        self.connection.backup(now_connection)
        self.connection = now_connection

    def get_all(self):
        sql = """SELECT * FROM user_states"""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        return dict(cursor.fetchall())
