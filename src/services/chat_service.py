from src.prompt_builder import get_chat_prompt
from src.llm import llm_client

chat_prompt = get_chat_prompt()

async def get_basic_answer(question):
    return await llm_client.basic_call(chat_prompt, question)