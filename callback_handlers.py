from properties import bot, active_sessions, crossIcon, circleIcon, Turn, users, logic_markup, position, types


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
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton(text=f' ', callback_data=f'0'),
               types.InlineKeyboardButton(text=f' ', callback_data=f'1'),
               types.InlineKeyboardButton(text=f' ', callback_data=f'2'))
    markup.add(types.InlineKeyboardButton(text=f' ', callback_data=f'3'),
               types.InlineKeyboardButton(text=f' ', callback_data=f'4'),
               types.InlineKeyboardButton(text=f' ', callback_data=f'5'))
    markup.add(types.InlineKeyboardButton(text=f' ', callback_data=f'6'),
               types.InlineKeyboardButton(text=f' ', callback_data=f'7'),
               types.InlineKeyboardButton(text=f' ', callback_data=f'8'))
    return markup


@bot.callback_query_handler(func=lambda call: call.data in [str(i) for i in range(9)])
def command_click_inline(call):
    user = call.message.chat.username

    if user not in active_sessions:
        bot.send_message(
            call.message.chat.id, text='No active session is found, please use /playwith to start new game.')
        return
    if active_sessions[user][2] == Turn.not_your:
        return
    if len(active_sessions[user]) != 6:
        active_sessions[user].append(
            call.message.id)
    if active_sessions[user][1][int(call.data)] != ' ':
        bot.edit_message_text(
            'Current position is occupied!', call.message.chat.id, call.message.id, reply_markup=active_sessions[user][0])
        return

    figure = active_sessions[user][3]

    active_sessions[user][0].keyboard[position[call.data][0]
                                      ][position[call.data][1]].text = figure
    active_sessions[user][1][int(call.data)] = user
    active_sessions[user][2] = Turn.not_your
    active_sessions[active_sessions[user][4]][2] = Turn.your

    cond = is_win(active_sessions[user][1])
    if cond != 'continue':
        text = 'You won!' if cond == 'win' else "Draw :("
        enemy_text = f'@{user} won...' if cond == 'win' else 'Draw :('
        for i in range(3):
            for j in range(3):
                active_sessions[user][0].keyboard[i][j].callback_data = 'end'
        bot.edit_message_text(
            text, call.message.chat.id, call.message.id, reply_markup=active_sessions[user][0])
        bot.edit_message_text(
            enemy_text, users[active_sessions[user][4]], active_sessions[active_sessions[user][4]][5], reply_markup=active_sessions[user][0])
        active_sessions.pop(active_sessions[user][4])
        active_sessions.pop(user)
        return

    bot.edit_message_text('Your opponent turn',
                          call.message.chat.id, call.message.id, reply_markup=active_sessions[user][0])

    bot.edit_message_text(
        "Your turn", users[active_sessions[user][4]], active_sessions[active_sessions[user][4]][5], reply_markup=active_sessions[user][0])


@bot.callback_query_handler(func=lambda call: call.data.startswith('apply'))
def apply_game(call):
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
    active_sessions[enemy] = [keyboard, logic_keyboard,
                              Turn.your, crossIcon, user]
    active_sessions[user] = [
        keyboard, logic_keyboard, Turn.not_your, circleIcon, enemy, call.message.id]
    bot.send_message(users[enemy], text='Your turn',
                     reply_markup=active_sessions[enemy][0])
    bot.edit_message_text('Your opponent turn',
                          call.message.chat.id, call.message.id, reply_markup=active_sessions[user][0])
