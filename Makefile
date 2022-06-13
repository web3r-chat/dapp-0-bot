SHELL := /bin/bash

GIT_BRANCH_NAME ?= $(shell git branch --show-current)

# The bot's rasa-sdk action server
ACTION_SERVER_IMAGE_REGISTRY ?= registry.digitalocean.com/web3r-chat/
ACTION_SERVER_IMAGE_NAME ?= dapp-0-bot-actions
ACTION_SERVER_IMAGE_TAG ?= $(GIT_BRANCH_NAME)
ACTION_SERVER_IMAGE_COMPLETE_NAME ?= $(ACTION_SERVER_IMAGE_REGISTRY)$(ACTION_SERVER_IMAGE_NAME):$(ACTION_SERVER_IMAGE_TAG)

.PHONY: clean
clean:
	rm -rf .rasa .mypy_cache

# This is the test we run during CI/CD
.PHONY: all-test
all-test: \
	all-static-check \
	rasa-train \
	rasa-test
	
.PHONY: all-static
all-static: \
	python-format python-lint-check python-type-check
	
.PHONY: all-static-check
all-static-check: \
	python-format-check python-lint-check python-type-check

.PHONY: rasa-train
rasa-train:
	rasa train --domain domain

.PHONY: rasa-test
rasa-test:
	rasa test --domain domain --fail-on-prediction-errors

#######################################################################
# Targets to build & push with docker:
# - the action server 

.PHONY: action-server-build
action-server-build:
	docker build . --file Dockerfile --tag $(ACTION_SERVER_IMAGE_COMPLETE_NAME)

.PHONY: action-server-push
action-server-push:
	@echo pushing image: $(ACTION_SERVER_IMAGE_COMPLETE_NAME)
	docker image push $(ACTION_SERVER_IMAGE_COMPLETE_NAME)

#######################################################################	
.PHONY: doctl-registry-login
doctl-registry-login:
	./scripts/doctl_registry_login.sh

.PHONY: doctl-auth-init
doctl-auth-init:
	./scripts/doctl_auth_init.sh


.PHONY: install-doctl
install-doctl:
	sudo snap install doctl
	sudo snap connect doctl:dot-docker

.PHONY: install-jp
install-jp:
	sudo apt-get update && sudo apt-get install jp
	

.PHONY: install-python-dev
install-python-dev:
	pip install --upgrade pip
	pip install -r requirements-dev.txt


.PHONY: install-python-prod
install-python-prod:
	pip install --upgrade pip
	pip install -r requirements.txt

PYTHON_DIRS ?= scripts actions

.PHONY: python-format
python-format:
	@echo "---"
	@echo "python-format"
	python -m black $(PYTHON_DIRS)

.PHONY: python-format-check
python-format-check:
	@echo "---"
	@echo "python-format-check"
	python -m black --check $(PYTHON_DIRS)

.PHONY: python-lint-check
python-lint-check:
	@echo "---"
	@echo "python-lint-check"
	python -m pylint --jobs=0 --rcfile=.pylintrc $(PYTHON_DIRS)

# https://github.com/python/mypy/issues/12664: --no-incremental 
.PHONY: python-type-check
python-type-check:
	@echo "---"
	@echo "python-type-check"
	python -m mypy --config-file .mypy.ini --show-column-numbers --no-incremental $(PYTHON_DIRS)

#######################################################################
.PHONY: jwt
jwt:
	@export SECRET_JWT_KEY=$(SECRET_JWT_KEY) ; \
	export JWT_METHOD=$(JWT_METHOD) ; \
	python -m scripts.jwt_create

.PHONY: connect
connect:
	@export SECRET_JWT_KEY=$(SECRET_JWT_KEY) ; \
	export JWT_METHOD=$(JWT_METHOD) ; \
	python -m scripts.connect
	
.PHONY: smoketest
smoketest:
	@export BOT_URL=$(BOT_URL) ; \
	export SECRET_JWT_KEY=$(SECRET_JWT_KEY) ; \
	export JWT_METHOD=$(JWT_METHOD) ; \
	python -m scripts.smoketest

	
	
	
