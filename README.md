## Pyrostates

> A state handling extension for [Pyrogram](https://github.com/pyrogram/pyrogram)

``` python
from pyrogram import Client, filters
from pyrostates import at_state, set_state, del_state

app = Client("my_account")


@app.on_message(at_state(None) & filters.private & filters.text)
async def home_state(client, message):
    await message.reply("Hello, I'm the conversation bot\nWhat is your name?")
    set_state(message, "NAME")


@app.on_message(at_state("NAME") & filters.private & filters.text)
async def name_state(client, message):
    name = message.text
    await message.reply(f"Nice to meet you, {name}!\nHow old are you?")
    set_state(message, "AGE")


@app.on_message(at_state("AGE") & filters.private & filters.text)
async def age_state(client, message):
    age = message.text
    await message.reply(f"You are {age} years old, good for you!\nHave a nice day!")
    del_state(message)


app.run()
```

**Pyrostates** is a ready, easy and elegant extension for the [Pyrogram](https://github.com/pyrogram/pyrogram)
framework. It enables you to handle the states of your users in the most simple, efficient and reliable way.

### Installing

``` bash
pip3 install pyrostates
```
