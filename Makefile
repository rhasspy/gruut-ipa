SHELL := bash

.PHONY: check clean reformat dist test

all: dist

venv:
	scripts/create-venv.sh

check:
	scripts/check-code.sh

reformat:
	scripts/format-code.sh

test:
	scripts/run-tests.sh

dist:
	python3 setup.py sdist
