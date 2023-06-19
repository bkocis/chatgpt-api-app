import logging
import gradio as gr
from pathlib import Path
from typing import List, Optional, Tuple
from queue import Empty, Queue
from threading import Thread

# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.prompts import HumanMessagePromptTemplate
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from callback import QueueCallback

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    format="[%(asctime)s %(levelname)s]: %(message)s", level=logging.INFO
)

ChatHistory = List[str]


def message_handler(
    chat: Optional[ChatOpenAI],
    message: str,
    chatbot_messages: ChatHistory,
    messages: List[BaseMessage]
) -> Tuple[ChatOpenAI, str, ChatHistory, List[BaseMessage]]:
    if chat is None:
        # in the queue we will store our streamed tokens
        queue = Queue()
        # let's create our default chat
        chat = ChatOpenAI(
            model_name=MODELS_NAMES[0],
            temperature=DEFAULT_TEMPERATURE,
            streaming=True,
            callbacks=([QueueCallback(queue)]),
        )
    else:
        # hacky way to get the queue back
        queue = chat.callbacks[0].queue

    job_done = object()

    logging.info("asking question to GPT")
    messages.append(HumanMessage(content=message))
    chatbot_messages.append((message, ""))
    # this is a little wrapper we need cuz we have to add the job_done

    def task():
        chat(messages)
        queue.put(job_done)

    t = Thread(target=task)
    t.start()
    # this will hold the content as we generate
    content = ""
    # now, we read the next_token from queue and do what it has to be done
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
    return chat, "", chatbot_messages, messages


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
    # don't forget to nuke our queue
    chat.callbacks[0].queue.empty()
    return chat, *on_clear_click()


def load_style():
    with open("prompts/prompt_instructions_helper.md") as f:
        help_page_header = f.read()

    with open("style/css_string.txt") as f:
        css_string = f.read()

    with open("style/page_header.txt") as f:
        page_subtitle = f.read()
        return help_page_header, css_string, page_subtitle


def main(system_message, human_message_prompt_template):
    help_page_header, css_string, page_subtitle = load_style()
    with gr.Blocks(
            title="ChatGPTapp",
            theme=gr.themes.Soft(text_size="sm"),
            css=css_string,
            ) \
            as demo:
        # here we keep our state so multiple user can use the app at the same time!
        messages = gr.State([system_message])
        # same thing for the chat, we want one chat per use so callbacks are unique I guess
        chat = gr.State(None)

        with gr.Column(elem_id="col_container"):
            gr.Markdown(page_subtitle, elem_id="centerImage")
            with gr.Tab("ChatGPT"):
                chatbot = gr.Chatbot(show_label=False)
                with gr.Row():
                    message = gr.Textbox(show_label=False, placeholder="write input here")
                    message.submit(
                        message_handler,
                        [chat, message, chatbot, messages],
                        [chat, message, chatbot, messages],
                        queue=True,
                    )
            with gr.Tab("Cheatsheet"):
                gr.Markdown(help_page_header)
            with gr.Tab("Settings"):
                with gr.Column():
                    model_name = gr.Dropdown(
                        choices=MODELS_NAMES, value=MODELS_NAMES[0], label="model"
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
                        [chat, message, chatbot, messages],
                    )
                    clear = gr.Button("Reset chat")
                    clear.click(
                        on_clear_click,
                        [],
                        [message, chatbot, messages],
                        queue=False,
                    )
    demo.queue()
    demo.launch(
        # debug=False,
        # share=True,
        server_name="0.0.0.0",
        server_port=8083,
        root_path="/openai-chatgpt-gradio-app")


if __name__ == "__main__":
    MODELS_NAMES = ["gpt-3.5-turbo"]
    DEFAULT_TEMPERATURE = 0.6

    # load up our system prompt
    system_message = SystemMessage(content=Path("prompts/system.prompt").read_text())
    # for the human, we will just inject the text
    human_message_prompt_template = HumanMessagePromptTemplate.from_template("{text}")
    main(system_message, human_message_prompt_template)
