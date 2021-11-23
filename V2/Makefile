.PHONY: help
help:
		@echo "---------------HELP-----------------"
		@echo "To install the dependencies type make install"
		@echo "To test the project type make test"
		@echo "To test a specific test of the project make test specific_test=name of test"
		@echo "To run the local database type make start-local"
		@echo "To run all comands type make ci"
		@echo "------------------------------------"

.PHONY: install
install:
		@echo "=========================================Installing dependencies Time Tracker========================================="
		npm install
		pip install --upgrade pip
		pip install -r requirements.txt
		@echo "Completed! "

.PHONY: test
test: export ENVIRONMENT = test
test: export TEST_DB_CONNECTION = sqlite:///file:memory?mode=memory&cache=shared&uri=true
test:
		@echo "=========================================Lint with flake8========================================="
		flake8 . --show-source --statistics
		@echo "Completed flake8!"
		@echo "=========================================Test with pytest========================================="
		@if [ "$(specific_test)" ]; then \
		python -m pytest -v -k $(specific_test);\
		else \
		python -m pytest -v;\
		fi
		@echo "Completed test!"

start-local:
		docker compose up
	
.PHONY: ci
ci: 	install test