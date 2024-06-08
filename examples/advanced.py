from pyrogram import Client, filters
from pyrostates import StateMachine, StateGroup, State, set_state, del_state

app = Client("my_account")

state_machine = StateMachine("user_states.db")


class States(StateGroup):
    NAME = State()
    AGE = State()


@app.on_message(state_machine.at(None) & filters.private & filters.text)
async def home_state(_, message):
    await message.reply("Hello, I'm the conversation bot\nWhat is your name?")
    set_state(message, "NAME")


@app.on_message(state_machine.at(States.NAME) & filters.private & filters.text)
async def name_state(_, message):
    name = message.text
    await message.reply(f"Nice to meet you, {name}!\nHow old are you?")
    set_state(message, "AGE")


@app.on_message(state_machine.at(States.AGE) & filters.private & filters.text)
async def age_state(_, message):
    age = message.text
    await message.reply(f"You are {age} years old, good for you!\nHave a nice day!")
    del_state(message)


app.run()
