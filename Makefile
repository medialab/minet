# Variables
SOURCE = minet
PEP8_IGNORE = E501,E722,E741,W503,W504

# Functions
define clean
	rm -rf *.egg-info .pytest_cache build dist
	find . -name "*.pyc" | xargs rm -f
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
	@echo Linting source code using pep8...
	pycodestyle --ignore $(PEP8_IGNORE) $(SOURCE) test hooks
	@echo
	@echo Searching for unused imports...
	importchecker $(SOURCE) | grep -v __init__ || true
	@echo

format:
	@echo Formatting source code using autopep8
	autopep8 --in-place minet/**/*.py --ignore $(PEP8_IGNORE)
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
		minet/cli/__main__.py
