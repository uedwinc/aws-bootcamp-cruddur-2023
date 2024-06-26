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


- Overdue, but you can set DOMAIN_NAME as variable:
```sh
export DOMAIN_NAME="cruddur.com"
gp env DOMAIN_NAME="cruddur.com"
```

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

- [Bucket Construct](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3.Bucket.html)
- [Removal Policy](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_core.RemovalPolicy.html)


- Manually or using the cli, create a new bucket on the console: assets.cruddur.com
```sh
aws s3 ls
```


- Create a .env.example file in thumbing-serverless-cdk directory to hold variables

- Install dotenv

```sh
npm i dotenv
```
- This should now show up in the package.json file in thumbing-serverless-cdk directory

## Load Env Vars
  ```ts
const dotenv = require('dotenv');
dotenv.config();

const bucketName: string = process.env.THUMBING_BUCKET_NAME as string;
const folderInput: string = process.env.THUMBING_S3_FOLDER_INPUT as string;
const folderOutput: string = process.env.THUMBING_S3_FOLDER_OUTPUT as string;
const webhookUrl: string = process.env.THUMBING_WEBHOOK_URL as string;
const topicName: string = process.env.THUMBING_TOPIC_NAME as string;
const functionPath: string = process.env.THUMBING_FUNCTION_PATH as string;
console.log('bucketName',bucketName)
console.log('folderInput',folderInput)
console.log('folderOutput',folderOutput)
console.log('webhookUrl',webhookUrl)
console.log('topicName',topicName)
console.log('functionPath',functionPath)
```

## Create Bucket

```ts
import * as s3 from 'aws-cdk-lib/aws-s3';

const bucket = this.createBucket(bucketName)

createBucket(bucketName: string): s3.IBucket {
  const logicalName: string = 'ThumbingBucket';
  const bucket = new s3.Bucket(this, logicalName , {
    bucketName: bucketName,
    removalPolicy: cdk.RemovalPolicy.DESTROY,
  });
  return bucket;
}
```

## Create Lambda

```ts
import * as lambda from 'aws-cdk-lib/aws-lambda';

const lambda = this.createLambda(folderInput,folderOutput,functionPath,bucketName)

createLambda(folderIntput: string, folderOutput: string, functionPath: string, bucketName: string): lambda.IFunction {
  const logicalName = 'ThumbLambda';
  const code = lambda.Code.fromAsset(functionPath)
  const lambdaFunction = new lambda.Function(this, logicalName, {
    runtime: lambda.Runtime.NODEJS_18_X,
    handler: 'index.handler',
    code: code,
    environment: {
      DEST_BUCKET_NAME: bucketName,
      FOLDER_INPUT: folderIntput,
      FOLDER_OUTPUT: folderOutput,
      PROCESS_WIDTH: '512',
      PROCESS_HEIGHT: '512'
    }
  });
  return lambdaFunction;
}
```

## Create SNS Topic

```ts
import * as sns from 'aws-cdk-lib/aws-sns';

const snsTopic = this.createSnsTopic(topicName)

createSnsTopic(topicName: string): sns.ITopic{
  const logicalName = "Topic";
  const snsTopic = new sns.Topic(this, logicalName, {
    topicName: topicName
  });
  return snsTopic;
}
```

## Create an SNS Subscription

```ts
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';

this.createSnsSubscription(snsTopic,webhookUrl)

createSnsSubscription(snsTopic: sns.ITopic, webhookUrl: string): sns.Subscription {
  const snsSubscription = snsTopic.addSubscription(
    new subscriptions.UrlSubscription(webhookUrl)
  )
  return snsSubscription;
}
```

## Create S3 Event Notification to SNS

```ts
this.createS3NotifyToSns(folderOutput,snsTopic,bucket)

createS3NotifyToSns(prefix: string, snsTopic: sns.ITopic, bucket: s3.IBucket): void {
  const destination = new s3n.SnsDestination(snsTopic)
  bucket.addEventNotification(
    s3.EventType.OBJECT_CREATED_PUT, 
    destination,
    {prefix: prefix}
  );
}
```

## Create S3 Event Notification to Lambda

```ts
this.createS3NotifyToLambda(folderInput,laombda,bucket)

createS3NotifyToLambda(prefix: string, lambda: lambda.IFunction, bucket: s3.IBucket): void {
  const destination = new s3n.LambdaDestination(lambda);
    bucket.addEventNotification(s3.EventType.OBJECT_CREATED_PUT,
    destination,
    {prefix: prefix}
  )
}
```

