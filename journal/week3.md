# Decentralized Authentication

## Provision Cognito User Group

Using the AWS Console we'll create a Cognito User Group

- Go to Amazon Cognito and create a user pool
  - Provider types: Cognito user pool
  - Cognito user pool sign-in options: Email
  - Password policy mode: Cognito defaults
  - MFA enforcement: No MFA
  - Check Enable self-service account recovery
  - Delivery method for user account recovery messages: Email only
  - Check Enable self-registration
  - Check Allow Cognito to automatically send messages to verify and confirm
  - Attributes to verify: Send email message, verify email address
  - Check Keep original attribute value active when an update is pending
  - Active attribute values when an update is pending: Check Email address
  - Additional required attributes: Select 'name' and 'preferred_username'
  - Email provider: Send email with Cognito
  - User pool name: cruddur-user-pool
  - App type: Public client
  - App client name: cruddur
  - Client secret: Don't generate a client secret
  - Review and create user pool

## Install AWS Amplify

- See documentation: https://docs.amplify.aws/react/build-a-backend/auth/

```sh
cd frontend-react-js
```

```sh
npm i aws-amplify --save
```

- This adds `aws-amplify` to `package.json` and modifies `package-lock.json`

## Configure Amplify

We need to hook up our cognito pool to our code in the `App.js`

```js
import { Amplify } from 'aws-amplify';

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_identity_pool_id": process.env.REACT_APP_AWS_COGNITO_IDENTITY_POOL_ID, //Remove this as we are not using identity pool
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_APP_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});
```

- Go to `docker-compose.yml` and configure the following as environment variables for frontend-react-js

```
REACT_APP_AWS_PROJECT_REGION
REACT_APP_AWS_COGNITO_REGION
REACT_APP_AWS_USER_POOLS_ID
REACT_APP_CLIENT_ID
```