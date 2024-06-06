from telethon import TelegramClient, events, Button
import requests
import sqlite3
import json

# Initialize the database
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

# API base URL and token (replace with your actual values)
API_BASE_URL = "http://192.168.101.190:8000"
API_ID = '25488122'
API_HASH = '39cb1cbc7783e7a1a3b32e339254ca43'
BOT_TOKEN = '7109116896:AAHU7XlSqRES0xL7l_z4Pw7UejPHxShU954'

# Initialize the client
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Generate token (dummy implementation for example purposes)

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

# Handler for the /start command
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    user_id = sender.id
    username = sender.username
    token = register_user(user_id, username)
    if token:
        add_or_update_user(user_id, username, token)
        await event.respond(f'Hi {username}! You was sucessfully registered✅')
        buttons = [
            [Button.inline("🌼New Conversation", data="menu_newconv")],
            [Button.inline("🌺All Conversations", data="menu_allconv")]
        ]
        await event.respond("Choose an option:", buttons=buttons)   
    else:
        await event.respond('❌Failed to register(maybe you already register💢)')
 
    raise events.StopPropagation

# Create a new conversation
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

# Handler for the /newconversation command
@client.on(events.NewMessage(pattern='/newconversation'))
async def new_conversation(event):
    user_id = event.sender_id
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT token FROM users WHERE userid=?', (user_id,))
    result = cursor.fetchone()
    if result:
        token = result[0]
        conversation_id = create_conversation(token)
        if conversation_id:
            update_current_conversation(user_id, conversation_id)
            update_conversations(user_id, conversation_id)
            await event.respond(f'✅New conversation created with ID: {conversation_id}')
        else:
            await event.respond('❌Failed to create a new conversation.')
    conn.close()
    raise events.StopPropagation

# Handler for the /allconversations command
@client.on(events.NewMessage(pattern='/allconversations'))
async def all_conversations(event):
    user_id = event.sender_id
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT conversationids FROM users WHERE userid=?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        conversation_ids = result[0].split(',')
        buttons = [Button.inline(f"🍃Conversation {conv_id}", data=f"conv_{conv_id}") for conv_id in conversation_ids]
        await event.respond('🌺Here are your conversations:', buttons=buttons)
    else:
        await event.respond('🥀You have no conversations.')

@client.on(events.CallbackQuery(pattern=b'conv_'))
async def callback_query_handler(event):
    selected_conversation = event.data.decode('utf-8')[5:]
    user_id = event.sender_id
    update_current_conversation(user_id, selected_conversation)
    await event.respond(f'🌼Selected conversation ID: {selected_conversation}')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/menu'))
async def menu(event):
    buttons = [
        [Button.inline("New Conversation", data="menu_newconv")],
        [Button.inline("All Conversations", data="menu_allconv")]
    ]
    await event.respond("Choose an option:", buttons=buttons)

# Handler for menu button presses
@client.on(events.CallbackQuery(pattern=b'menu_'))
async def menu_handler(event):
    data = event.data.decode('utf-8')
    if data == "menu_newconv":
        await new_conversation(event)
    elif data == "menu_allconv":
        await all_conversations(event)

# Handler for incoming messages to chat
@client.on(events.NewMessage)
async def chat(event):
    user_id = event.sender_id
    message_text = event.message.message

    # Skip commands
    if message_text.startswith('/'):
        return

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
        await event.respond(f"{bot_response}")

def main():
    client.start()
    client.run_until_disconnected()

if __name__ == '__main__':
    main()
