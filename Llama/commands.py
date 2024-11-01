import os
import subprocess

class Commands:
    def search(message):
        output = ""
        print("search")
        return output

    def save_file(name, content, description):
        print("save_file")

    def read_file(name):
        content = ""
        print("read_file")
        return content

    def type_msg(user, content):
        send = True
        print("type_msg")
        return send

    def cmd(command):
        returned_text = subprocess.check_output(command, shell=True, universal_newlines=True)
        print("cmd")
        return returned_text

    def 