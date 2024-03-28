# Deploying Containers

## Test RDS Connection

Add this `test` script into `db` so we can easily check our connection from our container.

```py
#!/usr/bin/env python3

import psycopg
import os
import sys

connection_url = os.getenv("CONNECTION_URL")

conn = None
try:
  print('attempting connection')
  conn = psycopg.connect(connection_url)
  print("Connection successful!")
except psycopg.Error as e:
  print("Unable to connect to the database:", e)
finally:
  conn.close()
```

- Add execute permission for this file

```sh
chmod u+x /backend-flask/bin/db/test
```

- If you want to test this in development, you need to temporarily change "CONNECTION_URL" to "PROD_CONNECTION_URL"

```sh
./bin/db/test
```

## Task Flask Script

We'll add a health-check endpoint for our flask app in `app.py`

```py
@app.route('/api/health-check')
def health_check():
  return {'success': True}, 200
```

We'll create a new bin script at `bin/flask/health-check`

- Add execute permission for this file

```sh
chmod u+x /bin/flask/health-check
```

- Run the script

```sh
./bin/flask/health-check
```

- This should return a 'Connection Refused' error

## Create CloudWatch Log Group

```sh
aws logs create-log-group --log-group-name "cruddur"

aws logs put-retention-policy --log-group-name "cruddur" --retention-in-days 1
```

- You can confirm on the console (CloudWatch > Log groups)

## Create ECS Cluster

```sh
aws ecs create-cluster \
--cluster-name cruddur \
--service-connect-defaults namespace=cruddur
```

- You can confirm this on the ECS console

## Preparing the Containers

## Create ECR repo and push image

### For Base-image python

**Create the repository**

```sh
aws ecr create-repository \
  --repository-name cruddur-python \
  --image-tag-mutability MUTABLE
```

> Login to ECR

```sh
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```

**Set URL**

```sh
export ECR_PYTHON_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/cruddur-python"
echo $ECR_PYTHON_URL
```

**Pull Image**

```sh
docker pull python:3.10-slim-buster
```

- You can confirm using:

```sh
docker images
```

**Tag Image**

```sh
docker tag python:3.10-slim-buster $ECR_PYTHON_URL:3.10-slim-buster
```

- You can confirm using:

```sh
docker images
```

**Push Image**

```sh
docker push $ECR_PYTHON_URL:3.10-slim-buster
```

- You can confirm on the ECR console

### For Flask

- In the flask dockerfile, replace the dockerhub image name in the 'From' section with the URI of the ECR image on AWS

**Create the repository**

```sh
aws ecr create-repository \
  --repository-name backend-flask \
  --image-tag-mutability MUTABLE
```

- You should be logged into ECR already from the previous login command

**Set URL**

```sh
export ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
echo $ECR_BACKEND_FLASK_URL
```

**Build Image**

- Make sure you are in the backend-flask directory

```sh
docker build -t backend-flask .
```

**Tag Image**

- Remember to put the :latest tag on the end

```sh
docker tag backend-flask:latest $ECR_BACKEND_FLASK_URL:latest
```

**Push Image**

```sh
docker push $ECR_BACKEND_FLASK_URL:latest
```

### For Frontend React

- Create a new Dockerfile, `frontend-react-js/Dockerfile.prod`

- Create new file, `frontend-react-js/nginx.conf` to serve as light-weight webserver

- Edit `.gitignore` to ignore the build aoutput


- Run a dry build to check

```sh
cd frontend-react-js

npm run build
```

- Edit /pages/ConfirmationPage.js and /pages/RecoverPage.js to remove error
- Change all setCognitoErrors to setErrors
- Run build again

**Create Repo**

```sh
aws ecr create-repository \
  --repository-name frontend-react-js \
  --image-tag-mutability MUTABLE
```

- Make sure you are logged into ECR

**Set URL**

```sh
export ECR_FRONTEND_REACT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/frontend-react-js"
echo $ECR_FRONTEND_REACT_URL
```

**Build Image**

```sh
docker build \
--build-arg REACT_APP_BACKEND_URL="https://4567-$GITPOD_WORKSPACE_ID.$GITPOD_WORKSPACE_CLUSTER_HOST" \ #Replace this with "http://loadbalancer-DNS-name:4567"
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="ca-central-1_CQ4wDfnwc" \
--build-arg REACT_APP_CLIENT_ID="5b6ro31g97urk767adrbrdj1g5" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```

**Tag Image**

```sh
docker tag frontend-react-js:latest $ECR_FRONTEND_REACT_URL:latest
```

**Push Image**

```sh
docker push $ECR_FRONTEND_REACT_URL:latest
```

