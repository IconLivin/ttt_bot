from properties import bot, active_sessions, users, types

rooms = []


@bot.callback_query_handler(func=lambda call: call.data.startswith('room'))
def join_room(call):
    invited_person = call.message.chat.username
    inviter = call.data.split()[2]
    answer = call.data.split()[1]
    if answer == 'no':
        bot.send_message(
            users[inviter], text=f'@{invited_person} refused to join room.')
        bot.edit_message_text('Ok.', call.message.chat.id, call.message.id)
        return

    bot.edit_message_text('Joined room', call.message.chat.id, call.message.id)
    if len(rooms) == 0:
        rooms.append([inviter, invited_person])
        bot.send_message(
            users[inviter], f'@{invited_person} joined room!')
        return
    for room in rooms:
        if inviter in room:
            for pin in room:
                bot.send_message(users[pin], f'@{invited_person} joined room!')
                return
            room.append(invited_person)

    rooms.append([inviter, invited_person])
    bot.send_message(
        users[inviter], f'@{invited_person} joined room!')


@bot.message_handler(commands=['room'])
def create_room(message):
    sender = message.from_user.username
    invited_users = message.text.split()[1:]
    if len(invited_users) == 0:
        bot.send_message(
            message.chat.id, 'No users specified. To use this command type /room and usernames separated by spece. For example /room obeme_dochka yomama etc.')
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text=f'Yes',
                                                                         callback_data=f'room yes {message.from_user.username}'),
                                              types.InlineKeyboardButton(text=f'No', callback_data=f'room no {message.from_user.username}'))
    not_found_users = []
    if len(rooms) == 0:
        for user in invited_users:
            if user not in users:
                not_found_users.append(user.lstrip('@'))
                continue
            if user == sender:
                continue
            bot.send_message(
                users[user], text=f'@{sender} invites you to the room. Join?', reply_markup=markup)
    else:
        for user in invited_users:
            for room in rooms:
                if user not in users:
                    not_found_users.append(user.lstrip('@'))
                    continue
                if user in room:
                    bot.send_message(
                        users[user], text=f'@{sender} invites to the room. Leave current room and join his chat?', reply_markup=markup)
                else:
                    bot.send_message(
                        users[user], text=f'@{sender} invites you to the room. Join?', reply_markup=markup)

    not_found_users = list(map(
        lambda x: '@' + x, filter(lambda x: len(x) != 0, not_found_users)))
    if len(not_found_users) != 0:
        nfu = "\n".join(not_found_users)
        bot.send_message(
            users[sender], text=f'Specified users are not found: \n{nfu}')


@bot.message_handler(commands=['tell'])
def tell_to_user(message):
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
            f'@{player} tells: {" ".join(message.text.split()[1:])}', users[active_sessions[player][4]], active_sessions[active_sessions[player][4]][5], reply_markup=active_sessions[player][0])


@bot.message_handler(commands=['myroom'])
def get_roommates(message):
    for room in rooms:
        if message.from_user.username in room:
            roommates = '\n'.join(
                '@' + mate for mate in room if mate != message.from_user.username)
            bot.send_message(message.chat.id, f'Your roommates:\n{roommates}')
            return
    bot.send_message(message.chat.id, 'You are not in the room.')


@bot.message_handler(commands=['leave'])
def leave_room(message):
    for room in rooms:
        if message.from_user.username in room:
            bot.send_message(message.chat.id, 'Ok.')
            room.remove(message.from_user.username)
            for pin in room:
                bot.send_message(
                    users[pin], f'@{message.from_user.username} left room.')
            if len(room) == 1:
                rooms.remove(room)
            print(rooms)
            return
    bot.send_message(message.chat.id, 'You are not in room.')


@bot.message_handler(content_types=['text'])
def send_message_to_room(message):
    for room in rooms:
        if message.from_user.username in room:
            for pin in room:
                if pin == message.from_user.username:
                    continue
                bot.send_message(
                    users[pin], f'@{message.from_user.username}: {message.text}')
