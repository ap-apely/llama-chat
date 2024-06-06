from llama_cpp import Llama
import sys
import os
import threading
import time
from Llama.llama import ChatLLama



def main():
    try:
        llama = ChatLLama.loadllama()
        ChatLLama.chatllama(llama)
    except Exception as e:
        print(e)
        raise e
    
    
if __name__ == '__main__':
    print('[+]Starting...') 
    main()

    
