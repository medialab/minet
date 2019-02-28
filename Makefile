# Variables
SOURCE = minet

# Commands
all: lint test
test: unit
publish: test upload clean # TODO: lint is missing

clean:
	rm -rf *.egg-info .pytest_cache build dist
	find . -name "*.pyc" | xargs rm
	rm -rf ftest/content
	rm *.spec

deps:
	find ./requirements -name "*.txt" | xargs -n 1 pip install -r

lint:
	@echo Linting source code using pep8...
	pycodestyle --ignore E501,E722 $(SOURCE) test
	@echo

unit:
	@echo Running unit tests...
	pytest -s
	@echo

upload:
	python setup.py sdist bdist_wheel
	twine upload dist/*