If you want to run and test it

```sh
docker run --rm -p 3000:3000 -it frontend-react-js 
```

## Register Task Defintions

### Passing Senstive Data to Task Defintion

https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data.html 
https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-ssm-paramstore.html

- We will be setting various sensitive data up in AWS Systems Manager
- Make sure to have set all as env variables first. 

The only one left is OTEL_EXPORTER_OTLP_HEADERS, so do:

```sh
export OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=${HONEYCOMB_API_KEY}"

echo $OTEL_EXPORTER_OTLP_HEADERS
```

- Now, run the following lines of code individually to set them up:

```sh
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_ACCESS_KEY_ID" --value $AWS_ACCESS_KEY_ID
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY" --value $AWS_SECRET_ACCESS_KEY
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/CONNECTION_URL" --value $PROD_CONNECTION_URL
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" --value $ROLLBAR_ACCESS_TOKEN
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" --value "x-honeycomb-team=$HONEYCOMB_API_KEY"
```

- Confirm that all are set on the console at AWS Systems Manager > Parameter store > My parameters

### Create Task and Exection Roles for Task Defintion

**Create ExecutionRole**

- Create role `aws/policies/service-assume-role-execution-policy.json`

```sh
aws iam create-role \    
--role-name CruddurServiceExecutionRole  \   
--assume-role-policy-document "file://aws/policies/service-assume-role-execution-policy.json"
```

- Create policy `aws/policies/service-execution-policy.json`

```sh
aws iam put-role-policy \
--role-name CruddurServiceExecutionRole \
--policy-name CruddurServiceExecutionPolicy \
--policy-document "file://aws/policies/service-execution-policy.json"
```

- The above should attach the policy to the CruddurServiceExecutionRole as specified.

- If not, use the below command to attach it

- Attach role policy:

```sh
aws iam attach-role-policy \
--policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
--role-name CruddurServiceExecutionRole
```

**Create TaskRole**

- Create role

```sh
aws iam create-role \
    --role-name CruddurTaskRole \
    --assume-role-policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[\"sts:AssumeRole\"],
    \"Effect\":\"Allow\",
    \"Principal\":{
      \"Service\":[\"ecs-tasks.amazonaws.com\"]
    }
  }]
}"
```

- Create policy (this will attach the policy to the CruddurtaskRole as defined)

```sh
aws iam put-role-policy \
  --policy-name SSMAccessPolicy \
  --role-name CruddurTaskRole \
  --policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[
      \"ssmmessages:CreateControlChannel\",
      \"ssmmessages:CreateDataChannel\",
      \"ssmmessages:OpenControlChannel\",
      \"ssmmessages:OpenDataChannel\"
    ],
    \"Effect\":\"Allow\",
    \"Resource\":\"*\"
  }]
}"
```

- Attach the following policies:

```sh
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess --role-name CruddurTaskRole
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess --role-name CruddurTaskRole
```

- Confirm all the permissions on the console

### Create task Definition

- Create a new folder `/aws/task-definitions` and add new files 'backend-flask.json' and 'frontend-react-js.json'

### Register Task Defintion

```sh
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json
```

```sh
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/frontend-react-js.json
```

- Confirm on the console; ECS > Task definitions

## Export VPC and Subnets

```sh
export DEFAULT_VPC_ID=$(aws ec2 describe-vpcs \
--filters "Name=isDefault, Values=true" \
--query "Vpcs[0].VpcId" \
--output text)
echo $DEFAULT_VPC_ID
```

```sh
export DEFAULT_SUBNET_IDS=$(aws ec2 describe-subnets  \
 --filters Name=vpc-id,Values=$DEFAULT_VPC_ID \
 --query 'Subnets[*].SubnetId' \
 --output json | jq -r 'join(",")')
echo $DEFAULT_SUBNET_IDS
```

## Create Security Group

```sh
export CRUD_SERVICE_SG=$(aws ec2 create-security-group \
  --group-name "crud-srv-sg" \
  --description "Security group for Cruddur services on ECS" \
  --vpc-id $DEFAULT_VPC_ID \
  --query "GroupId" --output text)
echo $CRUD_SERVICE_SG
```

**Authorize port 80 on the security group**

```sh
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --protocol tcp \
  --port 4567 \
  --cidr 0.0.0.0/0
```

> if we need to get the sg group id again

```sh
export CRUD_SERVICE_SG=$(aws ec2 describe-security-groups \
  --filters Name=group-name,Values=crud-srv-sg \
  --query 'SecurityGroups[*].GroupId' \
  --output text)
```

## Create Services

