# vim: set noet sw=4 ts=4 fileencoding=utf-8:

# Project-specific constants
NAME=memeoverflow

# Default target
all:
	@echo "make install - Install on local system"
	@echo "make develop - Install symlinks for development"
	@echo "make build - Build sdist and bdist_wheel"
	@echo "make clean - Remove all generated files"
	@echo "make lint - Run linter"
	@echo "make test - Run tests"

install:
	pip install .

develop:
	pip install -e .[test]

build: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf build/ dist/ $(NAME).egg-info/ docs/build/ .pytest_cache/ .coverage

lint:
	pylint -E $(NAME)

test: lint
	coverage run --rcfile coverage.cfg -m pytest -v tests
	coverage report --rcfile coverage.cfg

.PHONY: all install develop build clean lint test