## Create Policy for Bucket Access

```ts
const s3ReadWritePolicy = this.createPolicyBucketAccess(bucket.bucketArn)
```

## Create Policy for SNS Publishing

```ts
const snsPublishPolicy = this.createPolicySnSPublish(snsTopic.topicArn)
```

## Attach the Policies to the Lambda Role

```ts
lambda.addToRolePolicy(s3ReadWritePolicy);
lambda.addToRolePolicy(snsPublishPolicy);
```

## thumbing-serverless-cdk-stack.ts

```ts
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as sns from 'aws-cdk-lib/aws-sns';
import { Construct } from 'constructs';
import * as dotenv from 'dotenv';

dotenv.config();

export class ThumbingServerlessCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here
    const uploadsBucketName: string = process.env.UPLOADS_BUCKET_NAME as string;
    const assetsBucketName: string = process.env.ASSETS_BUCKET_NAME as string;
    const folderInput: string = process.env.THUMBING_S3_FOLDER_INPUT as string;
    const folderOutput: string = process.env.THUMBING_S3_FOLDER_OUTPUT as string;
    const webhookUrl: string = process.env.THUMBING_WEBHOOK_URL as string;
    const topicName: string = process.env.THUMBING_TOPIC_NAME as string;
    const functionPath: string = process.env.THUMBING_FUNCTION_PATH as string;
    console.log('uploadsBucketName',)
    console.log('assetsBucketName',assetsBucketName)
    console.log('folderInput',folderInput)
    console.log('folderOutput',folderOutput)
    console.log('webhookUrl',webhookUrl)
    console.log('topicName',topicName)
    console.log('functionPath',functionPath)

    const uploadsBucket = this.createBucket(uploadsBucketName);
    const assetsBucket = this.importBucket(assetsBucketName);

    // create a lambda
    const lambda = this.createLambda(
      functionPath, 
      uploadsBucketName, 
      assetsBucketName, 
      folderInput, 
      folderOutput
    );

    // create topic and subscription
    const snsTopic = this.createSnsTopic(topicName)
    this.createSnsSubscription(snsTopic,webhookUrl)

    // add our s3 event notifications
    this.createS3NotifyToLambda(folderInput,lambda,uploadsBucket)
    this.createS3NotifyToSns(folderOutput,snsTopic,assetsBucket)

    // create policies
    const s3UploadsReadWritePolicy = this.createPolicyBucketAccess(uploadsBucket.bucketArn)
    const s3AssetsReadWritePolicy = this.createPolicyBucketAccess(assetsBucket.bucketArn)
    //const snsPublishPolicy = this.createPolicySnSPublish(snsTopic.topicArn)

    // attach policies for permissions
    lambda.addToRolePolicy(s3UploadsReadWritePolicy);
    lambda.addToRolePolicy(s3AssetsReadWritePolicy);
    //lambda.addToRolePolicy(snsPublishPolicy);
  }

  createBucket(bucketName: string): s3.IBucket {
    const bucket = new s3.Bucket(this, 'UploadsBucket', {
      bucketName: bucketName,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });
    return bucket;
  }

  importBucket(bucketName: string): s3.IBucket {
    const bucket = s3.Bucket.fromBucketName(this,"AssetsBucket",bucketName);
    return bucket;
  }

  createLambda(functionPath: string, uploadsBucketName: string, assetsBucketName: string, folderInput: string, folderOutput: string): lambda.IFunction {
    const lambdaFunction = new lambda.Function(this, 'ThumbLambda', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(functionPath),
      environment: {
        DEST_BUCKET_NAME: assetsBucketName,
        FOLDER_INPUT: folderInput,
        FOLDER_OUTPUT: folderOutput,
        PROCESS_WIDTH: '512',
        PROCESS_HEIGHT: '512'
      }
    });
    return lambdaFunction;
  } 

  createS3NotifyToLambda(prefix: string, lambda: lambda.IFunction, bucket: s3.IBucket): void {
    const destination = new s3n.LambdaDestination(lambda);
    bucket.addEventNotification(
      s3.EventType.OBJECT_CREATED_PUT,
      destination//,
      //{prefix: prefix} // folder to contain the original images
    )
  }

  createPolicyBucketAccess(bucketArn: string){
    const s3ReadWritePolicy = new iam.PolicyStatement({
      actions: [
        's3:GetObject',
        's3:PutObject',
      ],
      resources: [
        `${bucketArn}/*`,
      ]
    });
    return s3ReadWritePolicy;
  }

  createSnsTopic(topicName: string): sns.ITopic{
    const logicalName = "ThumbingTopic";
    const snsTopic = new sns.Topic(this, logicalName, {
      topicName: topicName
    });
    return snsTopic;
  }

  createSnsSubscription(snsTopic: sns.ITopic, webhookUrl: string): sns.Subscription {
    const snsSubscription = snsTopic.addSubscription(
      new subscriptions.UrlSubscription(webhookUrl)
    )
    return snsSubscription;
  }

  createS3NotifyToSns(prefix: string, snsTopic: sns.ITopic, bucket: s3.IBucket): void {
    const destination = new s3n.SnsDestination(snsTopic)
    bucket.addEventNotification(
      s3.EventType.OBJECT_CREATED_PUT, 
      destination,
      {prefix: prefix}
    );
  }

  /*
  createPolicySnSPublish(topicArn: string){
    const snsPublishPolicy = new iam.PolicyStatement({
      actions: [
        'sns:Publish',
      ],
      resources: [
        topicArn
      ]
    });
    return snsPublishPolicy;
  }
  */
}
```

## Lambdas

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

- Create a file to hold sharp installation: bin/avatar/build
- Give execute permission


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

## List Stacks

```sh
cdk ls
```

- Check CloudFormantion, S3 and Lambda for resources

- Write scripts to upload and clear s3: bin/avatar/upload, bin/avatar/clear
- Give execute permissions
- Add the file to upload: bin/avatar/files/data.jpg (https://github.com/omenking/aws-bootcamp-cruddur-2023/blob/week-8-again/bin/avatar/files/data.jpg)
- Upload `./bin/avatar/upload`
- Confirm if this triggered the Lambda function and check the CloudWatch logs. Check S3 for processed output folder (make sure file output is in jpg)

- Update .gitpod.yml (just confirm)


## Desroy Stacks

```sh
cdk destroy
```

# Serving Avatars via CloudFront

+ Go to CloudFront on the console. Click Create a CloudFront distribution.
  - Origin domain: Choose the s3 bucket origin
  - Name: Leave default
  - Origin access: Origin access control settings
    + Create control setting
      - Name: Leave default
      - Signing behaviour: Sign requests
      - Origin type: S3
      - Create
    + Bucket policy: Copy policy
      - Go to our s3 bucket (assets.cruddur.com)
      - Under Permissions, Edit
      - Paste the copied policy
      - Save
  - Enable origin shield: No (it costs)
  - Compress objects automatically: Yes
  - Viewer protocol policy: Redirect HTTP to HTTPS
  - Allowed HTTP methods: GET, HEAD
  - Restrict viewer access: No
  - Cache key and origin requests: Cache policy and origin request policy
    + Cache policy: CachingOptimized
    + Origin request policy: CORS-CustomOrigin
  - Response headers policy: SimpleCORS
  - Additional settings >
    + Smooth streaming: No
  - Settings >
    + Price class: Use all edge locations
  - Alternate domain name (CNAME): assets.cruddur.com
  - Custom SSL certificate: The certificate is required to be in us-east-1 region, so you can go to ACM in that region and request
  - Standard logging: Off
  - IPv6: On
  - Description: Serve assets for cruddur
  - Create distribution
- This will take a while to create and enable

+ Go to Route53 > Hosted zones > cruddur.com > Create record
  - Record name: assets
  - Check Alias: Alias to CloudFront distribution
  - Select the CloudFront distribution
  - Create record


- Make sure you have upload in s3
- Try to open in browser (use another browser if necessary) at `assets.cruddur.com/avatars/processed/data.jpg`


# Implement Users Profile Page

> N.B: Before you can run docker compose, you must login to ecr /bin/ecr/login

- Edit backend-flask/Dockerfile

- Create a bash script to bootstrap major tasks: bin/bootstrap

- Create backend-flask/bin/db/sql/users/show.sql

- Modify /services/user_activities.py
- Modify frontend-react-js/src/pages/UserFeedPage.js

- Create new files: frontend-react-js/src/components/EditProfileButton.js and frontend-react-js/src/components/EditProfileButton.css
- Modify frontend-react-js/src/components/CrudButton.js
- Modify frontend-react-js/src/components/ActivityFeed.js
- Modify frontend-react-js/src/pages/HomeFeedPage.js
- Edit frontend-react-js/src/pages/NotificationsFeedPage.js
- Create new files: frontend-react-js/src/components/ProfileHeading.js and frontend-react-js/src/components/ProfileHeading.css
  - **You will need to modify something here to be specific to you**


# Implement Migrations Backend Endpoint and Profile Form

- Create a bash script to prepare all databases: bin/prepare
- Give it execute permissions

- Create a new file: frontend-react-js/jsconfig.json

- Create new files: frontend-react-js/src/components/ProfileForm.js and frontend-react-js/src/components/ProfileForm.css

- Modify frontend-react-js/src/components/ReplyForm.css

- Create new file: frontend-react-js/src/components/Popup.css

- Modify frontend-react-js/src/App.js

- Edit backend-flask/app.py

- Create file: backend-flask/services/update_profile.py

- Create file: backend-flask/db/sql/users/update.sql

- Create new directory and file: bin/generate/migration

- Create the migration directory and add a .keep file: backend-flask/db/migrations/.keep

- Give execute permission to the migration file:
```sh
chmod u+x bin/generate/migration
```

- Run the file:
```sh
./bin/generate/migration add_bio_column
```

- Confirm the file is generated in backend-flask/db/migrations/
- Edit this generated file as shown: https://github.com/omenking/aws-bootcamp-cruddur-2023/blob/week-8-again/backend-flask/db/migrations/16812294605993273_add_bio_column.py

- Create files: bin/db/migrate and bin/db/rollback
- Give execute permission to both files

- Modify backend-flask/db/schema.sql
- Modify backend-flask/lib/db.py

- Run the migrate and rollback files:
```sh
./bin/db/migrate

