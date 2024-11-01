from aiogram import Bot, Dispatcher, types
import asyncio
import requests
import sqlite3

API_TOKEN = '7410087255:AAHBI-9sYuWXGtZH_MRipYbl2nDini54FxU'
API_BASE_URL = "http://192.168.101.134:8000"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def initialize_db():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER UNIQUE,
            tgusername TEXT,
            token TEXT,
            conversationids TEXT,
            current_conversation TEXT
        )
    ''')
    conn.commit()
    conn.close()

initialize_db()

def generate_token(user_id, username):
    user_data = {"username": f"{username}", "password": f"{user_id}"}
    response = requests.post(f"{API_BASE_URL}/token", data=user_data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("Login successful, token:", token)
        return token
    else:
        try:
            error_details = response.json()
        except Exception as e:
            error_details = response.text
        print("Failed to login:", error_details)

def register_user(user_id, username):
    user_data = {
    "username": f"{username}",
    "password": f"{user_id}",
    "full_name": f"{username}",
    "email": f"{username}@tgbot.api"
    }
    response = requests.post(f"{API_BASE_URL}/users/", json=user_data)
    if response.status_code == 200:
        print("User registered successfully")
    else:
        try:
            error_details = response.json()
        except Exception as e:
            error_details = response.text
        print("Failed to register user:", error_details)
    token = generate_token(user_id, username)
    return token

# Add or update user in the database
def add_or_update_user(user_id, username, token):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (userid, tgusername, token, conversationids, current_conversation)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(userid) DO UPDATE SET
        tgusername=excluded.tgusername,
        token=excluded.token,
        conversationids=excluded.conversationids,
        current_conversation=excluded.current_conversation
    ''', (user_id, username, token, "", ""))
    conn.commit()
    conn.close()
"""
@dp.message(commands=['start', 'help'])
async def start(message: types.Message):
    sender = await message.from_user
    user_id = sender.id
    username = sender.username
    token = register_user(user_id, username)
    if token:
        add_or_update_user(user_id, username, token)
        await message.reply(f'Hi {username}! You was sucessfully registered✅')
    else:
        await message.reply('❌Failed to register(maybe you already register💢)')
"""
        
def create_conversation(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE_URL}/create-conversation", headers=headers)
    if response.status_code == 200:
        conversation_id = response.json().get("conversation_id")
        return conversation_id
    else:
        try:
            error_details = response.json()
        except Exception as e:
            error_details = response.text

# Update conversation IDs for a user
def update_conversations(user_id, conversation_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT conversationids FROM users WHERE userid=?', (user_id,))
    result = cursor.fetchone()
    if result:
        conversation_ids = result[0]
        if conversation_ids:
            conversation_ids += f",{conversation_id}"
        else:
            conversation_ids = conversation_id
        cursor.execute('UPDATE users SET conversationids=? WHERE userid=?', (conversation_ids, user_id))
    conn.commit()
    conn.close()

def update_current_conversation(user_id, conversation_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET current_conversation=? WHERE userid=?', (conversation_id, user_id))
    conn.commit()
    conn.close()

@dp.message()
async def echo(message: types.Message):
    """
    This handler will be called when user sends any message
    """
    
    await message.reply(message.text)

@dp.business_connection()
async def connection(connection: types.BusinessConnection):
    print("test")
    print(connection.is_enabled)

@dp.business_message()
async def business_message(message : types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    message_text = message.text

    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT token, current_conversation FROM users WHERE userid=?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    

    if result:
        token, current_conversation = result
        headers = {"Authorization": f"Bearer {token}"}
        params = {'message': message_text, 'conversation_id': current_conversation}
        response = requests.post(f"{API_BASE_URL}/chat", params=params, headers=headers)
        if response.status_code == 200:
            bot_response = response.json().get("response")["content"]
        else:
            bot_response = "Error while processing chat, contact with owner!"
        await message.reply(f"{bot_response}")
    else:
        token = register_user(user_id, username)
        add_or_update_user(user_id, username, token)
        cid = create_conversation(token)
        update_conversations(user_id, cid)
        update_current_conversation(user_id, cid)

        headers = {"Authorization": f"Bearer {token}"}
        params = {'message': message_text, 'conversation_id': cid}
        response = requests.post(f"{API_BASE_URL}/chat", params=params, headers=headers)
        if response.status_code == 200:
            bot_response = response.json().get("response")["content"]
        else:
            bot_response = "Error while processing chat, contact with owner!"
        await message.reply(f"{bot_response}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())