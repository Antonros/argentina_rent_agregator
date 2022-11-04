import os

from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from telethon import TelegramClient, events

load_dotenv()

# print(dir(telethon.tl.types))

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('TELEGRAM_TOKEN')
my_chat_id = int(os.getenv('MY_CHAT_ID'))


def telegram_parser(session, api_id, api_hash, telegram_channels):
    '''Телеграм агрегатор каналов'''

    # Ссылки на телеграмм каналы
    telegram_channels_links = list(telegram_channels.values())

    client = TelegramClient(
        session,
        api_id,
        api_hash
    )
    client.start()

    @client.on(events.Album(chats=telegram_channels_links))
    async def album_handler(event):
        print('Got an album with', len(event), 'items XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        # print(dir(event))
        text_message = ''
        for message in event.messages:
            text_message += message.message
        print(text_message)
        print(' ----- ')

        if await get_history(text_message, 20):
            print('-----уже было группа------')
            return

        # messages = await client.get_messages(int(my_chat_id), 10)
        # for message in messages:
        #     difference = fuzz.ratio(message.raw_text, text_message)
        #     print(message.raw_text)
        #     print(f'========={difference} группа==============')
        #     if difference > 98:
        #         print('-----уже было группа------')
        #         return

        if text_message == '':
            print('-----нет текста в группе------')
            print('-----------------------------------------------')
            return

        await event.forward_to(my_chat_id)
        return

    @client.on(events.NewMessage(chats=telegram_channels_links))
    async def handler(event):
        '''Забирает посты из телеграмм каналов и посылает их в наш канал'''

        chanel_id = event.message.peer_id.channel_id

        # print(dir(event.message.media))

        if event.message.grouped_id is not None:
            # print(f'{chanel_id} -----группа фото------')
            # print(f'media - {event.message}')
            # print('-----------------------------------------------')
            return

        if event.raw_text == '':
            print(f'{chanel_id} -----нет текста------')
            # print(f'media - {event.message}')
            print('-----------------------------------------------')
            print(' ')
            return

        if not hasattr(event.message.media, 'photo') and not hasattr(event.message.media, 'webpage'):
            print(f'{chanel_id} -----нет фото и вебконтента------')
            # print(f'message - {event.message}')
            print('-----------------------------------------------')
            print(' ')
            return

        if hasattr(event.message.media, 'webpage'):
            if event.message.media.webpage.photo is None:
                print(f'{chanel_id} -----есть веб, но нет фото------')
                # print(f'message - {event.message}')
                print('-----------------------------------------------')
                print(' ')
                return

        # messages = await client.get_messages(int(my_chat_id), 10)
        # for message in messages:
        #     difference = fuzz.ratio(message.raw_text, event.raw_text)
        #     print(f'========={difference}==============')
        #     if difference > 98:
        #         print(f'{chanel_id} -----уже было------')
        #         return

        if await get_history(event.raw_text, 0):
            print(f'{chanel_id} -----уже было------')
            return

        print(f'{chanel_id}')
        print(f'message - {event}')
        print('-----------------------------------------------')
        print(' ')

        await client.forward_messages(my_chat_id, event.message)

    return client


async def get_history(income_message, amount_messages):
    messages = await client.get_messages(my_chat_id, amount_messages)
    print(f'ИСХОДНЫЙ ТЕКСТ --- {income_message}')
    count = 1
    for message in messages:
        similarity = fuzz.ratio(message.raw_text, income_message)
        print(f'УЖЕ ЕСТЬ ТЕКСТ {count} - {message.id} --- {message.raw_text}')
        print(f'similarity - {similarity} +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(' ')
        count += 1
        if similarity > 95:
            return True
    return False


# if __name__ == "__main__":

telegram_channels = {
    1671940764: 'https://t.me/buenas_hatas',
    1762313483: 'https://t.me/alquilar_BuenosAires',
    1594905108: 'https://t.me/arendaArgentinaprop',
    1734338501: 'https://t.me/ruargentinadom',
    1532197220: 'https://t.me/fromtestchannel',
    1651128175: 'https://t.me/alquilertemporariobsas',
    1890281683: 'https://t.me/argentina_apartamentos',
    1632649859: 'https://t.me/ArgentinaHouse',
    1532876637: 'https://t.me/arendacaba',
    1585013175: 'https://t.me/apartment_in_Buenos_Aires',
    1591166110: 'https://t.me/alquilertemporario2022',
}

client = telegram_parser('sdgsdfgsdfgsdfgshgjhhfkjkghklgh777777777777777777lk', api_id, api_hash, telegram_channels)

client.run_until_disconnected()