./bin/db/rollback
```

- You can confirm by connecting to psql


# Implement Avatar Uploading

- To start things up, run the bootstrap script, then docker-compose, then db/setup, then ddb/schema-load, then ddb/seed, then migrate

**Setup Lambda function to use in API Gateway**

- Go to Lambda > Function > Create function
  - Function name: CruddurAvatarUpload
  - Runtime: Ruby 2.7
  - Architecture: x86_64
  - Execution role: Create a new role with basic Lambda permissions
  - Create

- Create new directory and file: aws/lambdas/cruddur-upload-avatar/function.rb

- Generate a Gemfile in this directory:

```sh
cd aws/lambdas/cruddur-upload-avatar/

bundle init
```
- This will generate a Gemfile in the directory
- Modify the Gemfile as shown: https://github.com/omenking/aws-bootcamp-cruddur-2023/blob/week-8-again/aws/lambdas/cruddur-upload-avatar/Gemfile
- Run the following command:
```sh
bundle install
```

- You can set the following env variables in your workspace:
```sh
export UPLOADS_BUCKET_NAME="cruddur-uploaded-avatars"
gp env UPLOADS_BUCKET_NAME="cruddur-uploaded-avatars"
```

- Run the function.rb exec
```sh
bundle exec ruby function.rb
```
- This returns a presigned url which we can use to upload data

+ You can test this using extensions like postman or alternative like thunder client
  - Go to New Request
  - Enter the presigned url
  - Drop down and choose "PUT"
  - Click "Send"
+ Upload the image and confirm that it shows on s3. You can delete the image from s3 afterwards.

- We need to package this as a ruby Lambda

- In the CruddurAvatarUpload Lambda created, paste the function.rb code and click Deploy
- Under the Configuration tab, go to Permissions and click into the Role name
  - Drop down permissions and add in-line policy
  - Under Visual editor:
    - Service: S3
    - Actions: PutObject
    - Resources: Check "Specific" and click "Add ARN"
      - Bucket name: cruddur-uploaded-avatars
      - Object name: Check "Any"
      - Add
    - Review Policy
      - Name: PresignedUrlAvatarPolicy
    - Create
- Expand that policy and copy the json code
- Create a new file to hold the policy: aws/policies/s3-upload-avatar-presigned-url-policy.json
- Under the Configuration tab, go to Environment variables and click Edit
  - Key: UPLOADS_BUCKET_NAME
  - Value: cruddur-uploaded-avatars
  - Save
- Under the "Code" section, go to "Runtime settings" and click Edit
  - Change "Handler" to function.handler
- If necessary, rename the function in the "Code" tab to 'function.rb'
- Deploy 
- Go to the "Test" tab and click "Test"


**Setup jwt-verify Lambda authorizer for HTTP API**

- Create new directory and file: aws/lambdas/lambda-authorizer/index.js

- Installation:
```sh
cd aws/lambdas/lambda-authorizer/

