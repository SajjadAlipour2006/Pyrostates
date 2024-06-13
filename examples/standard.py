from pyrogram import Client, filters
from pyrostates import StateGroup, State, at_state, set_state, del_state

app = Client("my_account")


class States(StateGroup):
    NAME = State()
    AGE = State()


@app.on_message(at_state(None) & filters.private & filters.text)
async def home_state(_, message):
    await message.reply("Hello, I'm the conversation bot. What is your name?")
    set_state(message, States.NAME)


@app.on_message(at_state(States.NAME) & filters.private & filters.text)
async def name_state(_, message):
    name = message.text
    await message.reply(f"Nice to meet you, {name}! How old are you?")
    set_state(message, States.AGE)


@app.on_message(at_state(States.AGE) & filters.private & filters.text)
async def age_state(_, message):
    age = message.text
    await message.reply(f"You are {age} years old, good for you! Have a nice day!")
    del_state(message)


app.run()
