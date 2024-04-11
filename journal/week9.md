# CI/CD with CodePipeline, CodeBuild and CodeDeploy

- Create a new branch on GitHub, named 'prod' from 'main'

- Create a buildspec file for CodeBuild: backend-flask/buildspec.yml

- Go to CodePipeline on AWS and click Create pipeline
	- Pipeline name: cruddur-backend-fargate
	- Service role: New service role
	- Role name: Leave the default generated
	- Check 'Allow AWS CodePipeline to create a service role ...'
	- Advanced settings:
		- Artifact store: Default location
		- Encryption key: Default AWS managed key
		- Click 'Next'
	- Source: Dropdown and select 'GitHub (version 2)'
		- Connection: Click 'Connect to GitHub'. This will bring up a pop-up window.
			- Connection name: cruddur
			- Click 'Connect to GitHub'
			- GitHub Apps: Click 'Install a new app'
				- Select the GitHub account you want to connect with
				- Enter GitHub password to confirm access
				- In Repository access, select only the aws-cruddur-bootcamp repository
				- Save
			- Click 'Connect' (This should show a green 'Ready to connect' status)
		- Repository name: Select the only repo, aws-cruddur-bootcamp
		- Branch name: prod
		- Change detection options: Check 'Start the pipeline on source code change'
		- Output artifact format: CodePipeline default
	- Add build stage: Click 'Skip build stage' //Don't skip. Build here//
	- Add Deploy stage:
		- Deploy provider: Amazon ECS
		- Region: Specify
		- InputArtifacts: ImageDefinition
		- Cluster name: select cruddur (previously created)
		- Service name: backend-flask
		- Next
	- Review and Create pipeline

- On the cruddur-backend-fargate pipeline, click 'Edit'
- We want to add a stage between source and deploy. Click 'Add stage' between Source and Deploy
- Stage name: Build
- Click 'Add stage'
- In the build stage, click 'Add action group'
	+ Action name: bake-image
	+ Action provider: Under 'Build', select AWS CodeBuid
	+ Region: Specify
	+ Input artifacts: Dropdown and select SourceArtifact
	+ Project name: Click 'Create project' to pop-up CodeBuild project creation or go to CodeBuild yourself, under 'Build projects' click 'Create build project'
		- Project name: cruddur-backend-flask-bake-image
		- Check 'Enable build badge'
		- Source provider: GitHub
		- Repository: Check 'Connect using OAuth' and click 'Connect to GitHub'. Authorize access to your GitHub account and click 'Confirm'
		- Repositort: Check 'Repository in my GitHub account'
		- GitHub repository: Select the aws-cruddur-bootcamp repository
		- Source version: prod
		- Webhook: Check 'Rebuild everytime a code change is pushed to this repository'
		- Build type: Single build'
		- Event type: Select any of choice
		- Environment image: Managed image
		- Operating system: Amazon Linux 2
		- Runtime(s): Standard
		- Image: Choose the latest
		- Environment type: Linux
		- Privileged: Check to enable the flag
		- Service role: New service role
		- Change timeout to 15-30 minutes (your choice)
		- Select VPC, subnets and security group (you can select defaults) //Don't do this//
		- Build specifications: Check 'Use a buildspec file'
		- Buildspec name: backend-flask/buildspec.yml
		- CloudWatch logs: Check
			- Group name: /cruddur/build/backend-flask
			- Stream name: backend-flask
		- Click 'Create build project'
	+ Project name: Select the cruddur-backend-flask-bake-image build project
	+ Build type: Single build
	+ Output artifacts: ImageDefinition
- Click to Save changes
- Click 'Release change' to run pipeline

- You can use any of the specified actions (push, pull request, etc) to trigger the pipeline
- Confirm everything is fine: Target groups on load balancers, app on browser, ECS, pipeline