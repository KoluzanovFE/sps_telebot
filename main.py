import sqlite3
import telebot
import time
from telebot import types
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


def check_admins_rights_by_message(message):
    print(f"username = {message.from_user.username}, chat_id = {message.chat.id}, chat_type = {message.chat.type}")
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    query = f"SELECT * FROM admins WHERE userId = '{message.from_user.username}';"
    curs.execute(query)
    admin_users = curs.fetchall()
    curs.close()
    db.close()
    if len(admin_users) > 0:
        return True
    else:
        return False


def check_admins_rights_by_name(name):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    query = f"SELECT * FROM admins WHERE userId = '{name}';"
    curs.execute(query)
    admin_users = curs.fetchall()
    curs.close()
    db.close()
    if len(admin_users) > 0:
        return True
    else:
        return False


def check_group(group_id):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"SELECT * FROM chatSPS WHERE chatID = {group_id};")
    admin_users = curs.fetchall()
    curs.close()
    db.close()
    if len(admin_users) > 0:
        return True
    else:
        return False


def add_group(group_id, chat_title):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"""INSERT INTO chatSPS (chatID, chatName) VALUES ({group_id}, '{chat_title}');""")
    db.commit()
    curs.close()
    db.close()


def get_group_name(chatId):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"""SELECT chatName FROM chatSPS WHERE chatID = {chatId};""")
    group_name = curs.fetchall()
    curs.close()
    db.close()
    return group_name[0]


def get_all_groups():
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"SELECT * FROM chatSPS ORDER BY chatName;")
    groups = curs.fetchall()
    curs.close()
    db.close()
    return groups


def delete_group(groupId):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"DELETE FROM chatSPS WHERE chatID = {groupId};")
    db.commit()
    curs.close()
    db.close()


def check_state(userId):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"SELECT * FROM mainChatUserState WHERE userId = '{userId}';")
    admin_users = curs.fetchall()
    curs.close()
    db.close()
    if len(admin_users) > 0:
        return True
    else:
        return False


def get_state(userId):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"SELECT * FROM mainChatUserState WHERE userId = '{userId}';")
    admin_users = curs.fetchall()
    curs.close()
    db.close()
    return admin_users[0][1]


def update_group_name(groupId, new_name):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    sql_update_query = f"""UPDATE chatSPS SET chatName = '{new_name}' WHERE chatID = '{groupId}';"""
    curs.execute(sql_update_query)
    db.commit()
    curs.close()
    db.close()


def update_state(userId, new_state):
    db=sqlite3.connect('AutoSendBot.db')
    curs=db.cursor()
    sql_update_query = f"""UPDATE mainChatUserState SET state = '{new_state}' WHERE userId = '{userId}';"""
    curs.execute(sql_update_query)
    db.commit()
    curs.close()
    db.close()


def add_state(userId, state):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"""INSERT INTO mainChatUserState (userId, state) VALUES ('{userId}', '{state}');""")
    db.commit()
    curs.close()
    db.close()


def add_admin(name):
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"""INSERT INTO admins (userId) VALUES ('{name}');""")
    db.commit()
    db.close()


def get_all_chats():
    db = sqlite3.connect('AutoSendBot.db')
    curs = db.cursor()
    curs.execute(f"SELECT chatID FROM chatSPS;")
    chats = curs.fetchall()
    curs.close()
    db.close()
    return chats


def check_state_send_to_all(message):
    username = message.from_user.username
    if get_state(username) == 'send_to_all':
        return True
    return False


markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("/send_to_all")
item2 = types.KeyboardButton("/help")
item3 = types.KeyboardButton("/group_list")
markup1.add(item1)
markup1.add(item2)
markup1.add(item3)


