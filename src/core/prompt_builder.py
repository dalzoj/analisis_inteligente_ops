import os
import configparser

config = configparser.ConfigParser()
config.read("config/config.cfg")


def _load_prompt_file(filename):
    prompts_dir = config["paths"]["prompts"]
    path = os.path.join(prompts_dir, f"{filename}.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
 

def get_chat_prompt():
    prompt_name = config["prompts"]["chat"]
    return _load_prompt_file(prompt_name)


def get_code_gen_prompt():
    prompt_name = config["prompts"]["code_gen"]
    return _load_prompt_file(prompt_name)


def get_code_insights_prompt():
    prompt_name = config["prompts"]["insights"]
    return _load_prompt_file(prompt_name)