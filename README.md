### Gradio app streaming prompt completion with OpenAI API

[![Python application](https://github.com/bkocis/gradio-apps/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/bkocis/gradio-apps/actions/workflows/python-app.yml)
----

## About

<img src="docs/images/chat_tab.png" width="400" />

Multiple tabs for accessing different models and settings

<img src="docs/images/settings_tab.png" width="400" />

## Some Features

- [LangChain `ChatOpenAI`](https://python.langchain.com/en/latest/modules/models/chat/integrations/openai.html)
- Streaming
- [State management](https://gradio.app/state-in-blocks/) so multiple users can use it
- UI with [Gradio](https://gradio.app/)
- types and comments

## Installation

Create a `.env` file with your OpenAI API Key

```bash
echo "OPENAI_API_KEY=<YOUR_API_KEY>" > .env
```

You `.env` should look like

```
OPENAI_API_KEY=<YOUR_KEY>
```

### Getting started

Virtual enviroment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
``` 

Running the application with gradio
```bash
cd chatgptApp
gradio main.py
```

### Docker 

```bash
docker build -t gradio-app .
docker run --rm -it -p 7860:7860 \
    -e GRADIO_SERVER_NAME=0.0.0.0 \
    -v $(pwd)/.env:/app/.env \
    gradio-app
```

```bash
docker build --build-arg -t gradio-app .
```

Deploy headless
```makefile
deploy_headless:
	docker build --tag=${app_name} --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} .
	docker run -dit -p ${port}:${port} ${app_name}
```

### Nginx 

```nginx
    location /openai-chatgpt-gradio-app/ {
        proxy_pass http://127.0.0.1:8083/;
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

```

Important setting to add to main.py:

```python
demo.launch(
    # debug=False,
    # share=True,
    server_name="0.0.0.0",
    server_port=8083,
    root_path="/openai-chatgpt-gradio-app")

```


Read more about deploying gradio apps to servers: 

https://gradio.app/running-gradio-on-your-web-server-with-nginx/

some issues encountered, with solution:

https://discuss.huggingface.co/t/deploy-gradio-app-on-my-own-server-machine-fails/41808

https://github.com/gradio-app/gradio/issues/1747


