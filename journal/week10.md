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

- Now, run the /bin file to create the resource: `./bin/cfn/networking`

- Execute the change set on the console