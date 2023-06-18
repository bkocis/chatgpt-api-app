port=8083
app_name=openai-chatgpt-gradio-app

build_test:
	flake8 --config=.flake8
	@if [ $$? -eq 0 ]; then \
		echo "Linting passed"; \
	else \
		echo "Linting failed"; \
	fi

	pytest
	@if [ $$? -eq 0 ]; then \
		echo "Tests passed"; \
	else \
		echo "Tests failed"; \
	fi
	docker build --tag=${app_name} --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} .
	docker run -p ${port}:${port} ${app_name}
build_run:
	docker build --tag=${app_name} --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} .
	docker run -p ${port}:${port} ${app_name}
run_local:
	docker run -p ${port}:${port} ${app_name}
run_app:
	gradio app.py
deploy_headless:
	docker build --tag=${app_name} --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} .
	docker run -dit -p ${port}:${port} ${app_name}
git_push:
	flake8
	git add .
	git commit -m "update run via makefile"
	git push
