import os
import logging
import sqlite3
import gradio as gr
from pathlib import Path
from typing import List, Optional, Tuple
from queue import Empty, Queue
from threading import Thread
from langchain.chat_models import ChatOpenAI
from langchain.prompts import HumanMessagePromptTemplate
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from callback import QueueCallback


logging.basicConfig(
    format="[%(asctime)s %(levelname)s]: %(message)s", level=logging.INFO
)

ChatHistory = List[str]


def insert_into_db(message, content):
    c.execute("INSERT INTO chat_session_01 (question, answer) VALUES (?, ?)", (message, content))
    conn.commit()
    c.execute("select * from chat_session_01")
    logging.info(f"{c.fetchall()}")


def message_handler_4(
        chat: Optional[ChatOpenAI],
        message: str,
        chatbot_messages: ChatHistory,
        messages: List[BaseMessage]
) -> Tuple[ChatOpenAI, str, ChatHistory, List[BaseMessage]]:
    if chat is None:
        queue = Queue()
        chat = ChatOpenAI(
            model_name='gpt-4',
            temperature=DEFAULT_TEMPERATURE,
            streaming=True,
            callbacks=([QueueCallback(queue)]),
        )
    else:
        queue = chat.callbacks[0].queue

    job_done = object()

    logging.info("asking question to GPT")
    messages.append(HumanMessage(content=message))
    chatbot_messages.append((message, ""))

    def task():
        chat(messages)
        queue.put(job_done)

    t = Thread(target=task)
    t.start()
    content = ""
    while True:
        try:
            next_token = queue.get(True, timeout=1)
            if next_token is job_done:
                break
            content += next_token
            chatbot_messages[-1] = (message, content)
            yield chat, "", chatbot_messages, messages
        except Empty:
            continue
    messages.append(AIMessage(content=content))
    logging.debug(f"reply = {content}")
    logging.info("Done!")
    insert_into_db(message, content)
    return chat, "", chatbot_messages, messages


def message_handler_3p5(
        chat: Optional[ChatOpenAI],
        message: str,
        chatbot_messages: ChatHistory,
        messages: List[BaseMessage]
) -> Tuple[ChatOpenAI, str, ChatHistory, List[BaseMessage]]:
    if chat is None:
        queue = Queue()
        chat = ChatOpenAI(
            model_name='gpt-3.5-turbo',
            temperature=DEFAULT_TEMPERATURE,
            streaming=True,
            callbacks=([QueueCallback(queue)]),
        )
    else:
        queue = chat.callbacks[0].queue

    job_done = object()

    logging.info("asking question to GPT")
    messages.append(HumanMessage(content=message))
    chatbot_messages.append((message, ""))

    def task():
        chat(messages)
        queue.put(job_done)

    t = Thread(target=task)
    t.start()
    content = ""
    while True:
        try:
            next_token = queue.get(True, timeout=1)
            if next_token is job_done:
                break
            content += next_token
            chatbot_messages[-1] = (message, content)
            yield chat, "", chatbot_messages, messages
        except Empty:
            continue
    messages.append(AIMessage(content=content))
    logging.debug(f"reply = {content}")
    logging.info("Done!")
    insert_into_db(message, content)
    return chat, "", chatbot_messages, messages


def list_db_tab():
    """Returns data from an SQL query as a list of dicts."""
    select_query = "SELECT * FROM chat_session_01"
    con = sqlite3.connect(path_to_db)
    con.row_factory = sqlite3.Row
    query = con.execute(select_query).fetchall()
    unpacked = [{k: item[k] for k in item.keys()} for item in query]
    return unpacked


def list_db_tab_questions(select_query):
    """Returns data from an SQL query as a list of dicts."""
    con = sqlite3.connect(path_to_db)
    con.row_factory = sqlite3.Row
    query = con.execute(select_query).fetchall()
    unpacked = [{k: item[k] for k in item.keys()} for item in query]
    question_list = []
    answer_list = []
    # formatted_output = [f"Question: {item['question']}\nAnswer: {item['answer']}\n" for item in unpacked]
    for item in unpacked:
        question_list.append(item['question'])
        answer_list.append(item.get('answer', ''))
    # return [[str(question_list[0]), str(answer_list[0])]]
    return [[str("\n".join(question_list)), str("\n".join(answer_list))]]


def on_clear_click() -> Tuple[str, List, List]:
    return "", [], []


