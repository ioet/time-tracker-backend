.PHONY: help
help:
		@echo "---------------HELP-----------------"
		@echo "- make install --> Install the dependencies"
		@echo "- make test --> Run all tests"
		@echo "- make test specific_test=<name_of_the_test> --> Run specific test"
		@echo "- make start-local --> Run local database"
		@echo "- make ci --> Install the dependencies and run all tests"
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
test:
		@echo "=========================================Lint with flake8========================================="
		flake8 . --show-source --statistics
		@echo "Completed flake8!"
		@echo "=========================================Test with pytest========================================="
		@if [ "$(specific_test)" ]; then \
		python -m pytest -vv -s -k $(specific_test);\
		else \
		python -m pytest -v;\
		fi
		@echo "Completed test!"

start-local:
		docker compose up
	
.PHONY: ci
ci: 	install test