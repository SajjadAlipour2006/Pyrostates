from pyrogram.filters import Filter


class AtState(Filter):

    def __init__(self, state, state_machine=None):
        super().__init__()
        self.state = state
        self.state_machine = state_machine

    async def __call__(self, client, event) -> bool:
        user = event.from_user
        if self.state_machine is None:
            return user.get_state() == self.state
        else:
            return self.state_machine[user.id] == self.state
