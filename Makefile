POETRY=poetry
POETRY_RUN=$(POETRY) run

SOURCES_FOLDER=src
TESTS_FOLDER=tests

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

check_no_main:
ifeq ($(BRANCH),main)
	echo "You are good to go!"
else
	$(error You are not in the main branch)
endif

patch: check_no_main
	$(POETRY_RUN) bumpversion patch --verbose
	git push --follow-tags

minor: check_no_main
	$(POETRY_RUN) bumpversion minor --verbose
	git push --follow-tags

major: check_no_main
	$(POETRY_RUN) bumpversion major --verbose
	git push --follow-tags

style:
	$(POETRY_RUN) isort $(SOURCES_FOLDER)
	$(POETRY_RUN) isort $(TESTS_FOLDER)
	$(POETRY_RUN) black $(SOURCES_FOLDER)
	$(POETRY_RUN) black $(TESTS_FOLDER)

lint:
	$(POETRY_RUN) isort $(SOURCES_FOLDER) --check-only
	$(POETRY_RUN) isort $(TESTS_FOLDER) --check-only
	$(POETRY_RUN) black $(SOURCES_FOLDER) --check
	$(POETRY_RUN) black $(TESTS_FOLDER) --check

test:
	$(POETRY_RUN) pytest $(TESTS_FOLDER)

test-verbose:
	$(POETRY_RUN) pytest $(TESTS_FOLDER) -vv

run:
	$(POETRY_RUN) python -m $(SOURCES_FOLDER)