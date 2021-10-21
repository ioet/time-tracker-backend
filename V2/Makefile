install:
		@echo "Installing Time Tracker"
		npm install
		pip install --upgrade pip
		pip install -r requirements.txt
		@echo "Completed! "

deploy:
		@echo "Using serverless.yml provider config to deploy"
		@echo "Deploying Time Tracker to Azure..."
		sls deploy
		rm -rf .serverless
		rm -f host.json
		rm -f local.settings.json
		@echo "Completed! "
