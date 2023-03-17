from properties import bot, active_sessions, users, InlineKeyboardButton, InlineKeyboardMarkup, json
import typing

if typing.TYPE_CHECKING:
    from telebot.types import Message

@bot.message_handler(commands=['abort'])
def abort_session(message: "Message"):
    user = message.from_user.username
    if message.from_user.username in active_sessions:
        bot.edit_message_text("Your opponent ran away!", users[active_sessions[user].enemy
                                                               ], active_sessions[active_sessions[user].enemy].message_id)
        bot.send_message(message.chat.id, "Pussy")
        active_sessions.pop(active_sessions[user].enemy)
        active_sessions.pop(user)


@bot.message_handler(commands=['playwith'])
def invite_player(message: "Message"):
    try:
        player = f'@{message.text.split()[1]}' if not message.text.split()[
            1].startswith('@') else message.text.split()[1]
    except IndexError:
        bot.send_message(
            message.chat.id, f'No player specified: {message.text}, to list available players type /players.')
        return
    if player[1:] not in users.keys():
        bot.send_message(
            message.chat.id, text=f"""Player {player} is not currently uses this bot. Please invite him there: http://t.me/ticitacitoe_bot""")
        return
    if users[player[1:]] == message.chat.id and player[1:] != "debug":
        bot.send_message(message.chat.id, 'You cannot play with yourself.')
        return
    if active_sessions.get(users[player[1:]], None) != None:
        bot.send_message(
            message.chat.id, text=f"""Player {player} is playing at the moment.""")
        return
    if message.from_user.username in active_sessions:
        bot.edit_message_text('Cannot start new game while playing. /abort for giving up!',
                              message.chat.id, active_sessions[message.from_user.username].message_id,\
                                reply_markup=active_sessions[message.from_user.username].keyboard)
        return
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Yes', callback_data=f'apply yes {message.from_user.username}'),
                                              InlineKeyboardButton(text='No', callback_data=f'apply no {message.from_user.username}'))
    bot.send_message(
        users[player[1:]], text=f"Player {message.from_user.username} want to play with you. Proceed?:", reply_markup=markup)


@bot.message_handler(commands=['players'])
def send_players(message: "Message"):
    players = 'Available players:\n'
    for key in users.keys():
        if key not in active_sessions:
            players += f'@{key}\n'

    bot.send_message(message.chat.id, text=players)


@bot.message_handler(commands=['start', 'help'])
def start(message: "Message"):
    help_message = f"""Hi, this is my test bot.
To play with friend, please write /playwith #user_id#, for example /playwith @{message.from_user.username} or /playwith {message.from_user.username}. 
To get list of available players use /players.
You can abort current game by command /abort.
You can messaging during the game by /tell %your message% or by /tell @username while chilling.
Invite your friends to the private room by /room command: /room player1 player2 ... playerN. You can chat with your friends without and command in room.
To get people in your current room please use /myroom
To leave room please use /leave"""
    if message.from_user.username not in users:
        users[message.from_user.username] = message.chat.id
        with open('database.json', 'w') as db:
            json.dump(users, db, indent=4)

    bot.send_message(
        message.chat.id, help_message)
