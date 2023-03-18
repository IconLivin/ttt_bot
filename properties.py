import telebot
import json
from enum import Enum, auto
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

API_KEY = "2137585543:AAHOzUVRhovLsZPbCMxo7r2g9E9HvCTNU3M"
bot = telebot.TeleBot(token=API_KEY)

crossIcon = u"\u274C"
circleIcon = u'\u2B55'

active_sessions = {}

users = json.load(open('database.json', 'r'))
replay = {}

logic_markup = [' ' for _ in range(9)]
position = {'0': [0, 0], '1': [0, 1], '2': [0, 2], '3': [1, 0], '4': [
    1, 1], '5': [1, 2], '6': [2, 0], '7': [2, 1], '8': [2, 2]}


class Turn(Enum):
    your = auto()
    not_your = auto()