- Create service file for backend-flask `aws/json/service-backend-flask.json`

- Create service file for frontend-react-js `aws/json/service-frontend-react-js.json`

- Create load balancer first (See below)

- Create service:

```sh
aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json
```

```sh
aws ecs create-service --cli-input-json file://aws/json/service-frontend-react-js.json
```

- Confirm that the services are created in ECS on the console

- Go to Load balancer > Target groups > 
- Click on the target group name. Under the targets tab, check health checks

- Authorize port 3000 in the security group of the frontend service and attach the load balancer security group as source

- Copy the load balancer DNS name and open on browser with port 3000 to load frontend

- You can debug issues like health-check and others by shelling into the container
- Health-check may take time to show healthy

### Connection to Container Shell via Sessions Manaager (Fargate)
 
https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-linux
https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-verify

Install for Ubuntu
```sh
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
sudo dpkg -i session-manager-plugin.deb
```

Verify its working
```sh
session-manager-plugin
```

Connect to the container
 ```sh
aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task dceb2ebdc11c49caadd64e6521c6b0c7 \
--container backend-flask \
--command "/bin/bash" \
--interactive
```

Test Flask App is running

```sh
./bin/flask/health-check
```

- Update `.gitpod.yml` file to install session manager plugin

- Create a file to connect to backend container; `/bin/ecs/connect-to-backend-flask`

- Create a file to connect to frontend container; `/bin/ecs/frontend-react-js`

- Give execute permission:

```sh
chmod u+x /bin/ecs/connect-to-backend-flask

chmod u+x /bin/ecs/connect-to-frontend-react-js
```

- Connect

```sh
./bin/ecs/connect-to-backend-flask
```

**Check Service IP Health-check**

- You can get the IP address of the service from the 'Task' section on ECS or 'Network interfaces' section on EC2 dashboard

- Check the endpoint: `IP/api/health-check` #Can't use this if load balancer is attached

- Copy load balancer DNS and check on browser with the endpoint `/api/health-check`

**Update RDS SG to allow access for the last security group**

```sh
aws ec2 authorize-security-group-ingress \
  --group-id $DB_SG_ID \
  --protocol tcp \
  --port 5432 \
  --source-group $CRUD_SERVICE_SG \
  --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=BACKENDFLASK}]'
```

- Now, try to connect to the database (Inside the backend-flask container shell)

```sh
./bin/db/test
```

- Check the endpoint: `IP/api/activities/home`

## Create Load Balancer

- Select Application load balancer and click 'Create'
    - Load balancer name: cruddur-alb
    - Scheme: Internet-facing
    - Ip address type: IPv4
    - VPC: Default
    - Mappings: Check all subnets
    - Remove attached security group and create a new one:
        - Name: cruddur-alb-sg
        - Description: cruddur-alb-sg
        - Inbound rules: HTTP and HTTPS (from anywhere or your specific IP)
        //Ignore for now, but if the listner is having issues, you will need to open ports 4567 and maybe 3000//
        - Create
        - Go to the service security group (crud-srv-sg) and allow inbound rule access for 'cruddur-alb-sg'
            - Port range: 4567
            - Description: CruddurALB
            - Delete the original inbound rule so that traffic is routed only through the load balancer
    - Select the load balancer security group (cruddur-alb-sg)
    - Listners and routing:
        - Protocol: HTTP
        - Port: 4567
        - Default action: Select target group. We don't have one yet so we select 'Create target group'
            - Choose target type: IP addresses
            - Target group name: cruddur-backend-flask-tg
            - Protocol: HTTP
            - Port: 4567
            - IP address type: IPv4
            - VPC: default
            - Protocol version: HTTP1
            - Health check:
                - Health check protocol: HTTP
                - Health check path: `/api/health-check`
            - Advanced health check settings:
                - Port: traffic port
                - Healthy threshold: 3
                - Unhealthy threshold: 2
                - Timeout: 5
                - Interval: 30
                - Success codes: 200
            - Next
            - Ignore register targets and create
        - Select the newly created target group
    - Add a listner for the frontend
        - Protocol: HTTP
        - Port: 3000
        - Default action: Select target group. We don't have one yet so we select 'Create target group'
            - Choose target type: IP addresses
            - Target group name: cruddur-frontend-react-js
            - Protocol: HTTP
            - Port: 3000
            - IP address type: IPv4
            - VPC: default
            - Protocol version: HTTP1
            - Health check: (ignore)
                - Health check protocol: HTTP
                - Health check path: /
            - Advanced health check settings:
                - Port: traffic port
                - Healthy threshold: 3
                - Unhealthy threshold: 2
                - Timeout: 5
                - Interval: 30
                - Success codes: 200
            - Next
            - Ignore register targets and create
        - Select the newly created target group
    - Create the load balancer