npm install aws-jwt-verify --save
```

- Zip the contents of the lambda-authorizer
```sh
zip -r lambda-authorizer /lambda-authorizer
```

- Go to Lambda > Function > Create function
  - Function name: CruddurApiGatewayLambdaAuthorizer
  - Runtime: Node.js 18.x
  - Architecture: x86_64
  - Create
  - In the "Code" tab, click 'Upload from' dropdown and select ".zip"
  - Upload the lambda-authorizer.zip file
  - Save


**Setup API Gateway**

- Go to API Gateway on AWS > APIs > HTTP API > Build
  + Create an API
    - Integrations: lambda
    - AWS Region: Specify
    - Lambda function: Select the CruddurAvatarUpload lambda function
    - API name: api.cruddur.com
    - Next
  + Configure routes
    - Method: POST
    - Resource path: /avatars/key_upload
    - Integration target: CruddurAvatarUpload
    - Next
  + Define stages
    - Stage name: $default
    - Check Auto-deploy
    - Next
  + Review and Create
  + Create
- In the sidebar, click "Authorization"
- Go to "Manage authorizers" and click 'Create'
- Check 'Lambda' and specify the following under 'Authorizer settings'
  + Name: CruddurJWTAuthorizer
  + AWS Region: Specify
  + Lambda function: Select the CruddurApiGatewayLambdaAuthorizer
  + Response mode: Simple
  + Uncheck 'Authorizer caching'
  + Check 'Invoke permissions'
  + Create
- Go to "Attach authorizers to routes"
  + Click 'POST'
  + Dropdown 'Select existing authorizer' and select the CruddurJWTAuthorizer
  + Click "Attach authorizer"
- In the sidebar panel, under 'Deploy', click on "Stages"
  - Check '$default'
  - Copy the 'Invoke url'

- If you want, you can turn on logging for $default API Gateway

//- In API Gateway, Under 'Develop' in the sidebar, select "CORS" and click 'Configure'
//  + Access-Control-Allow-Origin: * (Click 'Add')
//  + Access-Control-Allow-Methods: Select 'POST' and 'OPTIONS'
//  + Access-Control-Allow-Headers: *, Authorization
//  + Access-Control-Expose-Headers: *, Authorization
//  + Save

- Open the frontend app, go to profile page and try to upload avatar
- Enter the url along with the resource path in the browser: Invoke url/avatars/key_upload
- Confirm that the Lambda was triggered in Lambda > Monitor > Logs > View CloudWatch logs

//- Create a custom domain in API Gateway: api.cruddur.com

- Go to S3 > Buckets > cruddur-uploaded-avatars > Permissions
- Go to 'Cross-origin resource sharing (CORS)' and click 'Edit'
- Enter the following json code and save:
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT"],
    "AllowedOrigins": [
      "https://*.gitpod.io"
    ],
    "ExposeHeaders": [
      "x-amz-server-side-encryption",
      "x-amz-request-id",
      "x-amz-id-2"
    ],
    "MaxAgeSeconds": 3000
  }
]
```
- Create a new directory/file to hold the CORS code: aws/s3/cors.json