@bot.message_handler(func=check_admins_rights_by_message, commands=['start'])
def start_function(message):
    if message.chat.type == 'private':
        username = message.from_user.username
        if check_state(username):
            update_state(username, 'start')
        else:
            add_state(message.from_user.username, 'start')

        bot.send_message(message.chat.id, 'Для продолжения введи или выбери любую команду из выпадающего списка!', reply_markup=markup1)

    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        if check_group(message.chat.id):
            bot.send_message(message.chat.id, 'Группа уже была добавлена список рассылок!')
        else:
            add_group(message.chat.id, message.chat.title)
            bot.send_message(message.chat.id, 'Группа добавлена список рассылок!')

@bot.message_handler(func=lambda x: check_admins_rights_by_message(x) * (x.chat.type == 'group' or x.chat.type == 'supergroup'), commands=['delete'])
def delete_bot_from_group(message):
    delete_group(message.chat.id)
    bot.send_message(message.chat.id, "Удаление чата из бота произошло успешно!")


@bot.message_handler(func=lambda x: check_admins_rights_by_message(x) * x.chat.type == 'private', commands=['help'])
def help_message(message):
    username = message.from_user.username
    if check_state(username):
        update_state(username, 'start')
    else:
        add_state(message.from_user.username, 'start')

    bot.send_message(message.chat.id, 'Для того, чтобы добавить бота в чат, просто пригласи его в роли пользователя и отправь в чат команду /start! Его ник - @AutoSenderSPS_bot.'
                                          '\n\nДля удаления бота из группы используй команду /delete в чате группы.'
                                          ' \n\nИспользуй команду /send_to_all в чате с ботом для того, чтобы сделать рассылку во все чаты, в которые был добавлен бот!'
                                      ' \n\nИспользуй команду /group_list в чате с ботом, чтобы посмотреть все чаты, куда был добавлен бот.'
                                      ' \n\nПо всем вопросам о работе бота обращаться к @pphll.', reply_markup=markup1)


@bot.message_handler(func=lambda x: check_admins_rights_by_message(x) * x.chat.type == 'private', commands=['group_list'])
def get_all_groups_command(message):
    if message.chat.type == 'private':
        username = message.from_user.username
        update_state(username, 'start')
        group_list = get_all_groups()
        text = ''
        i = 1
        for item in group_list:
            text+= f"{i}. {item[1]} \n"
            i += 1
        if text == '':
            text='Никакие группы подлючены не были!'

        bot.send_message(message.chat.id, text, reply_markup=markup1)


@bot.message_handler(func=lambda x: check_admins_rights_by_message(x) * x.chat.type == 'private', commands=['send_to_all'])
def send_to_all_first_step(message):
    if message.chat.type == 'private':
        username = message.from_user.username
        if check_state(username):
            update_state(username, 'send_to_all')
        else:
            add_state(message.from_user.username, 'send_to_all')

        bot.send_message(message.chat.id, 'Введи сообщение, которое хочешь отрпавить всем группам!'
                                          '\n\nЛюбые сообщения будут пересылаться в групповые чаты (в том числе и файлы), пока ты не введешь любую другую команду. Напрмиер, /start или /help!'
                                          '\n\nСмотри не ошибись! В боте не предусмотрена функция исправления!', reply_markup=markup1)


@bot.message_handler(func=(lambda x: check_admins_rights_by_message(x) * check_state_send_to_all(x) * x.chat.type == 'private'),
                     content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location'])
def send_to_all_second_step(message):
    if message.chat.type == 'private':
        chats = get_all_chats()
        for id in chats:
            try:
                bot.forward_message(id[0], message.chat.id, message.id)
                time.sleep(0.5)
            except:
                print("[SECOND STEP ERROR!]")
                continue
        bot.send_message(message.chat.id, 'Готово!\nЧто еще ты хочешь отправить?\nДля заверешния нужна любая команда, например /start.')

@bot.message_handler(func=lambda x: check_admins_rights_by_message(x) * x.chat.type == 'private')
def all_other_messages_with_rights(message):
    bot.send_message(message.chat.id, 'Введена неверная комманда!', reply_markup=markup1)


@bot.message_handler(func=lambda x: x.chat.type == 'private')
def all_other_messages_no_rights(message):
    bot.send_message(message.chat.id, 'Извините, у вас нет прав!')

bot.infinity_polling()