def on_apply_settings_click(model_name: str, temperature: float):
    logging.info(
        f"Applying settings: model_name={model_name}, temperature={temperature}"
    )
    chat = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        streaming=True,
        callbacks=[QueueCallback(Queue())],
    )
    # clear queue - reset the conversation
    chat.callbacks[0].queue.empty()
    return chat, *on_clear_click()


def load_style():
    with open("prompts/prompt_instructions_helper.md") as f:
        help_page_header = f.read()

    with open("style/page_header.txt") as f:
        page_subtitle = f.read()
        return help_page_header, page_subtitle


def main(human_message_prompt_template):
    help_page_header, page_subtitle = load_style()
    with gr.Blocks(
            title="ChatGPTapp",
            theme=gr.themes.Soft(text_size="sm"),
            css="style/css_string.css"
            ) as demo:
        messages_gen = gr.State([SystemMessage(content=Path("prompts/system.prompt.general").read_text())])
        messages_py = gr.State([SystemMessage(content=Path("prompts/system.prompt.python").read_text())])
        messages_4pyanalyzer = gr.State([SystemMessage(content=Path("prompts/system.prompt.python-analyser").read_text())])
        kwargs = {
            "show_label": False,
            "height": 750
        }
        chat = gr.State(None)

        with gr.Column(elem_id="col_container"):
            gr.Markdown(page_subtitle, elem_id="centerImage")
            with gr.Tab("ChatGPT4-py"):
                chatbot = gr.Chatbot(**kwargs)
                with gr.Row():
                    message = gr.Textbox(show_label=False, placeholder="write question here")
                    message.submit(
                        message_handler_4,
                        [chat, message, chatbot, messages_py],
                        [chat, message, chatbot, messages_py],
                        queue=True,
                    )

            with gr.Tab("ChatGPT4-pyAnalyzer"):
                chatbot = gr.Chatbot(**kwargs)
                with gr.Row():
                    message = gr.Textbox(show_label=False, placeholder="write question here")
                    message.submit(
                        message_handler_4,
                        [chat, message, chatbot, messages_4pyanalyzer],
                        [chat, message, chatbot, messages_4pyanalyzer],
                        queue=True,
                    )

            with gr.Tab("ChatGPT3.5"):
                chatbot = gr.Chatbot(**kwargs)
                with gr.Row():
                    message = gr.Textbox(show_label=False, placeholder="write question here")
                    message.submit(
                        message_handler_3p5,
                        [chat, message, chatbot, messages_gen],
                        [chat, message, chatbot, messages_gen],
                        queue=True,
                    )

            with gr.Tab("Query_History"):
                query_chatbot = gr.Chatbot(**kwargs)
                query = gr.Textbox(show_label=False,
                                   value="select * from chat_session_01 order by id desc limit 1 offset 0",
                                   show_copy_button=True)
                query.submit(
                    list_db_tab_questions,
                    [query],
                    query_chatbot
                )

            with gr.Tab("Cheatsheet"):
                gr.Markdown(help_page_header)
            with gr.Tab("Settings"):
                with gr.Column():
                    model_name = gr.Dropdown(
                        choices=MODELS, value=MODELS[1], label="model"
                    )
                    temperature = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=DEFAULT_TEMPERATURE,
                        step=0.1,
                        label="temperature",
                        interactive=True,
                    )
                    apply_settings = gr.Button("Apply")
                    apply_settings.click(
                        on_apply_settings_click,
                        [model_name, temperature],
                        [chat, message, chatbot, messages_gen],
                    )
                    clear = gr.Button("Reset chat")
                    clear.click(
                        on_clear_click,
                        [],
                        [message, chatbot, messages_gen],
                        queue=False,
                    )
    demo.queue()
    demo.launch(
        # debug=False,
        # share=True,
        server_name="0.0.0.0",
        server_port=8083,
        # root_path="/openai-chatgpt-gradio-app")
    )


if __name__ == "__main__":
    MODELS = ["gpt-3.5-turbo", "gpt-4"]
    DEFAULT_TEMPERATURE = 0.1
    DB_NAME = "chat_sessions.db"
    path_to_db = os.path.join(os.environ["PATH_TO_DB"], DB_NAME)

    conn = sqlite3.connect(path_to_db, check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS chat_session_01 (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)")
    conn.commit()

    # load up our system prompt
    human_message_prompt_template = HumanMessagePromptTemplate.from_template("{text}")
    main(human_message_prompt_template)
