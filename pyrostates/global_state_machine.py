from pyrogram.filters import Filter

from .state_machine import StateMachine

global_state_machine = StateMachine()


def get_state(user, state_machine=global_state_machine):
    return state_machine[user]


def set_state(user, state, state_machine=global_state_machine):
    state_machine[user] = state


def del_state(user, state_machine=global_state_machine):
    del state_machine[user]


def del_state_if_exists(user, state_machine=global_state_machine):
    state_machine.delete_user_state(user)


class AtState(Filter):
    def __init__(self, state, state_machine=global_state_machine):
        super().__init__()
        self.state = state
        self.state_machine = state_machine

    async def __call__(self, client, update) -> bool:
        at_state = self.state_machine.at(self.state)
        return at_state(client, update)
