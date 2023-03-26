import telebot
import json
from enum import Enum, auto
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Union

import typing

if typing.TYPE_CHECKING:
    from telebot.types import Message
    from telebot.types import CallbackQuery


API_KEY = "2137585543:AAHOzUVRhovLsZPbCMxo7r2g9E9HvCTNU3M"
bot = telebot.TeleBot(token=API_KEY)

crossIcon = u"\u274C"
circleIcon = u'\u2B55'

active_sessions = {}

users: dict[str, int] = json.load(open('database.json', 'r'))
replay = {}

def check_in_base(func):
    def wrapper(call: Union["Message", "CallbackQuery"]):
        owner = call.from_user.username
        if owner in users:
            return func(call)
        owner_chat_id = call.from_user.id
        users_to_delete = []
        print(users)
        for user, chat_id in users.items():
            if owner_chat_id == chat_id:
                users_to_delete.append(user)
        for user in users_to_delete:
            del users[user]
        users[owner] = owner_chat_id
        with open("database.json", "w") as OUT:
            json.dump(users, OUT, indent=4)
        return func(call)
    return wrapper

logic_markup = [' ' for _ in range(9)]
position = {'0': [0, 0], '1': [0, 1], '2': [0, 2], '3': [1, 0], '4': [
    1, 1], '5': [1, 2], '6': [2, 0], '7': [2, 1], '8': [2, 2]}


class Turn(Enum):
    your = auto()
    not_your = auto()