> Use this command to generate the skeleton for any cli command specified: `aws cli create-service --generate-cli-skeleton`. Here, create-service is the specified command.


# Custom Domain

- Go to Route53
- Create a hosted zone (eg app.cruddur.com) and copy the name servers attached

- Go to the domain name servers of your domain and update/change the nameservers to the hosted zone nameservers

- To attach an SSL certificate, go to ACM (certificate manager)
- Request a certificate (Request a public certificate)
  - Fully qualified domain name: cruddur.com
  - Choose Add another name to this certificate: *.cruddur.com
  - Validation method: DNS validation
  - Key algorithm: RSA 2048 (defaut)
  - Request

- Refresh the Certificates page. 
- Click into the certificate. Wait for success.
- Under Domains, click Create records in Route53
- Make sure everything is checked and click Create. 
- Confirm new record on Route53

- In EC2, go to Load balancer
- Check the load balancer created
- Go to Listeners. Add listener
  - Protocol: HTTP, Port: 80
  - Default Actions: Under Add action dropdown, select Redirect
  - Protocol: HTTPS, Port: 443
  - Status code: 302 Found
  - Add
- Add another listener
  - Protocol: HTTPS, Port: 443
  - Default Actions: Under Add action dropdown, select Forward
  - Target group: cruddur-frontend-react-js
  - Default SSL/TLS certificate: Select the ACM certificate
  - Add
- You can delete the two previous other listeners

- Under Listeners
- Check the HTTPS:443, under Actions tab, Manage rules
- There should be a default that goes to the frontend-react-js
- Click on the + button to add, then click Insert rule
  - Add condition: Host header...     - Value: api.cruddur.com
  - Add Action: Forward               - Target group: cruddur-backend-flask-tg
  - Save

- Point Route53 to the load balancer
- Go to Route53 > Hosted zones
- click into the cruddur.com hosted zone
- Create a record
  - Record name: (leave empty so it is naked and goes to cruddur.com or you can add "app" in my case)
  - Record type: A - Routes traffic to...
  - Toggle 'Alias'
  - Route traffic to: Alias to application and classic load balancer
  - Choose 'Region' and 'Load balancer'
  - Simple routing
  - Evaluate target health on
  - Create record

- Create a record
  - Record name: api
  - Record type: A - Routes traffic to...
  - Toggle 'Alias'
  - Route traffic to: Alias to application and classic load balancer
  - Choose 'Region' and 'Load balancer'
  - Simple routing
  - Evaluate target health on
  - Create record

**Confirm**

```sh
ping api.cruddur.com

curl api.cruddur.com/api/health-check
```

- Confirm address on browser: `api.cruddur.com/api/health-check` (possibly a different browser like firefox)
- Also check if the connection is secure on the browser

- You can edit the backend task definition. In the 'environment' section, change 'FRONTEND_URL' value from * to https://cruddur.com and 'BACKEND_URL' value from * to https://api.cruddur.com

- Update the task definition: `aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json`

Using previous commands (for frontend):
- Login to ECR
- Set URL
- Build image:
  - Change the backend_url to "https://api.cruddur.com"
- Tag image
- Push image

- Go to ECS on the console
- Click the cruddur cluster
- Under services, check backend-flask and click update
  - Check force deployment
  - Choose latest revision
  - Update
- Under services, check frontend-react-js and click update
  - Check force deployment
  - Confirm latest revision
  - Update
- Wait for it to update

- Go to EC2 > Load balancing > Target groups
- Confirm that both target groups are healthy

- You can check health-check url and cruddur.com on the browser
- Sign-in and create cruds. Also check messages section.

# Securing Flask

https://flask.palletsprojects.com/en/2.3.x/debugging/

- Edit inbound rules for cruddur-alb-sg to only work for my IP (for now)
- Leave only ports for HTTPS and HTTP and allow only My IP

- In backend-flask/ directory, create a new dockerfile (/Dockerfile.prod) for production and edit the original dockerfile to allow debugging

`/backend-flask/Dockerfile`
```Dockerfile
FROM 387543059434.dkr.ecr.ca-central-1.amazonaws.com/cruddur-python:3.10-slim-buster

# Inside Container
# make a new folder inside container
WORKDIR /backend-flask

# Outside Container -> Inside Container
# this contains the libraries want to install to run the app
COPY requirements.txt requirements.txt

# Inside Container
# Install the python libraries used for the app
RUN pip3 install -r requirements.txt

# Outside Container -> Inside Container
# . means everything in the current directory
# first period . - /backend-flask (outside container)
# second period . /backend-flask (inside container)
COPY . .

EXPOSE ${PORT}

# CMD (Command)
# python3 -m flask run --host=0.0.0.0 --port=4567
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567", "--debug"]
```

