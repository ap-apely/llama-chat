from Llama.conservation import Conservation
from llama_cpp import Llama

import sys

sys.path.append('../Llama')



def Terminal(llama : Llama, default_history, conservation : Conservation):
    
    from Llama.llama import ChatLLama
    from Llama.conservation import Conservation
    
    history = default_history
    
    while True:
        """
                    if kb.is_pressed("ctrl+i"):
                        multi_line = True
                        input("🐢 Your multi line message (Ctrl+i to stop input): ")
                        user_message = ""
                        while multi_line == True:
                            user_message += input() + '\n'
                            if kb.is_pressed("ctrl+i"):
                                multi_line = False
                                
                        l_message = ChatLLama.msggen(llama, history, ChatLLama.chatcompletionformat("user", user_message))
                        l_message_text = l_message["content"]
                        print(f"🦙 Llama message: {l_message_text}")
                        
                        history.append(ChatLLama.chatcompletionformat("assistant", l_message_text))
        """
        if True == False : break #its for multi line input 3>>>
                    
        else:
            user_message = input("🐢 Your message (!type h for help): ")
                        
            conservationid = 0
                        
            match user_message:
                case 'exit':
                    print("[!]Exit")
                    conservation.save_conversation(history)
                    sys.exit()
                case 'h':
                    help = """[!]Help
                                d - display all conservations
                                l - load conservation
                                s - save conservation
                                n - new conservation
                                del - delete conservation
                            """
                    print(help)
                case 'd':
                    conservation.display_conversations()
                case 'l':
                    conversation_id_to_load = int(input("Enter the conversation ID to load: "))
                    conservationid = conversation_id_to_load
                    loaded_conversation = conservation.load_conversation(conversation_id_to_load)
                    if loaded_conversation:
                        print("Conversation Loaded Successfully.")
                        history = loaded_conversation
                                    
                    else:
                        print("Conversation not found.")
                case 's':
                    conservation.save_conversation(history)
                    print("Conversation Saved Successfully.")
                case 'n':
                    history = default_history   
                case 'del':
                    conversation_id_to_delete = int(input("Enter the conversation ID to delete: "))
                    conservation.delete_conversation(conversation_id_to_delete)    
                                
                case _:
                    l_message = ChatLLama.msggen(llama, history, ChatLLama.chatcompletionformat("user", user_message))
                    l_message_text = l_message["content"]
                    print(f"🦙 Llama message: {l_message_text}")
                                
                    history.append(ChatLLama.chatcompletionformat("assistant", l_message_text))    