# Serverless Image Processing

## New Directory

Lets contain our cdk pipeline in a new top level directory called:

```sh
cd /workspace/aws-bootcamp-cruddur-2023

mkdir thumbing-serverless-cdk

cd thumbing-serverless-cdk
```

## Install CDK globally

This is so we can use the AWS CDK CLI for anywhere.

```sh
npm install aws-cdk -g
```

- Confirm by typing `cdk`

We'll add the install to our gitpod task file
```sh
  - name: cdk
    before: |
      npm install aws-cdk -g
```

## Initialize a new project

We'll initialize a new typescript cdk project within the folder we created:

```sh
cdk init app --language typescript
```

This will create several directories and files including a "thumbing-serverless-cdk/lib/thumbing-serverless-cdk-stack.ts" file which is where we will define all our IaC

## Add an S3 Bucket

Add the following code to your `thumbing-serverless-cdk-stack.ts`

```ts
import * as s3 from 'aws-cdk-lib/aws-s3';

const bucketName: string = process.env.THUMBING_BUCKET_NAME as string;

const bucket = new s3.Bucket(this, 'ThumbingBucket', {
  bucketName: bucketName,
  removalPolicy: cdk.RemovalPolicy.DESTROY,
});
```

```sh
export THUMBING_BUCKET_NAME="assets.cruddur.com"
gp env THUMBING_BUCKET_NAME="assets.cruddur.com"
```

- [Bucket Construct](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3.Bucket.html)
- [Removal Policy](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_core.RemovalPolicy.html)


Create a .env.example file in thumbing-serverless-cdk directory to hold variables

- Install dotenv

```sh
npm i dotenv
```
- This should now show up in the package.json file in thumbing-serverless-cdk directory


Create a new folder to hold the lambda functions in aws/lambdas/process-images/
  - Add the following files: index.js, test.js, s3-image-processing.js
  - We will add another file; example.json, to visualize the structure of our output
  - Do `cd aws/lambdas/process-images/` and run the following command: `npm init -y`
  - This will create package.json file in the directory
  - Installation:
    - Sharp: https://sharp.pixelplumbing.com/install#aws-lambda
    
    ```sh
    npm i sharp
    npm i @aws-sdk/client-s3
    ```
  - Ignore node-modules in .gitignore


## CDK Bootstrapping

> Deploying stacks with the AWS CDK requires dedicated Amazon S3 buckets and other containers to be available to AWS CloudFormation during deployment. 

https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html

```sh
cdk bootstrap aws://ACCOUNT-NUMBER-1/REGION-1 aws://ACCOUNT-NUMBER-2/REGION-2 ...
```
Example:
```sh
cdk bootstrap aws://123456789012/us-east-1
cdk bootstrap 123456789012/us-east-1 123456789012/us-west-1
```

Run:

```sh
cdk bootstrap "aws://$AWS_ACCOUNT_ID/$AWS_DEFAULT_REGION"
```

- Go to the console, under CloudFormation. There should be a "CDKToolkit" stack

## Build

We can use build to catch errors prematurely.
This just builds tyescript

```sh
npm run build
```

## Synth

> The synth command is used to synthesize the AWS CloudFormation stack(s) that represent your infrastructure as code.

```sh
cdk synth
```
The command works a little similar to terraform plan. This should dump some files in cdk.out directory.

## Deploy

```sh
cdk deploy
```

- Check CloudFormantion and Lambda for resources