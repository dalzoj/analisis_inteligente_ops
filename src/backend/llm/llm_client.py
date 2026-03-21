from src.backend.llm.llm_factory import create_handler

_handler = create_handler()
 
async def basic_call(system_prompt, user_message):
    return await _handler.basic_call(system_prompt, user_message)

async def history_call(system_prompt, user_message):
    return await _handler.history_call(system_prompt, user_message)