FROM python:3.10-slim-bullseye

ARG OPENAI_API_KEY
ENV OPENAI_API_KEY $OPENAI_API_KEY
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH /opt/chatgptApp

RUN mkdir /opt/chatgptApp

COPY chatgptApp /opt/chatgptApp
COPY ./requirements.txt /opt/chatgptApp/requirements.txt

RUN apt-get update && \
    apt-get install python3-dev -y && \
    pip install --upgrade pip && \
    pip install --no-cache-dir setuptools wheel && \
    pip install --no-cache-dir -r /opt/chatgptApp/requirements.txt

WORKDIR /opt/chatgptApp
EXPOSE 8083

CMD ["python", "main.py"]