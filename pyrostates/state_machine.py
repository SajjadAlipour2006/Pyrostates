from sqlite3 import connect
from typing import Union, Type

from pyrogram.filters import create
from pyrogram.types import Message, CallbackQuery, Chat, User

import pyrostates
from .state import State

UserTypes = Union[Message, CallbackQuery, Chat, User, str, int]


class StateMachine:
    @staticmethod
    def get_id(user: UserTypes) -> int:
        if isinstance(user, Message):
            if user.from_user:
                return user.from_user.id
            if user.sender_chat:
                return user.sender_chat.id
        if isinstance(user, CallbackQuery):
            return user.from_user.id
        if isinstance(user, (Chat, User)):
            return user.id
        if isinstance(user, str):
            return int(user)
        return user

    def create_table(self):
        sql = """CREATE TABLE IF NOT EXISTS user_states(user_id INTEGER PRIMARY KEY, user_state TEXT)"""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()

    def __init__(self, database: str = ":memory:", state_group: Type["pyrostates.StateGroup"] = None):
        self.connection = connect(database, check_same_thread=False)
        self.state_group = state_group
        self.create_table()

    def insert_user_state(self, user: UserTypes, state: Union[State, str]):
        sql = """INSERT INTO user_states VALUES (?, ?)"""
        user_id = self.get_id(user)
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id, state))
        self.connection.commit()

    def update_user_state(self, user: UserTypes, state: Union[State, str]):
        sql = """UPDATE user_states SET user_state = ? WHERE user_id = ?"""
        user_id = self.get_id(user)
        cursor = self.connection.cursor()
        cursor.execute(sql, (state, user_id))
        self.connection.commit()

    def __setitem__(self, user: UserTypes, state: Union[State, str]):
        if isinstance(state, State):
            state = str(state)
        if self[user] is None:
            self.insert_user_state(user, state)
        else:
            self.update_user_state(user, state)

    def select_user_state(self, user: UserTypes) -> Union[str, None]:
        sql = """SELECT user_state FROM user_states WHERE user_id = ?"""
        user_id = self.get_id(user)
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()

    def __getitem__(self, user: UserTypes) -> Union[State, str, None]:
        result = self.select_user_state(user)
        if result is None:
            return result
        elif self.state_group is not None and result[0] in self.state_group.get_state_dict():
            return getattr(self.state_group, result[0])
        else:
            return result[0]

    def delete_user_state(self, user: UserTypes):
        sql = """DELETE from user_states where user_id = ?"""
        user_id = self.get_id(user)
        cursor = self.connection.cursor()
        cursor.execute(sql, (user_id,))
        self.connection.commit()

    def __delitem__(self, user: UserTypes):
        if self[user] is None:
            raise KeyError("User does not exist")
        self.delete_user_state(user)

    def at(self, state: Union[State, str, None]):
        @create
        def at_state(_, __, update) -> bool:
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

    def get_all(self) -> dict:
        sql = """SELECT * FROM user_states"""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        return dict(cursor.fetchall())
