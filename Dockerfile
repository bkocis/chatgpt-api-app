FROM python:3.10-slim-bullseye

ARG OPENAI_API_KEY
ENV OPENAI_API_KEY $OPENAI_API_KEY
ENV DEBIAN_FRONTEND=noninteractive
ENV GRADIO_SERVER_PORT=8083
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV PYTHONPATH /opt/gradio-chatgpt-app

RUN mkdir /opt/gradio-chatgpt-app

COPY gradio-chatgpt-app /opt/gradio-chatgpt-app
COPY ./requirements.txt /opt/gradio-chatgpt-app/requirements.txt

RUN apt-get update && \
    apt-get install python3-dev -y && \
    pip install --upgrade pip && \
    pip install --no-cache-dir setuptools wheel && \
    pip install --no-cache-dir -r /opt/gradio-chatgpt-app/requirements.txt

WORKDIR /opt/gradio-chatgpt-app
EXPOSE 8083

CMD ["gradio", "app.py"]
