from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler

from uform.gen_model import VLMForCausalLM, VLMProcessor
import PIL
import torch

import os
import sys
from .conservation import Conservation

sys.path.append('../Llama')

from config import get_config
from Modes import terminal
from Modes.webui import webui 
from Modes.api import api 

mode = "terminal"

class Image:
    def loaduform():
        #device = torch.device("cuda")
        
        model = VLMForCausalLM.from_pretrained("unum-cloud/uform-gen")
        processor = VLMProcessor.from_pretrained("unum-cloud/uform-gen")
        
        #model.to(device)
        return model, processor

    def texttoimage(model : VLMForCausalLM, processor : VLMProcessor):
        prompt = "[cap] Narrate the contents of the image with precision"
        image = PIL.Image.open("test.jpg")

        inputs = processor(texts=[prompt], images=[image], return_tensors="pt")

        #inputs.to('cuda')

        with torch.inference_mode():
            output = model.generate(
                **inputs,
                do_sample=False,
                use_cache=True,
                max_new_tokens=2048,
                eos_token_id=32001,
                pad_token_id=processor.tokenizer.pad_token_id
                
            )

        prompt_len = inputs["input_ids"].shape[1]
        decoded_text = processor.batch_decode(output[:, prompt_len:])[0]
        decoded_text = "<img/>" + decoded_text + "</img>"
        return 

class ChatLLama:
    def chatcompletionformat(role , message):
        return {"role": f"{role}", "content": f"{message}"}
    
    def msggen(llama : Llama, history, message):
        messages = history
        messages.append(message)
        
        response =  llama.create_chat_completion(
            messages=messages,
            stream=False
        )
        
        return response["choices"][0]["message"]

    def loadllama():
        print("[+]Loading text model(Llama3 8b)...")
        llama = Llama(model_path = './Models/LLama(Text)/llama-8b-u.gguf',
                    n_gpu_layers=-1,
                    n_ctx=0,
                    chat_format="llama-3")
        llama.verbose = False
        os.system("cls")
        print("[+]Model loaded!")
        return llama
    
    """
    def loadllava():
        print("[+]Loading image model(Llavi-phi 3 int4)...")
        chat_handler = Llava15ChatHandler(clip_model_path="./Models/LLaVa(Image)/llava-phi-3-mini-mmproj-f16.gguf")
        llava = Llama(model_path = './Models/LLaVa(Image)/llava-phi-3-mini-int4.gguf',
                    n_gpu_layers=-1,
                    n_ctx=0,
                    chat_handler=chat_handler)
        llava.verbose = False
        os.system("cls")
        print("[+]Model loaded!")
        return llava
    """

    
    def chatllama(llama : Llama):
        conservation = Conservation()
        
        current_config = get_config()
        
        
        default_history = current_config.DEFAULT_HISTORY
        mode = current_config.MODE
        image = current_config.IMAGE
        
        history = default_history
        
        if mode == "terminal":
            terminal.Terminal(llama, history, conservation)
        elif mode == 'ui':
            webui.WebUI(llama, history, conservation)
        elif mode == 'api':
            print("Api")
            api.api(llama)
        elif mode == 'discord':
            return