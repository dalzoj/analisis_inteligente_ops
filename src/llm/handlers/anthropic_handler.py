import os
import anthropic
from src.llm.llm_base import LLMBase

class AnthropicHandler(LLMBase):
    
    def __init__(self, model_name, max_tokens, temperature):
        print('INFO: Initializing AnthropicHandler')
        
        self.model_name = model_name
        self.max_tokens = max_tokens
        self. temperature = temperature
        self.client = anthropic.AsyncAnthropic(api_key = os.getenv("ANTHROPIC_API_KEY"))

    async def basic_call(self, system_prompt, user_message):
        print('INFO: Basic Call Anthropic')

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

            return {
                "model_name": self.model_name,
                "tokens_in": response.usage.input_tokens,
                "tokens_out": response.usage.output_tokens,
                "answer": response.content[0].text,
            }

        except Exception as error:
            print(f"ERROR: {error}")
            raise error
        
    def history_call():
        pass