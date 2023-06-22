PORT=8083
APP_NAME=openai-chatgpt-gradio-app

build_test:
	flake8 --config=.flake8
	@if [ $$? -eq 0 ]; then \
		echo "Linting passed"; \
	else \
		echo "Linting failed"; \
	fi
	cd chatgptApp && \
	python -m pytest ../tests
	@if [ $$? -eq 0 ]; then \
		echo "Tests passed"; \
	else \
		echo "Tests failed"; \
	fi
	docker build --tag=${APP_NAME} --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} .
	docker run -p ${PORT}:${PORT} ${APP_NAME}
build_run:
	docker build --tag=${APP_NAME} --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} .
	docker run -p ${PORT}:${PORT} ${APP_NAME}
run_local:
	docker run -p ${PORT}:${PORT} ${APP_NAME}
run_app:
	python main.py
deploy_headless:
	docker build --tag=${APP_NAME} --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} .
	docker run -dit -p ${PORT}:${PORT} ${APP_NAME}
git_push:
	flake8
	git add .
	git commit -m "update run via makefile"
	git push
