import pandas as pd
from src.llm import llm_client
from src.core import prompt_builder, code_executor


async def _generate_code(question):
    code_gen_prompt = prompt_builder.get_code_gen_prompt()
    return await llm_client.basic_call(code_gen_prompt, question)


def _format_to_string(result) :
    if isinstance(result, pd.DataFrame):
        return result.to_string(index=False)
    return str(result)


async def _interpret_result(question, result_text):

    chat_prompt = prompt_builder.get_chat_prompt()

    new_question = (
        f"Yo pregunté: {question}\n\n"
        f"Los resultados fueron:\n"
        f"{result_text}\n\n"
        f"Limpia y presenta la respuesta en formato Markdown"
    )

    return await llm_client.basic_call(chat_prompt, new_question)


async def get_basic_metrics_ops_answer(question):
    
    python_code_answer = await _generate_code(question)

    response = {
        "answer": python_code_answer['answer'],
        "model": python_code_answer['model'],
        "tokens_in": python_code_answer['tokens_in'],
        "tokens_out": python_code_answer['tokens_out'],
    }

    success, result, error = code_executor.run(response['answer'])

    if success:
        result_text = _format_to_string(result)
        interpret_answer = await _interpret_result(question, result_text) 

        response['answer'] = interpret_answer['answer']
        response['tokens_in'] = response['tokens_in'] + interpret_answer['tokens_in']
        response['tokens_out'] = response['tokens_out'] + interpret_answer['tokens_out']
        
        return response