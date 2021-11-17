.PHONY: help
help:
		@echo "---------------HELP-----------------"
		@echo "To install the dependencies type make install"
		@echo "To test the project type make test"
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
test:
		@echo "=========================================Lint with flake8========================================="
		flake8 . --show-source --statistics
		@echo "Completed flake8!"
		@echo "=========================================Test with pytest========================================="
		python -m pytest -v
		@echo "Completed test!"

start-local:
		docker compose up
	
.PHONY: ci
ci: 	install test