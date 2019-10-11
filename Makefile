# Variables
SOURCE = minet

# Functions
define clean
	rm -rf *.egg-info .pytest_cache build dist
	find . -name "*.pyc" | xargs rm -f
	find . -name __pycache__ | xargs rm -rf
	rm -rf ftest/content
	rm -f *.spec
endef

# Commands
all: lint test
compile: clean pyinstaller
test: unit
publish: clean lint test upload
	$(call clean)

clean:
	$(call clean)

pyinstaller:
	pyinstaller minet/cli/__main__.py \
		-n minet \
		--hidden-import lxml \
		--hidden-import lxml.etree \
		--hidden-import sklearn.neighbors.typedefs \
		--hidden-import sklearn.neighbors.quad_tree \
		--hidden-import sklearn.tree._utils \
		--hidden-import scipy.ndimage \
		--onefile \
		--clean

deps:
	find ./requirements -name "*.txt" | xargs -n 1 pip install -r

lint:
	@echo Linting source code using pep8...
	pycodestyle --ignore E501,E722,E741,W503,W504 $(SOURCE) test
	@echo
	@echo Searching for unused imports...
	importchecker $(SOURCE) | grep -v __init__ | grep -v dragnet || true
	@echo

readme:
	python generate_readme.py > README.md

unit:
	@echo Running unit tests...
	pytest -svvv
	@echo

upload:
	python setup.py sdist bdist_wheel
	twine upload dist/*
