from fuzzywuzzy import fuzz

from dictionary import (ALL_LIST, BLACK_LIST, FOUR_ROUM, ONE_ROOM,
                        THREE_ROOM, TOPICS, TWO_ROOM)


async def get_history(client, chat_id, income_message, amount_messages):
    messages = await client.get_messages(chat_id, amount_messages)
    print('------Проверка совпадений------------')
    print(f'ИСХОДНЫЙ ТЕКСТ --- {income_message}')
    if income_message == '':
        print('-----нет текста------')
        return True

    for wrd in BLACK_LIST:
        if income_message.find(wrd) >= 0:
            print(f'BLACK_LIST {wrd}')
            return True

    for message in messages:
        similarity = fuzz.ratio(str(message.text), str(income_message))
        print(f'{message.id} similarity - {similarity} +++++++++++++')
        if similarity >= 95:
            print('-----совпадение больше 95------')
            return True
    return False


def get_rooms(message: str):
    message = message.lower()
    message = message.split()
    message = ''.join(message)
    print(message)
    for word in ONE_ROOM:
        if message.find(word) >= 0:
            print(f'{word} 12')
            return 12
    for word in TWO_ROOM:
        if message.find(word) >= 0:
            print(f'{word} 5')
            return 5
    for word in THREE_ROOM:
        if message.find(word) >= 0:
            print(f'{word} 9')
            return 9
    for word in FOUR_ROUM:
        if message.find(word) >= 0:
            print(f'{word} 18')
            return 18
    return 1


async def check_topic(username, reply_to_msg_id):
    count_top = 0
    count_name = 0
    for topic in TOPICS:
        x = topic.split('/')
        name = x[0]
        topic_id = x[1]
        print(f'name: {name} topic_id: {topic_id}')
        if username == name:
            count_name += 1
            if reply_to_msg_id == int(topic_id):
                count_top += 1
    print(f'count_name: {count_name} count_top: {count_top}')
    if count_name != 0 and count_top == 0:
        return True
    return False


async def print_event_info(event):
    print('-------------------------------------------------------')
    print(f'---------------{event._event_name}----------------')
    print('-------------------------------------------------------')

    # print(dir(event.message))
    print(f'event.message_name: {event._event_name}')
    print(f'chat_id: {event.chat_id}')
    print(f'username: {event.chat.username}')
    print(f'post_author: {event.message.post_author}')
    # print(f'reply: {event.message.reply}')
    print(f'message_id: {event._message_id}')
    print(f'grouped_id: {event.message.grouped_id}')
    print(f'raw_text: {event.message.raw_text}')
    # print(f'photo: {event.message.photo}')
    print(f'reply_to_msg_id: {event.message.reply_to_msg_id}')
    print(f'reply_to: {event.message.reply_to}')
    # print(f'media: {event.message.media}')
    print(f'file: {event.message.file}')
    # print(f'message: {event.message}')
    return


async def check_media(event):
    if (not hasattr(event.message.media, 'photo') and
       not hasattr(event.message.media, 'webpage') and
       event.message.video is None):

        print(f'{event.chat_id} -----нет фото и вебконтента------')
        print('-----------------------------------------------')
        print(' ')
        return True
    if hasattr(event.message.media, 'webpage'):
        if event.message.media.webpage.photo is None:
            print(f'{event.chat_id} -----есть веб, но нет фото------')
            print('-----------------------------------------------')
            print(' ')
            return True
    return False


async def webpage_description(event):
    description = ''
    if hasattr(event.message.media, 'webpage'):
        if event.message.media.webpage.description is not None:
            description = str(event.message.media.webpage.description)
    return description


def cut_caption(text, author):
    max_len = 1024 - len(author)
    return (text[:max_len] + '...') if len(text) >= max_len else text


async def send_files(client, chat_id, files, text_to_send, author):

    print('-----------------------------------------------')
    print(f'ids_to_send - {files} {text_to_send} {author}')
    print('-----------------------------------------------')

    if await get_history(client, chat_id, text_to_send, 20):
        return

    topic = get_rooms(text_to_send)

    text_to_send = cut_caption(text_to_send, author)
    print(text_to_send)

    caption = text_to_send + author
    print(f'len(caption): {len(caption)}')

    await client.send_file(chat_id, files, reply_to=topic, caption=caption)
    return


def check_words(text):
    text = text.lower()
    if text == '':
        return True
    for word in ALL_LIST:
        if text.find(word) >= 0:
            print(f'IN ALL_LIST  {word}')
            return True
    print(f'NO IN ALL_LIST {word}')
    return False
