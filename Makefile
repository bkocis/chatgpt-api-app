PORT=8083
APP_NAME=openai-chatgpt-gradio-app
VOLUME_NAME=chat-sqlite3-volume-2
DB_PATH_ON_HOST=$(shell pwd)/resources/chat_history

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
	$(MAKE) build_run

build_run:
	docker build --tag=${APP_NAME} --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} .
	# docker run -v ${VOLUME_NAME}:/opt/app -p ${PORT}:${PORT} ${APP_NAME}
	docker run -it -v ${DB_PATH_ON_HOST}:/opt/resources -p ${PORT}:${PORT} -e PATH_TO_DB="/opt/resources" ${APP_NAME}
run_local:
	docker run -v ${VOLUME_NAME}:/opt/app -p ${PORT}:${PORT} ${APP_NAME}

create_volume:
	docker volume create ${VOLUME_NAME}

check_volume:
	docker volume ls
	docker volume inspect ${VOLUME_NAME}
	docker run -it --rm --volume ${VOLUME_NAME}:/opt/app alpine ls -ltr /opt/app

run_app:
	python main.py
deploy_headless:
	docker build --tag=${APP_NAME} --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} .
	# docker run -dit -v ${VOLUME_NAME}:/opt/app -p ${PORT}:${PORT} ${APP_NAME}
	docker run --name chatgpt_app -dit -v ${DB_PATH_ON_HOST}:/opt/resources -p ${PORT}:${PORT} -e PATH_TO_DB="/opt/resources" ${APP_NAME}
git_push:
	flake8
	git add .
	git commit -m "update run via makefile"
	git push
