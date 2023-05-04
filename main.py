import os
# import time
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events

from dictionary import CHANEL_LINKS
from functions import (check_media, check_topic, check_words, get_history,
                       print_event_info, send_files, webpage_description)
from sql import (check_group, messsage_insert,
                 select_message_to_send, update_message)

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
my_chat_id = int(os.getenv('MY_CHAT_ID'))


PHOTO_DIR = Path(__file__).resolve().parent / 'photo/'

session = 'ffffffsssq23'

client = TelegramClient(session, api_id, api_hash)

# def cut_caption_test(text_test):

#     return (text_test[:965] + '...') if len(text_test) >= 965 else text_test

print(len('Источник: https://t.me/alquilertemporariobsas/4748 (new_one)'))
# print (cut_caption_test(text_test))
# # print(text_test)


@client.on(events.MessageEdited(chats=CHANEL_LINKS))
async def handler(event):

    await print_event_info(event)

    # sender_id = event.chat_id
    # print(dir(event.message))
    # username = event.chat.username
    message_id = event._message_id
    message_text = event.message.raw_text

    if event.message.grouped_id is not None:
        print('---------------группа фото Edited----------------')
        group_id = event.message.grouped_id
        print(group_id)
        to_send = []
        # path = await client.download_media(event.message, file=PHOTO_DIR)

        print(f'Edited YES group in base: {group_id}')

        update_message(message_id, message_text)

        # messsage_insert(message_id, group_id, sender_id,
        #                 message_text, path, username)

        to_send = select_message_to_send('edit', group_id)

        if (to_send[0]):
            await send_files(client, my_chat_id,
                             to_send[0], to_send[1], to_send[2])

            # message_send_delete()

        return

    if await check_media(event):
        return

    if await get_history(client, my_chat_id, message_text, 20):
        return

    update_message(message_id, message_text)

    # description = await webpage_description(event)
    # message_text = message_text+description

    # path = await client.download_media(event.message, file=PHOTO_DIR)

    # to_send = select_message_to_send('new_one', '')

    # if (to_send):
    #     files = to_send[0]
    #     text_to_send = str(to_send[1])
    #     author = str(to_send[2])

    #     messsage_insert(message_id, '', sender_id,
    #                     message_text, path, username, 4)

    #     print('-----------------------------------------------')
    #     print(f'ids_to_send - {files} {text_to_send} {author}')
    #     print('-----------------------------------------------')
    #     text_to_send = cut_caption(text_to_send)

    #     caption = text_to_send + author
    #     print(f'len(caption): {len(caption)}')

    #     topic = await get_rooms(message_text)

    #     await client.send_file(my_chat_id, file=files,
    #                           reply_to=topic, caption=caption)

    print('-----END EDIT------------')

    return


@client.on(events.NewMessage(chats=CHANEL_LINKS))
async def handlernew(event):

    await print_event_info(event)

    sender_id = event.chat_id
    username = event.chat.username
    message_id = event._message_id
    message_text = event.message.raw_text
    to_send = []

    # if new message send from topic of group
    if event.message.reply_to_msg_id is not None:
        reply_to_msg_id = event.message.reply_to_msg_id
        if await check_topic(username, reply_to_msg_id):
            return

    if event.message.grouped_id is not None:
        print('---------------группа фото----------------')
        group_id = event.message.grouped_id
        print(group_id)
        # load media of the message
        path = await client.download_media(event.message, file=PHOTO_DIR)

        if check_group(group_id):
            print(f'YES group in base: {group_id}')
            messsage_insert(message_id, group_id, sender_id,
                            message_text, path, username)
            return
        else:
            print(f'NO group in base: {group_id}')
            to_send = select_message_to_send('new_group')

            # delete_old_one(group_id, message_text, username)

            messsage_insert(message_id, group_id, sender_id,
                            message_text, path, username)

        if (to_send[0]):
            await send_files(client, my_chat_id,
                             to_send[0], to_send[1], to_send[2])

        return

    # new one message no group ------------------------
    if await check_media(event):
        return

    if await get_history(client, my_chat_id, message_text, 20):
        return

    description = await webpage_description(event)
    message_text = message_text+description

    to_send = select_message_to_send('new_one', '')

    if check_words(message_text):
        path = await client.download_media(event.message, file=PHOTO_DIR)
        messsage_insert(message_id, '', sender_id,
                        message_text, path, username, 4)

    if (to_send[0]):
        await send_files(client, my_chat_id,
                         to_send[0], to_send[1], to_send[2])

    print('-------END new message--------------')
    return


if __name__ == '__main__':
    client.start()
    client.run_until_disconnected()
