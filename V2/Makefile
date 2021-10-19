deploy:
		@echo "Using serverles.yml provider config to deploy"
		@echo "Deploying Time Tracker to Azure..."
		sls deploy
		rm -rf .serverless
		rm -f host.json
		rm -f local.settings.json
		@echo "Completed! "
