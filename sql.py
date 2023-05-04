import os
from datetime import datetime
from pathlib import Path

import peewee

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_FILE = BASE_DIR / 'base.db'

db = peewee.SqliteDatabase(SQLITE_DB_FILE)


class Base(peewee.Model):
    class Meta:
        database = db


class MessageGroup(Base):
    message_id = peewee.IntegerField()
    group_id = peewee.IntegerField()
    chat_id_from = peewee.IntegerField()
    message = peewee.CharField()
    file = peewee.CharField()
    username = peewee.CharField()
    send = peewee.IntegerField()
    timestamp = peewee.DateTimeField()


db.create_tables([MessageGroup, ])


def check_group(group_id):
    try:
        MessageGroup.get(group_id=group_id)
        return True
    except peewee.DoesNotExist:
        return False


def delete_old_one(group_id, message, username):
    query = MessageGroup.select().where(
        (MessageGroup.message == message) &
        (MessageGroup.message != '') &
        (MessageGroup.username == username) &
        (MessageGroup.group_id != group_id) &
        (MessageGroup.send == 4)
        )
    for row in query:
        message_id = row.message_id
        (MessageGroup.delete().where(
            MessageGroup.message_id == message_id).execute())
        print(f'delete_old_one: {message_id}')

    return


def update_message(message_id, message):
    try:
        update_id = MessageGroup.get(message_id=message_id).message_id
        print(f'message: {message}')
        print(f'update_id: {message_id}')
        (MessageGroup.update(message=message).where(
            MessageGroup.message_id == update_id).execute())
    except peewee.DoesNotExist:
        print(f'update_id NO: {message_id}')
    return


def messsage_insert(
        message_id, group_id, chat_id_from,
        message, file, username, send=0):
    MessageGroup.create(
        message_id=message_id,
        group_id=group_id,
        chat_id_from=chat_id_from,
        message=message,
        file=file,
        username=username,
        send=send,
        timestamp=datetime.now()
    )
    return


def message_send_delete():
    current_time = datetime.now()

    query = MessageGroup.select().where(MessageGroup.send == 1)
    for row in query:
        file = row.file
        timestamp = row.timestamp
        dif_time = (current_time - timestamp)
        print(f'------------------dif_time----------------------: {dif_time}')

        if os.path.exists(file):
            os.remove(file)
            print(f'=======delete file {file} ===================')
        else:
            print(f'The file {file} does not exist')
    (MessageGroup.delete().where(MessageGroup.send == 1).execute())
    return


def select_message_to_send(select_type, group_id=''):
    result = []
    text = ''
    text_author = ''
    m_url = ''
    if select_type == 'new_group':
        query = MessageGroup.select().where(
            (MessageGroup.send == 0) &
            (MessageGroup.group_id != ''))
        update_send = 1

    if select_type == 'edit':
        query = MessageGroup.select().where(
            (MessageGroup.group_id == group_id) &
            (MessageGroup.send != 2))
        update_send = 2

    if select_type == 'new_one':
        query = MessageGroup.select().where(
            (MessageGroup.send == 4) &
            (MessageGroup.group_id == ''))
        update_send = 1

    for row in query:
        result.append(row.file)
        if row.message:
            text = str(row.message)
            username = str(row.username)
            m_id = str(row.message_id)
            m_url = f'https://t.me/{username}/{m_id}'

            text_author = f'\n\n**Источник: {m_url}** __({select_type})__'
        (MessageGroup.update(send=update_send).where(
            MessageGroup.id == row.id).execute())
    return result, text, text_author
