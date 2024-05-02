# Week 12 — Modern APIs



# Name not certain yet

# Setup and Sync Static Website

- Create a new file: bin/frontend/static-build
- Give execution rights
- Run the file
- This should add a /static dir in frontend-react-js/build/ and also reflect a static reference in the index.html in the frontend-react-js/build/ dir
- Zip the contents of the build dir `zip -r build.zip build/`
- Download to your system and unzip (delete the zip from cloudprojectbootcamp now that it's on desktop)
- Go to s3 > cruddur.com (which is a public bucket)
- Drag and drop the contents of the build dir into here to upload
- This should now be served by cloudfront as it is supposed to read the contents of this s3 bucket

- We would be using a library (https://github.com/teacherseat/aws-s3-website-sync) to sync a folder from your local developer enviroment to your S3 Bucket and then invalidate the CloudFront cache.

- cd to the parent directory and and install
```sh
gem install aws_s3_website_sync

gem install dotenv
```

- Create a script to run the sync: bin/frontend/sync
- Next, create an erb file to generate a .env for environment variables: erb/sync.env.erb
- We want to output the changeset of sync into our tmp/ dir. Add a `.keep` file to persist the dir. This dir is ignored so we run `git add -f tmp/.keep`. Then commit `git commit -m "keep the tmp dir"`

- Update bin/frontend/generate-env to generate out env for the frontend
```sh
./bin/frontend/generate-env
```
- This creates the sync.env file which will be passed into the sync script

- Give execute permission to the sync script

- Run the script

- At this point, it should not have anything to execute. You can got to frontend-react-js/src/components/DesktopSidebar.js and maybe add or remove the `!` after `About` on line 36. Then run the sync tool again. This time, it should have new modifications to apply. Apply the changes. Go to CloudFront on the console, click on the cloudfront distribution id and confirm the changeset. You can reload cruddur.com to confirm the change is correctly shown in the desktopsidebar area.

+ Setup GitHub actions to perform frontend sync

- Create Gemfile and Rakefile in the top level project dir

- Update gitpod.yml to update bundler

- Create a CloudFormation template to configure IAM to trust GitHub
  - Create the files: aws/cfn/sync/template.yaml, aws/cfn/sync/config.toml
  - Create a script to run the template: bin/cfn/sync
  - Give execute permissions
  - Run the script
  - Go to cloudformation and execute the changeset
  - This would create an IAM role. From the resources tab, click into the role
  - Copy the Arn of the role created. This will be use in the GitHub Actions workflow file
  - Add inline policy for S3:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
        "s3:DeleteObject"
      ],
      //Change cruddur.com to your own bucket name
      "Resource": [
        "arn:aws:s3 ::: cruddur.com/*",
        "arn:aws:s3 ::: cruddur.com"
      ]
    }
  ]
}
```
- Give the policy a name: S3Accessfor Sync

- **Homework challenge**
- Create the GitHub Actions worksflow: github/workflows/sync.yaml (You would need to rename these accordingly when setting up the workflow. And also rework the yaml file)


# Reconnect Database

- Go to api.cruddur.com/api/health-check (This should show success) but api.cruddur.com/api/activities/home (This should show internal server error. If it shows debug mode error, then you need to fix that)

- May not be applicable, but if debug mode is shown, you may need to change sth in app.py, then push a new prod image and run the service stack to apply

- Compose up to startup locally

- Internal server error is because we don't have the database seeded with information

+ Update env variable PROD_CONNECTION_URL to reflect the new database name

- Upon up port 5432 for gitpod in the database security group (make sure the description is GITPOD). Use ./bin/rds/update-sg-rule to update security group rule for our specific gitpod IP. There are a number of envs you will need to change in the script.

- You can now connect to the prod database: `./bin/db/connect prod`
- Exit

- Schema load for prod: `./bin/db/schema-load prod`

- You can run migrate locally for production using `CONNECTION_URL=PROD_CONNECTION_URL ./bin/db/migrate`
- You can connect again and use postgres commands from before to see tables

- You may need to change the CONNECTION_URL set in env variables of post confirmation lambda to reflect the new cfn cluster
- On the console, under the post confirmation lambda, manually point the vpc to the new cfn created vpc. Create a new security group (in a new tab) (name: CognitoLambdaSG) (description: For the Lambda that needs to connect to postgres) with no inbound rules and attach it to the vpc. Select the public subnets. 
- Go to the database security group and allow postgres port access from that newly created security group (description: COGNITOPOSTCONF)

- In cognito, delete all previous users

- Now, try to signup on cruddur.com
- Then sign-in
- Make a Crud

- Try to signup as another user or even multiples

**Refactor app.py into separate modules**

- Create the following files: backend-flask/lib/rollbar.py, backend-flask/lib/xray.py, backend-flask/lib/honeycomb.py, backend-flask/lib/cors.py, backend-flask/lib/cloudwatch.py, backend-flask/lib/helpers.py

- Create a new folder: backend-flask/routes
- Create the following files: backend-flask/routes/activities.py, backend-flask/routes/users.py, backend-flask/routes/messages.py, backend-flask/routes/general.py
- Refactor backend-flask/app.py

- Create file: backend-flask/db/sql/activities/reply.sql

- Run `migration`

```sh
./bin/generate/migration reply_to_activity_uuid_to_string
```
- Thi should generate out a migration file as backend-flask/db/migrations/16844665640237772_reply_to_activity_uuid_to_string.py (may not be exact)

- Modify the file to https://github.com/omenking/aws-bootcamp-cruddur-2023/blob/week-x/backend-flask/db/migrations/16844665640237772_reply_to_activity_uuid_to_string.py

- Run the migration
```sh
./bin/db/migrate
```

- Create file: backend-flask/db/sql/activities/show.sql

- Create the following files: frontend-react-js/src/components/FormErrors.js, frontend-react-js/src/components/FormErrors.css, frontend-react-js/src/components/FormErrorItem.js

- Create files: frontend-react-js/src/lib/Requests.js

- Create files: frontend-react-js/src/pages/ActivityShowPage.js, frontend-react-js/src/pages/ActivityShowPage.css
- Create files: frontend-react-js/src/components/Replies.js, frontend-react-js/src/components/Replies.css

- Create file: frontend-react-js/src/components/ActivityShowItem.js