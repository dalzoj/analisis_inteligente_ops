import configparser
import pandas as pd
from src.backend.llm import llm_client
from src.backend.core import prompt_builder, code_executor

config = configparser.ConfigParser()
config.read("config/config.cfg")

DATA_FLAG = "DATA"
CHAT_FLAG = "CHAT"


async def _classify_question(question):
    print('INFO: chat_service -> _classify_question')
    
    classifier_prompt = prompt_builder.get_classifier_prompt()
    result = await llm_client.basic_call(classifier_prompt, question)
    return result


async def _generate_code(question):
    print('INFO: chat_service -> _generate_code')
    
    code_gen_prompt = prompt_builder.get_code_gen_prompt()
    return await llm_client.basic_call(code_gen_prompt, question)


def _format_to_string(result):
    print('INFO: chat_service -> _format_to_string')

    if isinstance(result, pd.DataFrame):
        return result.to_string(index=False)
    return str(result)


async def _interpret_result(question, result_text):
    print('INFO: chat_service -> _interpret_result')

    chat_prompt = prompt_builder.get_chat_prompt()

    new_question = (
        f"Yo pregunté: {question}\n\n"
        f"Los resultados fueron:\n"
        f"{result_text}\n\n"
        f"Limpia y presenta la respuesta en formato Markdown"
    )

    return await llm_client.basic_call(chat_prompt, new_question)


async def get_basic_metrics_ops_answer(question):
    print('INFO: chat_service -> get_basic_metrics_ops_answer')
    
    python_code_answer = await _generate_code(question)

    response = {
        "answer": python_code_answer['answer'],
        "model_name": python_code_answer['model_name'],
        "tokens_in": python_code_answer['tokens_in'],
        "tokens_out": python_code_answer['tokens_out'],
    }

    success, result, error = code_executor.run(response['answer'])

    if success:
        result_text = _format_to_string(result)
        interpret_answer = await _interpret_result(question, result_text) 

        response['answer'] = interpret_answer['answer']
        response['tokens_in'] += interpret_answer['tokens_in']
        response['tokens_out'] += interpret_answer['tokens_out']
        
        return response


async def get_history_metrics_ops_answer(question, history):
    print('INFO: chat_service -> get_history_metrics_ops_answer')

    memory_window = config.getint("llm", "memory_window")

    classification = await _classify_question(question)

    response = {
        "answer": classification['answer'],
        "model_name": classification['model_name'],
        "tokens_in": classification['tokens_in'],
        "tokens_out": classification['tokens_out'],
    }

    chat_prompt = prompt_builder.get_chat_prompt()
    recent_history = history[-(memory_window * 2):]

    if CHAT_FLAG in classification['answer'].strip():
        messages = recent_history + [{"role": "user", "content": question}]
        direct_answer = await llm_client.history_call(chat_prompt, messages)

        response['answer'] = direct_answer['answer']
        response['tokens_in'] += direct_answer['tokens_in']
        response['tokens_out'] += direct_answer['tokens_out']

        return response

    python_code_answer = await _generate_code(question)

    response['tokens_in'] += python_code_answer['tokens_in']
    response['tokens_out'] += python_code_answer['tokens_out']

    success, result, error = code_executor.run(python_code_answer['answer'])

    if success:
        result_text = _format_to_string(result)

        new_message = (
            f"Yo pregunté: {question}\n\n"
            f"Los resultados fueron:\n"
            f"{result_text}\n\n"
            f"Limpia y presenta la respuesta en formato Markdown"
        )

        messages = recent_history + [{"role": "user", "content": new_message}]
        interpret_answer = await llm_client.history_call(chat_prompt, messages)

        response['answer'] = interpret_answer['answer']
        response['tokens_in'] += interpret_answer['tokens_in']
        response['tokens_out'] += interpret_answer['tokens_out']

        return response