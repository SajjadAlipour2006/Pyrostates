from pyrogram import Client, filters
from pyrostates import StateMachine, StateGroup, State

app = Client("my_account")


class States(StateGroup):
    NAME = State()
    AGE = State()


state_machine = StateMachine("user_states.db", States)


@app.on_message(state_machine.at(None) & filters.private & filters.text)
async def home_state(_, message):
    await message.reply("Hello, I'm the conversation bot. What is your name?")
    state_machine[message] = States.NAME


@app.on_message(state_machine.at(States.NAME) & filters.private & filters.text)
async def name_state(_, message):
    name = message.text
    await message.reply(f"Nice to meet you, {name}! How old are you?")
    state_machine[message] = States.AGE


@app.on_message(state_machine.at(States.AGE) & filters.private & filters.text)
async def age_state(_, message):
    age = message.text
    await message.reply(f"You are {age} years old, good for you! Have a nice day!")
    del state_machine[message]


app.run()
