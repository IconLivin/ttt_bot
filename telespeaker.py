from properties import bot, active_sessions, users, InlineKeyboardButton, InlineKeyboardMarkup
from dataclasses import dataclass
import typing
from typing import List
from telebot.types import Sticker, Audio, Voice, Document

if typing.TYPE_CHECKING:
    from telebot.types import Message, CallbackQuery

@dataclass
class Room:
    owner: str
    users: List[str]

rooms = {}


@bot.callback_query_handler(func=lambda call: call.data.startswith('room'))
def join_room(call: "CallbackQuery"):
    invited_person = call.message.chat.username
    inviter = call.data.split()[2]
    answer = call.data.split()[1]
    if answer == 'no':
        bot.send_message(
            users[inviter], text=f'@{invited_person} refused to join room.')
        bot.edit_message_text('Ok.', call.message.chat.id, call.message.id)
        return

    bot.edit_message_text('Joined room', call.message.chat.id, call.message.id)
    if not inviter in rooms:
        rooms[inviter] = Room(inviter, [inviter, invited_person])
        bot.send_message(
            users[inviter], f'@{invited_person} joined room!')
        return
    for owner, room in rooms.items():
        if inviter == owner:
            for pin in room.users:
                bot.send_message(users[pin], f'@{invited_person} joined room!')
            room.users.append(invited_person)

    bot.send_message(
        users[inviter], f'@{invited_person} joined room!')


@bot.message_handler(commands=["add"])
def add_to_room(message: "Message"):
    owner = message.from_user.username
    invited_persons = list(map(lambda x: x.lstrip("@"), message.text.split()[1:]))
    if owner not in rooms:
        bot.send_message(message.chat.id, "You are not own any room")
        return
    not_found_users = []
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'Yes', callback_data=f'room yes {message.from_user.username}'),
                                              InlineKeyboardButton(text=f'No', callback_data=f'room no {message.from_user.username}'))
    in_your_session = []
    for ip in invited_persons:
        if ip in rooms[owner].users:
            in_your_session.append(ip)
            continue
        if ip not in users:
            not_found_users.append(ip)
        bot.send_message(users[ip], f"@{owner} invites to the room. Join?", reply_markup=markup)

    if in_your_session:
        bot.send_message(message.chat.id, "In your session already:\n" + "\n".join("@" + iys for iys in in_your_session))

    if not_found_users:
        bot.send_message(message.chat.id, "Users not found:\n" + "\n".join("@" + nfu for nfu in not_found_users))


@bot.callback_query_handler(func=lambda call: call.data.startswith("leave"))
def leave_handler(call: "CallbackQuery"):
    user = call.from_user.username
    answer = call.data.split()[1]
    if answer == "no":
        bot.edit_message_text("Not leaving", call.message.chat.id, call.message.message_id)

    for owner, room in rooms.items():
        if owner == user:
            for pid in room.users:
                bot.send_message(users[pid], f"@{user} disolved the room")
            rooms.pop(user)
            return
        if user in room:
            room.remove(user)
            for pid in room:
                bot.send_message(users[pid], f"@{user} left the room")
            bot.send_message(users[user], "You left the room")


@bot.message_handler(commands=['room'])
def create_room(message: "Message"):
    sender = message.from_user.username
    invited_users = message.text.split()[1:]
    invited_users = list(map(lambda x: x.lstrip("@"), invited_users))
    print(invited_users)
    if len(invited_users) == 0:
        bot.send_message(message.chat.id,\
            'No users specified. To use this command type /room and usernames separated by space. For example /room obeme_dochka yomama etc.')
        return
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'Yes', callback_data=f'room yes {message.from_user.username}'),
                                              InlineKeyboardButton(text=f'No', callback_data=f'room no {message.from_user.username}'))
    not_found_users = []

    for owner, room in rooms.items():
        print("In room check")
        if sender == owner or sender in room.users:
            leave_markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'Yes', callback_data=f'leave yes'),
                                                InlineKeyboardButton(text=f'No', callback_data=f'leave no'))
            bot.send_message(message.chat.id, "You are currently in the room, leave?", reply_markup=leave_markup)
            return

    for user in invited_users:
        print("invite section")
        if user not in users:
            not_found_users.append(user.lstrip('@'))
            print("not found", user)
            continue
        if any(map(lambda x: user in x.users, rooms.values())):
            print(user, "in another room")
            bot.send_message(
                users[user], text=f'@{sender} invites you to the room. Leave current room and join his chat?', reply_markup=markup)
        else:
            print("send invite")
            bot.send_message(
                users[user], text=f'@{sender} invites you to the room. Join?', reply_markup=markup)

    not_found_users = list(map(
        lambda x: '@' + x, filter(lambda x: len(x) != 0, not_found_users)))
    if len(not_found_users) != 0:
        nfu = "\n".join(not_found_users)
        bot.send_message(
            users[sender], text=f'Specified users are not found: \n{nfu}')


