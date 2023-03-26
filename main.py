from requests import exceptions
from message_handlers import *
from callback_handlers import *
from telespeaker import *

def main():
    try:
        while True:
            bot.polling()
    except (exceptions.ReadTimeout, exceptions.ConnectionError) as e:
        print(e)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()