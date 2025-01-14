from typing import Union

from pyrogram.filters import Filter

from .state_machine import StateMachine, UserTypes
from .state import State

global_state_machine = StateMachine()


def get_state(user: UserTypes, state_machine: StateMachine = global_state_machine):
    return state_machine[user]


def set_state(user: UserTypes, state: Union[State, str], state_machine: StateMachine = global_state_machine):
    state_machine[user] = state


def del_state(user: UserTypes, state_machine: StateMachine = global_state_machine):
    del state_machine[user]


def del_state_if_exists(user: UserTypes, state_machine: StateMachine = global_state_machine):
    state_machine.delete_user_state(user)


class AtState(Filter):
    def __init__(self, state: Union[State, str, None], state_machine: StateMachine = global_state_machine):
        super().__init__()
        self.state = state
        self.state_machine = state_machine

    async def __call__(self, client, update) -> bool:
        at_state = self.state_machine.at(self.state)
        return at_state(client, update)
