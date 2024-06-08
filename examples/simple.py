from pyrogram import Client, filters
from pyrostates import at_state, set_state, del_state

app = Client("my_account")


@app.on_message(at_state(None) & filters.private & filters.text)
async def home_state(_, message):
    await message.reply("Hello, I'm the conversation bot\nWhat is your name?")
    set_state(message, "NAME")


@app.on_message(at_state("NAME") & filters.private & filters.text)
async def name_state(_, message):
    name = message.text
    await message.reply(f"Nice to meet you, {name}!\nHow old are you?")
    set_state(message, "AGE")


@app.on_message(at_state("AGE") & filters.private & filters.text)
async def age_state(_, message):
    age = message.text
    await message.reply(f"You are {age} years old, good for you!\nHave a nice day!")
    del_state(message)


app.run()
