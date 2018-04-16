# convenience makefile

.DEFAULT_GOAL := build



help:
	@echo "Usage:"
	@echo "    make help        show this message"
	@echo "    make setup       create virtual environment and install dependencies"
	@echo "    make activate    enter virtual environment"
	@echo "    make pipfile     updates Pipfile ana Pipfile.lock based on setup.py"
	@echo "    make tests       run the test suite"
	@echo "    exit             leave virtual environment"

setup:
	@pipenv install --dev

activate:
	@pipenv shell

# anything, in regex-speak
filter = "."
# additional arguments for pytest
args = ""
unit:
	@find . -name '*.pyc' -delete
	@pipenv run pytest myapp/tests -k $(filter) $(args)


run:
	@pipenv run pserve --reload myapp/myapp.ini

.PHONY: help activate unit run