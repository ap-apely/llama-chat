import sqlite3
import json
import re

class Conservation:
    def __init__(self, db_name='conversations.db'):
        self.db_name = db_name
        self.__create_table()
    
    def __create_table(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    # Serialize data
    @staticmethod
    def __serialize(data):
        return json.dumps(data)

    # Deserialize data
    @staticmethod
    def __deserialize(data):
        return json.loads(data)

    # Extract the first sentence
    @staticmethod
    def __extract_first_sentence(text):
        sentences = re.split(r'(?<=[.!?]) +', text)
        return sentences[0] if sentences else ""

    # Save conversation to the database
    def save_conversation(self, conversation):
        serialized_data = self.__serialize(conversation)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO conversations (data) VALUES (?)", (serialized_data,))
        conn.commit()
        conn.close()

    # Load conversation from the database
    def load_conversation(self, conversation_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM conversations WHERE id=?", (conversation_id,))
        serialized_data = cursor.fetchone()
        conn.close()
        if serialized_data:
            return self.__deserialize(serialized_data[0])
        else:
            return None

    # Display all conversations
    def display_conversations(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, data FROM conversations")
        conversations = cursor.fetchall()
        conn.close()
        
        if not conversations:
            print("No conversations found.")
            return
        
        print("Available Conversations:")
        for conversation_id, serialized_data in conversations:
            conversation = self.__deserialize(serialized_data)
            last_assistant_message = next((msg["content"] for msg in reversed(conversation) if msg["role"] == "assistant"), "")
            first_sentence = self.__extract_first_sentence(last_assistant_message)
            print(f"{conversation_id}: {first_sentence}")
 
    def delete_conversation(self, conversation_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE id=?", (conversation_id,))
        conn.commit()
        conn.close()
        print(f"Conversation with ID {conversation_id} deleted successfully.")