@bot.message_handler(commands=['tell', 't'])
def tell_to_user(message: "Message"):
    player = message.from_user.username
    if player not in active_sessions:
        try:
            to_player, player_message = message.text.split()[1].strip(
                '@'), ' '.join(message.text.split()[2:])
        except IndexError:
            bot.send_message(
                message.chat.id, 'No user specified. To send message type /tell #@username# $message%. For exmaple /tell @obeme_dochka Hi!')
            return
        if len(player_message) == 0:
            return

        if to_player not in users:
            bot.send_message(
                message.chat.id, text=f"""Player {player} is not currently uses this bot. Please invite him there: http://t.me/ticitacitoe_bot""")
            return
        bot.send_message(
            users[to_player], text=f"@{player} tells: {player_message}")
        return
    if len(message.text.strip()) != 5:
        bot.edit_message_text(
            f'@{player} tells: {" ".join(message.text.split()[1:])}',\
                users[active_sessions[player].enemy],\
                    active_sessions[active_sessions[player].enemy].message_id, reply_markup=active_sessions[player].keyboard)


@bot.message_handler(commands=['myroom'])
def get_roommates(message: "Message"):
    for room in rooms:
        if message.from_user.username in room.users:
            roommates = '\n'.join(
                '@' + mate for mate in room.users if mate != message.from_user.username)
            bot.send_message(message.chat.id, f'Your roommates:\n{roommates}')
            return
    bot.send_message(message.chat.id, 'You are not in the room.')


@bot.message_handler(commands=['leave'])
def leave_room(message: "Message"):
    user = message.from_user.username
    silent = True if len(message.text.split()) == 2 else False
    for owner, room in rooms.items():
        if owner == user:
            for pid in room.users:
                bot.send_message(users[pid], f"@{user} disolved the room")
            rooms.pop(user)
            return
        if message.from_user.username in room.users:
            bot.send_message(message.chat.id, 'Ok.')
            room.users.remove(message.from_user.username)
            if not silent:
                for pin in room:
                    bot.send_message(
                        users[pin], f'@{message.from_user.username} left room.')
            if len(room) == 1:
                rooms.remove(room)
            print(rooms)
            return
    bot.send_message(message.chat.id, 'You are not in room.')


@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice',\
                                                               'video', 'document', 'text',\
                                                               'location', 'contact', 'sticker'])
def send_message_to_room(message: "Message"):
    writer = message.from_user.username
    for room in rooms.values():
        if writer in (room.users):
            for pin in room.users:
                if pin == writer:
                    continue
                bot.send_message(
                    users[pin], f'@{writer}: {message.text if message.text else ""}', )
                for caption in [message.sticker, message.audio, message.voice, message.document, message.photo]:
                    if not caption:
                        continue
                    if isinstance(caption, Sticker):
                        bot.send_sticker(users[pin], caption.file_id)
                    elif isinstance(caption, Audio):
                        bot.send_audio(users[pin], caption.file_id)
                    elif isinstance(caption, Voice):
                        bot.send_voice(users[pin], caption.file_id)
                    elif isinstance(caption, Document):
                        bot.send_document(users[pin], caption.file_id)
                    elif isinstance(caption, list):
                        photos = {p.file_id for p in caption}
                        for photo in photos:
                            bot.send_photo(users[pin], photo)
                    return
