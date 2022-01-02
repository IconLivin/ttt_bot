from requests import exceptions
from message_handlers import *
from callback_handlers import *
from telespeaker import *

while True:
    try:
        bot.polling()
    except (exceptions.ReadTimeout, exceptions.ConnectionError) as e:
        print(e)
    except KeyboardInterrupt:
        exit()
