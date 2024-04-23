# CloudFormation

- Create a new directory to hold cloudformation templates: aws/cfn/
- Add file: template.yaml

- You can use this command to validate template syntax:
```sh
aws cloudformation validate-template --template-body file:///workspace/aws-bootcamp-cruddur-2023/aws/cfn/template.yaml
```

---
- You can also use cfn-lint to validate template:

Install: `pip install cfn-lint`
Check: `cfn-lint`
To validate a file: `cfn-lint -t /workspace/aws-bootcamp-cruddur-2023/aws/cfn/template.yaml`

- Add the command to install cfn-lint in _.gitpod.yml_
---

- There is also CloudFormation guard, a policy-as-code evaluation tool, used to write rules and validate JSON- and YAML-formatted data such as CloudFormation Templates, K8s configurations, and Terraform JSON plans/configurations against those rules.
- To install: cargo install cfn-guard
  - Add to .gitpod.yml

- Create the following policy as code guard files: aws/cfn/task-definition.guard

- Read-up on cfn-guard and try to implement it********************************************************

---

- You can use application composer or cloudformation designer to generate cfn template

- Create new directory and file: bin/cfn/cluster
- The _--no-execute-changeset_ flag in the deployment command allows you to manually review and authorize changes before they are created.
- Go to CloudFormation > Stacks > cluster-name
  - Under 'Change set' tab, click into the change set and click 'Execute change set'

- You can go to Cloudtrail and see logs of all the events in CloudTrail > Event history > event-name

//You can use Stacksets on CloudFormation console to deploy across multiple regions and accounts//

- Create an s3 bucket to contain all of our artifacts for CloudFormation and adjust bin/cfn/cluster to use the bucket

```sh
aws s3 mk s3://cfn-artifacts
export CFN_BUCKET="cfn-artifacts"
gp env CFN_BUCKET="cfn-artifacts"
```
> Remember bucket names are unique

**CFN for Networking**

- Create a new directory/file: aws/cfn/networking/template.yaml

- Create a file to run the template: bin/cfn/networking

- Give execute permission to the file

- Now, run the /bin file to create the resource: `./bin/cfn/networking`

- Execute the change set on the console

**CFN for Cluster**

- Create dir/file: aws/cfn/cluster/template.yaml

- Modify bin/cfn/cluster

- Give execute permission to the file

+ Use cfn-toml

- `gem install cfn-toml` (add this to gitpod.yml)

- Create the following: aws/cfn/cluster/config.toml.examle, aws/cfn/cluster/config.toml, aws/cfn/networking/config.toml.example, aws/cfn/networking/config.toml

**CFN for Service Layer**

- Create the following: aws/cfn/service/config.toml.examle, aws/cfn/service/config.toml, aws/cfn/service/template.yaml

- Create the service deployment file: bin/cfn/service
- Give execute permission to the file
- Run the file

- This didn't work because we need database security group to setup the service so we will continue this section after database setup

- While trying to debug service create, make a new file: bin/backend/create-service

**CFN for RDS**

- Create the dir/file: aws/cfn/db/template.yaml and aws/cfn/db/config.toml

- Create the file: bin/cfn/db

- Set DB_PASSWORD for MasterUserPassword. It is required in bin/cfn/db

```sh
export DB_PASSWORD=dbPassword123
gp env DB_PASSWORD=dbPassword123
```

- Give execute permission to the file: bin/cfn/db

- Run the database deployment

- Copy the connection endpoint of the database. Go to Parameter store on Systems manager and edit the CONNECTION_URL to reflect that. You only need to edit what is after @ and before port number.

**CFN for Service Layer Again**

- After pointing the load balancer to the appropriate port, run the service deployment script

- Go to Route53 > Hosted zones > Records > api.cruddur.com and edit route to point to the new load balancer dns. Do the same for cruddur.com record

- On the browser: api.cruddur.com/api/health-check

**SAM CFN for DynamoDB, DynamoDB Streams and Lambda**

- We will be using AWS SAM for the infrastructure implementation here

- Create dir/files: ddb/template.yaml, ddb/config.toml

- In the template.yaml, the Dynamodb table resource attributedefinitions and keyschema sections as well as other specifications was filled from our previously created bin/ddb/schema-load
- Most of the configurations are gotten from the previously created lambda stream on the console

- Add task to install AWS SAM in .gitpod.yml
https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

- Do `sam --version` to confirm

- Create a new directory: ddb/cruddur-messaging-stream

- Move and rename aws\lambdas\cruddur-messaging-stream.py to ddb/cruddur-messaging-stream/lambda_function.py

- Create SAM files for build, package and deploy: ddb/build, ddb/package, ddb/deploy

- Give execute permission to all files

- Modify .gitignore to ignore the output of SAM build function including the .aws.sam/ directory

- Now, run the files

- Deploy will create a changeset and require console authorization

**CFN for CICD**

- Create the dir/files: aws/cfn/cicd/template.yaml, aws/cfn/cicd/config.toml
- Create the artifact bucket manually

- Create a codebuild nested stack dir/file: aws/cfn/cicd/nested/codebuild.yaml

- Create the deployment file: bin/cfn/cicd
- Give execute permission to the file

- Create a new top level dir called tmp to hold the output of cloudformation package

- Run the deploy script: bin/cfn/cicd

- Confirm changeset on cloudformation

- If successful, go to codepipeline. The first run usually fails because you need to update github connection. 
- Go to codepipeline > settings > connections. Check the correct connection and click 'update pending connection'
- Either install app on the correct github account or just connect if you already installed previously

**CFN Static Website Hosting Frontend**

- Serving frontend via CloudFront

- Create the following dir/files: aws/cfn/frontend/template.yaml, aws/cfn/frontend/config.toml

- Create the provisioning file: bin/cfn/frontend
- Give execute permission to the file
- Run the file

//- You may need to remove the cruddur.com type A record from route53 to prevent conflict error//