- Create a script to log into ECR `/bin/ecr/login`

- Add execute permission and login

```sh
chmod u+x /bin/ecr/login

./bin/ecr/login
```

- Create the following directories: `/bin/docker/build/`(files here: backend-flask-prod, frontend-react-js-prod), `/bin/docker/push/` (files here: backend-flask-prod), `/bin/docker/run/` (files here: backend-flask-prod)

- Give execute permissions

- Build the production image

```sh
./bin/docker/build/backend-flask-prod
```

- Set URL, tag and push

```sh
./bin/docker/push/backend-flask-prod
```

- Now, we need to update task definition on ECS and force deployment
- Create a new file: `/bin/ecs/force-deploy-backend-flask`

- Give execute permissions

- Execute

```sh
./bin/ecs/force-deploy-backend-flask
```

- Restructure bin/ directory
  - Move the /bin dir up one level outside backend-flask/

- Build the frontend-react-js

```sh
./bin/docker/build/frontend-react-js-prod
```

- Create push script for frontend-react-js

- Make the script executable

- Execute the script

```sh
./bin/docker/push/frontend-react-js-prod
```

- Now, we need to update task definition on ECS and force deployment
- Create a new file: `/bin/ecs/force-deploy-frontend-react-js`

- Give execute permissions

- Execute

```sh
./bin/ecs/force-deploy-frontend-react-js
```

- Confirm the following url paths on browser

https://api.cruddur.com
https://api.cruddur.com/api/health-check
https://api.cruddur.com/api/activities/home

- Type in a wrong endpoint to be sure it doesn't return a typeerror (instead an internal server error maybe) as that debug mode should not be seen from customer end

- If you encounter any errors, you can also check rollbar for error logging

> Incase you want to reduce spend and stop your running containers, go to ECS, check the service and click 'update'. Then change the 'Desired tasks' to zero(0). Then, when you stop your tasks, it won't start another one.

- Restructure the /bin directory

- Create an sql script to kill all connections: /backend-flask/db/kill-all-connections.sql
- Create a script to run the kill all db connections: /bin/db/kill-all

# Implement Cognito Refresh Token

- Edit frontend-react-js/src/lib/CheckAuth.js
- Edit HomeFeedPage.js, MessageGroupNewPage.js, MessageGroupPage.js, MessageGroupsPage.js
- Edit MessageForm.js

# Configure Container Insights

- Configure xray in task-definitions/backend-flask.json

- Create a bin/backend/register and bin/frontend/register scripts to register task definitions

- Give execute rights to the files

- Run the register files

- Deploy /bin/backend/deploy

- Confirm that all the services are running on ECS. Click into all to see the various tasks

- Create env files to hold our environment variables
  - First, we need to store the env variables in env.erb files: erb/backend-flask.env.erb and erb/frontend-react-js.env.erb
  - Next, we need to create ruby scripts that generate the envs: /bin/backend/generate-env and /bin/frontend/generate-env
  - When these files are run, they generate a `.env` file. Let's ignore that in .gitignore
  - Give execute permission to the generate-env files
  - Add command to generate-env at startup in .gitpod.yml file
  - Remove env variables from docker-compose and reference generated env file path

- Create bin/frontend/run script

- Edit docker-compose networks

- Create bin/busybox to be used for debugging
  - Give execute permission
  - Run the file
  - While connected, go to another tab and run `docker network inspect cruddur-net`
  - Search for the busybox service (just look through for a weirdly named service)
  - In the shell tab of busybox, run some commands to be debug: `ping xray-daemon`, `telnet xray-daemon 2000`

- Move health-check file to the backend-flask/bin directory

- Now, to turn on container insights, go to ECS > Custers > cruddur
  - Click 'Update cluster'
  - Expand 'Monitoring' tab and check 'Use container insights'
  - Click 'Update'

- Go to CloudWatch > Container insights

# Corectly Implementing Timezones for ISO 8601

- Edit bin/ddb/seed, backend-flask/lib/ddb.py
- Create a new file: frontend-react-js/src/lib/DateTimeFormats.js
- Edit frontend-react-js/src/components/MessageItem.js, frontend-react-js/src/components/MessageItem.css, frontend-react-js/src/components/MessageGroupItem.js, frontend-react-js/src/components/ActivityContent.js