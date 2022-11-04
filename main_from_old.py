import asyncio
import logging
import os
from collections import deque

import httpx
from dotenv import load_dotenv
from telegram_parser import telegram_parser
from telethon import TelegramClient

from utils import create_logger, get_history, send_error_message

load_dotenv()


api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
my_chat_id = os.getenv('MY_CHAT_ID')
bot_token = os.getenv('TELEGRAM_TOKEN')

###########################
# Можно добавить телеграм канал, rss ссылку или изменить фильтр новостей

telegram_channels = {
    1532197220: 'https://t.me/fromtestchannel',
    # 1428717522: 'https://t.me/gazprom',
    # 1101170442: 'https://t.me/rian_ru',
    # 1133408457: 'https://t.me/prime1',
    # 1149896996: 'https://t.me/interfaxonline',
    # # 1001029560: 'https://t.me/bcs_express',
    # 1203560567: 'https://t.me/markettwits',  # Канал аггрегатор новостей
}


def check_pattern_func(text):
    '''Вибирай только посты или статьи про газпром или газ'''
    words = text.lower().split()

    key_words = [
        'газп',     # газпром
        'газо',     # газопровод, газофикация...
        'поток',    # сервеный поток, северный поток 2, южный поток
        'спг',      # спг - сжиженный природный газ
        'gazp',
    ]

    for word in words:
        if 'газ' in word and len(word) < 6:  # газ, газу, газом, газа
            return True

        for key in key_words:
            if key in word:
                return True

    return False


###########################
# Если у парсеров много ошибок или появляются повторные новости

# 50 первых символов от поста - это ключ для поиска повторных постов
n_test_chars = 50

# Количество уже опубликованных постов, чтобы их не повторять
amount_messages = 50

# Очередь уже опубликованных постов
posted_q = deque(maxlen=amount_messages)

###########################


logger = create_logger('agregator2')
logger.info('Start...')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

tele_logger = create_logger('telethon', level=logging.ERROR)

bot = TelegramClient(
    'dfgdfghfghetu908t4uhriwjhihfidsfg8',
    api_id,
    api_hash,
    base_logger=tele_logger,
    loop=loop
)

bot.start(bot_token=bot_token)


async def send_message_func(text):
    '''Отправляет посты в канал через бот'''
    await bot.send_message(
        int(my_chat_id),
        parse_mode='html',
        link_preview=False,
        message=text
    )

    logger.info(text)


# Телеграм парсер
client = telegram_parser(
    'sdgsdfgsdfgsdfgshgjhhfkjkghklgh777777777777777777lk',
    api_id,
    api_hash,
    telegram_channels,
    posted_q,
    n_test_chars,
    None,
    send_message_func,
    tele_logger,
    loop
)


# Список из уже опубликованных постов, чтобы их не дублировать
history = loop.run_until_complete(get_history(client, my_chat_id,
                                              n_test_chars, amount_messages))

posted_q.extend(history)

httpx_client = httpx.AsyncClient()

try:
    # Запускает все парсеры
    client.run_until_disconnected()

except Exception as e:
    message = f'&#9888; ERROR: telegram parser (all parsers) is down! \n{e}'
    loop.run_until_complete(send_error_message(message, bot_token,
                                               my_chat_id, logger))
finally:
    loop.run_until_complete(httpx_client.aclose())
    loop.close()
