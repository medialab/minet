# Variables
SOURCE = minet

# Functions
define clean
	rm -rf *.egg-info .pytest_cache build dist
	find . -name "*.pyc" | xargs rm -f
	find . -name "*.pyo" | xargs rm -f
	find . -name __pycache__ | xargs rm -rf
	find . -name .ipynb_checkpoints | xargs rm -rf
	rm -f *.spec
endef

# Targets
all: lint test
compile: clean pyinstaller
test: unit
publish: clean lint test upload
	$(call clean)

clean:
	$(call clean)

deps:
	pip3 install -U pip
	pip3 install -r requirements.txt

lint:
	@echo Searching for unused imports...
	importchecker $(SOURCE) | grep -v __init__ | grep -v idna || true
	importchecker test | grep -v __init__ || true
	@echo

format:
	@echo Formatting source code using black
	black $(SOURCE) ftest hooks scripts test
	@echo

ua:
	@echo Upgrading internals...
	python -m minet.cli ua update
	black minet/user_agents/data.py
	@echo

readme:
	python -m scripts.generate_readme > docs/cli.md

unit:
	@echo Running unit tests...
	pytest -svvv
	@echo

upload:
	python setup.py sdist bdist_wheel
	twine upload dist/*

pyinstaller: clean
	pyinstaller \
		--additional-hooks-dir=./hooks \
		--name minet \
		--clean \
		--exclude-module IPython \
		--exclude-module ipykernel \
		--exclude-module ipywidgets \
		--exclude-module jedi \
		--exclude-module jupyter \
		--exclude-module jupyter_client \
		--exclude-module jupyter_core \
		--exclude-module jupyter-server \
		--exclude-module jupyterlab \
		--exclude-module jupyterlab_server \
		--exclude-module jupyterlab-widgets \
		minet/cli/__main__.py
