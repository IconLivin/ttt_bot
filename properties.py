import telebot
import json
from enum import Enum, auto
from telebot import types

API_KEY = '2137585543:AAE6Nb13TZ7nLIKbJm1k6-oPk4fn73XgB7Q'
bot = telebot.TeleBot(token=API_KEY)

crossIcon = u"\u274C"
circleIcon = u'\u2B55'

active_sessions = {}

users = json.load(open('database.json', 'r'))


logic_markup = [' ' for _ in range(9)]
position = {'0': [0, 0], '1': [0, 1], '2': [0, 2], '3': [1, 0], '4': [
    1, 1], '5': [1, 2], '6': [2, 0], '7': [2, 1], '8': [2, 2]}


class Turn(Enum):
    your = auto()
    not_your = auto()
