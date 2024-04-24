# Week 12 — Modern APIs



# Name not certain yet

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

- **Homework challenge**
- Create the GitHub Actions worksflow: github/workflows/sync.yaml (You would need to rename these accordingly when setting up the workflow. And also rework the yaml file)