from requests import exceptions
from message_handlers import *
from callback_handlers import *
from telespeaker import *

while True:
    try:
        bot.polling()
    except KeyboardInterrupt:
        exit()
    except (exceptions.ReadTimeout, exceptions.ConnectionError) as e:
        print(e)
