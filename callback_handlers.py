from properties import bot, active_sessions, crossIcon, circleIcon, Turn, \
    users, logic_markup, position, InlineKeyboardMarkup, InlineKeyboardButton, replay
from dataclasses import dataclass
from random import shuffle
from copy import deepcopy
from typing import List

import typing

if typing.TYPE_CHECKING:
    from telebot.types import CallbackQuery

@dataclass
class Player:
    keyboard: InlineKeyboardMarkup
    logic_keyboard: List[str]
    turn: Turn
    icon: str
    enemy: str
    message_id: str

@dataclass
class Replay:
    user: str
    message_id: str

def is_win(markup):
    if ((markup[0] == markup[3] == markup[6] or (markup[0] == markup[1] == markup[2])) and markup[0] != ' '):
        return 'win'
    elif ((markup[1] == markup[4] == markup[7] or (markup[3] == markup[4] == markup[5])) and markup[4] != ' '):
        return 'win'
    elif ((markup[2] == markup[5] == markup[8] or (markup[6] == markup[7] == markup[8])) and markup[8] != ' '):
        return 'win'
    elif (markup[0] == markup[4] == markup[8] or markup[6] == markup[4] == markup[2]) and markup[4] != ' ':
        return 'win'

    if any(map(lambda x: x == ' ', markup)):
        return 'continue'
    return 'draw'


def makeKeyboard():
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(text=f' ', callback_data=f'0'),
               InlineKeyboardButton(text=f' ', callback_data=f'1'),
               InlineKeyboardButton(text=f' ', callback_data=f'2'))
    markup.add(InlineKeyboardButton(text=f' ', callback_data=f'3'),
               InlineKeyboardButton(text=f' ', callback_data=f'4'),
               InlineKeyboardButton(text=f' ', callback_data=f'5'))
    markup.add(InlineKeyboardButton(text=f' ', callback_data=f'6'),
               InlineKeyboardButton(text=f' ', callback_data=f'7'),
               InlineKeyboardButton(text=f' ', callback_data=f'8'))
    return markup


@bot.callback_query_handler(func=lambda call: call.data in [str(i) for i in range(9)])
def command_click_inline(call: "CallbackQuery"):
    user = call.message.chat.username
    if user not in active_sessions:
        bot.send_message(
            call.message.chat.id, text='No active session is found, please use /playwith to start new game.')
        return
    enemy = active_sessions[user].enemy
    if active_sessions[user].turn == Turn.not_your:
        return
    if active_sessions[user].logic_keyboard[int(call.data)] != ' ':
        bot.edit_message_text(
            'Current position is occupied!', call.message.chat.id, call.message.id, reply_markup=active_sessions[user].keyboard)
        return

    figure = active_sessions[user].icon

    active_sessions[user].keyboard.keyboard[position[call.data][0]
                                      ][position[call.data][1]].text = figure
    active_sessions[user].logic_keyboard[int(call.data)] = user
    active_sessions[user].turn = Turn.not_your
    active_sessions[enemy].turn = Turn.your

    cond = is_win(active_sessions[user].logic_keyboard)
    if cond != 'continue':
        replay[user] = Replay(enemy, call.message.message_id)
        replay[enemy] = Replay(user, active_sessions[enemy].message_id)
        text = 'You won! Repeat?' if cond == 'win' else "Draw :( Repeat?"
        enemy_text = f'@{user} won... Repeat?' if cond == 'win' else 'Draw :( Repeat?'
        for i in range(3):
            for j in range(3):
                active_sessions[user].keyboard.keyboard[i][j].callback_data = 'end'
        user_keyboard = deepcopy(active_sessions[user].keyboard).add(\
            InlineKeyboardButton(text=f'Yes', callback_data=f'replay yes {enemy}'),\
            InlineKeyboardButton(text=f'No', callback_data=f'replay no {enemy}'))
        enemy_keyboard = deepcopy(active_sessions[user].keyboard).add(\
            InlineKeyboardButton(text=f'Yes', callback_data=f'replay yes {user}'),\
            InlineKeyboardButton(text=f'No', callback_data=f'replay no {user}'))
        bot.edit_message_text(
            text, call.message.chat.id, call.message.id, reply_markup=user_keyboard)
        bot.edit_message_text(
            enemy_text, users[enemy],\
            active_sessions[enemy].message_id, reply_markup=enemy_keyboard)
        active_sessions.pop(enemy, None)
        active_sessions.pop(user, None)
        return

    bot.edit_message_text('Your opponent turn',
                          call.message.chat.id, call.message.id, reply_markup=active_sessions[user].keyboard)

    bot.edit_message_text(
        "Your turn", users[enemy],\
        active_sessions[enemy].message_id, reply_markup=active_sessions[user].keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('apply'))
def apply_game(call: "CallbackQuery"):
    enemy = call.data.split()[2].lstrip('@')
    reply_ans = call.data.split()[1]
    if reply_ans == 'no':
        bot.send_message(
            users[enemy], text=f'@{call.message.chat.username} refused to play with you.')
        return
    user = call.message.chat.username
    if enemy in active_sessions:
        bot.send_message(
            call.message.chat.id, text=f'Player @{enemy} is playing at the moment.')
        return
    keyboard = makeKeyboard()
    logic_keyboard = logic_markup.copy()
    message = bot.send_message(users[enemy], "Waiting your opponent")
    active_sessions[enemy] = Player(keyboard, logic_keyboard, Turn.your, crossIcon, user, message.id)
    active_sessions[user] = Player(keyboard, logic_keyboard, Turn.not_your, circleIcon, enemy, call.message.id)
    players = [(active_sessions[user], user), (active_sessions[enemy], enemy)]
    shuffle(players)
    user_obj, enemy_obj = players
    active_sessions[user_obj[1]].turn = Turn.not_your
    active_sessions[enemy_obj[1]].turn = Turn.your
    bot.edit_message_text('Your turn', users[enemy_obj[1]], enemy_obj[0].message_id,
                     reply_markup=active_sessions[enemy_obj[1]].keyboard)
    bot.edit_message_text('Your opponent turn',
                          users[user_obj[1]], user_obj[0].message_id, reply_markup=active_sessions[user_obj[1]].keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("replay"))
def replay_match(call: "CallbackQuery"):
    player = call.from_user.username
    if not player in replay:
        return
    _, answer, enemy = call.data.split()
    if answer == "no":
        bot.edit_message_text(f'@{player} refused to play with you.', users[enemy], replay[enemy].message_id)
        bot.edit_message_text(f"You declined to replay a match", users[player], replay[player].message_id)
        replay.pop(player, None)
        replay.pop(enemy, None)
        return
    bot.edit_message_text("Waiting for opponent", call.message.chat.id, call.message.message_id)
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Yes', callback_data=f'apply yes {player}'),
                                              InlineKeyboardButton(text='No', callback_data=f'apply no {player}'))
    bot.edit_message_text("Your opponent waiting to play again! Do you?", users[enemy],\
                        replay[enemy].message_id, reply_markup=markup)
    replay.pop(player, None)
    replay.pop(enemy, None)