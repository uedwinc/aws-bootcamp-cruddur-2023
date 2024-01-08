# Billing and Architecture

## Architecture Design using Lucidchart

![Cruddur Architecture](_docs/assets/cruddur-architecture.png)

## Setting up Gitpod and Billing

- Launch the github repo on gitpod

### Installing aws cli on gitpod

1. First install in the workspace directory following standard procedure here for linux: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

2. Configure using environmental variables: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html

3. Let's persist the environment variables using:
    ```
    gp env AWS_ACCESS_KEY_ID="your-access-key-id"
    gp env AWS_SECRET_ACCESS_KEY="your-secret-access-key"
    gp env AWS_DEFAULT_REGION="your-region"
    ```

4. Confirm configuration with some basic cli commands:

- To enable aws cli auto-promt, use `aws --cli-auto-prompt`

- To see user info, use `aws sts get-caller-identity`

- To get only a section, say Account, `aws sts get-caller-identity --query Account`

- To remove the parenthesis `aws sts get-caller-identity --query Account --output text`

- If you want to add this to environment variables, `export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)`

- You can save to gitpod env variables using `gp env AWS_ACCOUNT_ID="account-id-here"`

- See https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html for other cli queries

5. Next, configure gitpod with some startup tasks. Update the `.gitpod.yml` file with the following code:

```
tasks:
  - name: aws-cli
    env:
      AWS_CLI_AUTO_PROMPT: on-partial
    init: |
      cd /workspace
      curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
      unzip awscliv2.zip
      sudo ./aws/install
      cd $THEIA_WORKSPACE_ROOT
```

### Configure budget and notification on cli

1. Follow examples here: https://docs.aws.amazon.com/cli/latest/reference/budgets/create-budget.html#examples

2. Create [budget.json](aws/json/budget.json) and [budget-notifications-with-subscribers.json](aws/json/budget-notifications-with-subscribers.json)

3. Set AWS_ACCOUNT_ID env variable

4. Run the following command

```
aws budgets create-budget \
    --account-id $AWS_ACCOUNT_ID \
    --budget file://aws/json/budget.json \
    --notifications-with-subscribers file://aws/json/budget-notifications-with-subscribers.json
```
5. Confirm on the console

### Create Billing Alarm

1. First create an SNS Topic
    ```
    aws sns create-topic --name billing-alarm
    ```

- This will return a TopicARN

2. Next, we'll create a subscription by supplying the TopicARN and our Email

```
aws sns subscribe \
    --topic-arn TopicARN \
    --protocol email \
    --notification-endpoint your@email.com
```

3. Open Amazon SNS on the console

4. You can either confirm subscription on the console or open the mail received for the subscription and confirm.

### Create Alarm

1. Follow doc here: https://repost.aws/knowledge-center/cloudwatch-estimatedcharges-alarm

2. Create an [alarm-config.json](aws/json/alarm-config.json) file

3. Run

    ```
    aws cloudwatch put-metric-alarm --cli-input-json file://aws/json/alarm-config.json
    ```

4. Go to Cloudwatch to confirm