- Modify erb/frontend-react-js.env.erb to reflect the API_GATEWAY_ENDPOINT_URL (ie the invoke url)

- Modify frontend-react-js/src/lib/CheckAuth.js

//
+ At some point, we had to zip the contents of aws/lambdas/cruddur-upload-avatar/, which includes function.rb, Gemfile and Gemfile.lock and save the zip as ruby-lambda.zip.
+ Now, in the Lambda > CruddurAvatarUpload, upload as zip and choose ruby-lambda.zip
//

**Setup Lambda Layers**

- Create new directory/file: bin/lambda-layers/ruby-jwt

- Give execute permission to the file

- Run the file to create the lambda layer (consider dir path)

- Go to Lambda > Functions > CruddurAvatarUpload
- Under the 'Code' tab, scroll down to Layers and click 'Add layer'
  - Layer source: Custom layers
  - Custom layers: jwt
  - Choose version
  - Add
- Deploy

- Open the frontend app, go to profile page, Edit profile and try to upload avatar. Then check the logs from the lambda function
- Now go to S3 > Buckets > cruddur-uploaded-avatars and confirm the presence of the image named after the cognito user uuid. Also confirm it is being served in assets.cruddur.com/avatars


**Render Avatar**

- Create the following files: frontend-react-js/src/components/ProfileAvatar.js and frontend-react-js/src/components/ProfileAvatar.css

- Modify frontend-react-js/src/components/ProfileInfo.js