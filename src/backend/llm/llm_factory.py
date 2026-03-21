
import configparser
from dotenv import load_dotenv
from src.backend.llm.handlers.anthropic_handler import AnthropicHandler

load_dotenv()

config = configparser.ConfigParser()
config.read("config/config.cfg")


def create_handler():
    print('INFO: llm_factory -> create_handler')

    resolved_provider = config['llm']['name']
    
    if resolved_provider == 'anthropic':
        
        model_name = config['llm_anthropic']['model_name']
        max_tokens  = config.getint('llm_anthropic', 'max_tokens')
        temperature = config.getfloat('llm_anthropic', 'temperature')
        
        return AnthropicHandler(
            model_name = model_name,
            max_tokens = max_tokens,
            temperature = temperature
        )

