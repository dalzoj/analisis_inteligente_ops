import os
import anthropic
from src.llm.llm_base import LLMBase

class AnthropicHandler(LLMBase):
    
    def __init__(self, model_name, max_tokens, temperature):
        print('INFO: Creating AnthropicHandler')
        
        self.model_name = model_name
        self.max_tokens = max_tokens
        self. temperature = temperature
        self.client = anthropic.AsyncAnthropic(api_key = os.getenv("ANTHROPIC_API_KEY"))

    async def basic_call(self, system_prompt, user_message):
        print('INFO: Basic Call Anthropic')
        print('system_prompt',system_prompt)
        print('user_message',user_message)
        print('self.max_tokens',self.max_tokens)
        print('self.temperature',self.temperature)


        try:

            response = await self.client.messages.create(
                model = self.model_name,
                max_tokens = self.max_tokens,
                temperature = self.temperature,
                system = system_prompt,
                messages = [{
                    "role": "user",
                    "content": user_message
                }]
            )
            print('-------------------------------------------')
            print(response)
            print('-------------------------------------------')
            print(response.content[0].text)
            print('-------------------------------------------')

            return response.content[0].text

        except Exception as error:
            print(f"ERROR: {error}")
            raise error
        
    def history_call():
        pass