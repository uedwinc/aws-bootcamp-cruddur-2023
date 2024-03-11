# Postgres and RDS

## Provision RDS Instance

Documentation: https://docs.aws.amazon.com/cli/latest/reference/rds/create-db-instance.html

```sh
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username cruddurroot \
  --master-user-password cruddurPassword1 \
  --allocated-storage 20 \
  --availability-zone us-east-2a \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection
```

- You can add this to turn off enhanced monitoring to minimize cost:

```
    --monitoring-interval 0 \
```

Doc: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.Enabling.html

> Creating the RDS instance will take about 10-15 mins

We can temporarily stop an RDS instance for 7 days when we aren't using it.

## Running Postgres Locally

- We alrady set up postgres in docker compose: https://github.com/uedwinc/aws-bootcamp-cruddur-2023/blob/main/journal/week1.md#adding-dynamodb-local-and-postgres

- Run `docker compose up`

- Connect to psql

Connect to psql via the psql client cli tool (remember to use the host flag to specify localhost)

```sh
psql -U postgres --host localhost
```

**Common PSQL commands:**

```sql
\x on -- expanded display when looking at data
\x auto -- expanded display is used automatically
\q -- Quit PSQL
\l -- List all databases
\c database_name -- Connect to a specific database
\dt -- List all tables in the current database
\d table_name -- Describe a specific table
\du -- List all users and their roles
\dn -- List all schemas in the current database
CREATE DATABASE database_name; -- Create a new database
DROP DATABASE database_name; -- Delete a database
CREATE TABLE table_name (column1 datatype1, column2 datatype2, ...); -- Create a new table
DROP TABLE table_name; -- Delete a table
SELECT column1, column2, ... FROM table_name WHERE condition; -- Select data from a table
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...); -- Insert data into a table
UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition; -- Update data in a table
DELETE FROM table_name WHERE condition; -- Delete data from a table
```

### Creating (and dropping) our database

We can use the createdb command to create our database:

https://www.postgresql.org/docs/current/app-createdb.html

```
createdb cruddur -h localhost -U postgres
```
Or just use:

```sh
create database cruddur;
```

```sql
\l
DROP database cruddur;
```

We can create the database within the PSQL client

```sql
CREATE database cruddur;
```

### Import Script

We'll create a new SQL file called `schema.sql`
and we'll place it in `backend-flask/db`

**Add UUID Extension**

We are going to have Postgres generate out UUIDs. This helps to generate random non-serial IDs for database clients.
We'll need to use an extension called:

```sql
CREATE EXTENSION "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; --Use this
```

- We need to add `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";` to schema.sql

- `cd backend-flask`

- Import the script:

```sh
psql cruddur < db/schema.sql -h localhost -U postgres
```

### Create a CONNECTION URI string

CONNECTION URI string is a way of providing all the details that is needed to authenticate to the server. 

Documentation: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING

More documentation here https://stackoverflow.com/questions/3582552/what-is-the-format-for-the-postgresql-connection-string-url shows general format: postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]

```sh
CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
```

We can test this using:

```sh
psql postgresql://postgres:password@localhost:5432/cruddur
```

Now, we can set this as env variable:

```sh
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"

gp env CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
```

- Now, we can authenticate into the server using:

```sh
psql $CONNECTION_URL
```

- We can set this for production using the details used for RDS on AWS

```sh
PROD_CONNECTION_URL="postgresql://cruddurroot:cruddurPassword1@cruddur-db-instance.cbkq6ia0u32o.us-east-2.rds.amazonaws.com:5432/cruddur"
```

- Set this as env variable:

```sh
export PROD_CONNECTION_URL="postgresql://cruddurroot:cruddurPassword1@cruddur-db-instance.cbkq6ia0u32o.us-east-2.rds.amazonaws.com:5432/cruddur"

gp env PROD_CONNECTION_URL="postgresql://cruddurroot:cruddurPassword1@cruddur-db-instance.cbkq6ia0u32o.us-east-2.rds.amazonaws.com:5432/cruddur"
```

Next, we need to write bash scripts to automate some basic sql tasks

- In `backend-flask`, create a folder `bin` and add some files with no extension `db-connect`, `db-create`, `db-drop` and `db-schema-load`

- Give execute rights to user for the four files:

```bash
chmod u+x bin/db-connect

chmod u+x bin/db-create

chmod u+x bin/db-drop

chmod u+x bin/db-schema-load
```

- In `db-connect`:

```bash
#! /usr/bin/bash

psql $CONNECTION_URL
```

- In `db-drop`:

```bash
#! /usr/bin/bash

echo "db-drop"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "DROP DATABASE IF EXISTS cruddur;"
```

- We use SED to create a NO_DB_CONNECTION_URL. This is because CONNECTION_URL authenticates us into the `cruddur` database and we cannot drop a database that we are in.

- In `db-create`:

```bash
#! /usr/bin/bash

echo "db-create"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "CREATE DATABASE IF NOT EXISTS cruddur;"
```

- In `db-schema-load`:

First, we will use the function `realpath` to determine the path of `schema.sql`. Then we will pass this as a variable.

```bash
#! /usr/bin/bash

echo "db-schema-load"

schema_path="$(realpath .)/db/schema.sql"

echo $schema_path

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL cruddur < $schema_path
```

- Make prints nicer

We can make prints for our shell scripts coloured so we can see what we're doing:

https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux


```sh
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"
```

- We will add this to the `db-schema-load`

- Confirm by running the schema

```bash
./bin/db-schema-load
```

- Create our tables

https://www.postgresql.org/docs/current/sql-createtable.html

We'll add these in the `schema.sql`

```sql
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.activities;

CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text,
  handle text,
  cognito_user_id text,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

```sql
CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_uuid UUID NOT NULL,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

- To create the tables, run `db-schema-load`

```bash
./bin/db-schema-load
```

Next, we want to manually add seed values to the tables/database.

- Create a `db-seed` and `seed.sql` files

- Give execute rights to user for `db-seed`

```bash
chmod u+x bin/db-seed
```

- In `db-seed`, enter:

```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-seed"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

seed_path="$(realpath .)/db/seed.sql"

echo $seed_path

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL cruddur < $seed_path
```

- In `seed.sql`, enter:

```sql
INSERT INTO public.users (display_name, handle, cognito_user_id)
VALUES
  ('Andrew Brown', 'andrewbrown' ,'MOCK'),
  ('Andrew Bayko', 'bayko' ,'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'andrewbrown' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )
```

- To add the seed data, run `db-seed`

```sh
./bin/db-seed
```

- Let's try to see the seed data in the database:

> Connect to the database
```sh
./bin/db-connect
```

> `\dt` to see tables

> `SELECT * FROM activities;`
Quit with `q`

> Do `\x on` to activate expanded display or `\x auto` to activate automatic use of expanded display

> Now, you can do: `SELECT * FROM activities;`

> Confirm that uuid and timestamps are correctly generated and set


See what connections we are using

- Create a `db-sessions` file in the `bin` directory

- Make the file executable

```sh
chmod u+x bin/db-sessions
```

```sh
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-sessions"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

NO_DB_URL=$(sed 's/\/cruddur//g' <<<"$URL")
psql $NO_DB_URL -c "select pid as process_id, \
       usename as user,  \
       datname as db, \
       client_addr, \
       application_name as app,\
       state \
from pg_stat_activity;"
```

> We could have idle connections left open by our Database Explorer extension, try disconnecting and checking again the sessions

- Run the script

```sh
./bin/db-sessions
```

Easily setup (reset) everything for our database

- Create a `db-setup` file

- Make it executable

```sh
chmod u+x bin/db-setup
```

```sh
#! /usr/bin/bash
-e # stop if it fails at any point

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-setup"
printf "${CYAN}==== ${LABEL}${NO_COLOR}\n"

bin_path="$(realpath .)/bin"

source "$bin_path/db-drop"
source "$bin_path/db-create"
source "$bin_path/db-schema-load"
source "$bin_path/db-seed"
```

- This is only useful in development, and not production

- Run the script

```sh
./bin/db-setup
```

**Setup Driver for Postgres**

https://www.psycopg.org/psycopg3/

https://www.psycopg.org/psycopg3/docs/basic/install.html

We'll add the following to our `requirments.txt`

```
psycopg[binary]
psycopg[pool]
```

```sh
pip install -r requirements.txt
```

**DB Object and Connection Pool**

- Create a new file `lib/db.py`

```py
from psycopg_pool import ConnectionPool
import os

def query_wrap_object(template):
  sql = '''
  (SELECT COALESCE(row_to_json(object_row),'{}'::json) FROM (
  {template}
  ) object_row);
  '''

def query_wrap_array(template):
  sql = '''
  (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
  {template}
  ) array_row);
  '''

connection_url = os.getenv("CONNECTION_URL")
pool = ConnectionPool(connection_url)
```

- We need to add CONNECTION_URL as env var in docker-compose for our backend-flask application:

```yml
  backend-flask:
    environment:
      CONNECTION_URL: "${CONNECTION_URL}"
```

In our home_activities we'll do `from lib.db import pool`. Then, we'll replace our mock endpoint with real api call:

```py
from lib.db import pool, query_wrap_array

      sql = query_wrap_array("""
      SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
      """)
      print(sql)
      with pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(sql)
          # this will return a tuple
          # the first field being the data
          json = cur.fetchone()
      return json[0]
```

- Set the CONNECTION_URL in docker-compose to reflect db rather than localhost IP. You can copy the full value from the env var of the backend container shell

```
postgresql://postgres:password@db:5432/cruddur
```

- Try to load cruddur on the browser and check the logs for backend
- Cruddur should load the seed data

## Establish a connection to the Postgres database on AWS

- Start up the RDS instance previously created

- Do `echo $PROD_CONNECTION_URL` to confirm it is properly set

- Next, go to RDS on AWS and modify the inbound rules of the associated security group.

- Choose port as Postgres (port number = 5432).

- For the IP address, we need to put in our Gitpod IP address. This is gotten with the command:

  ```sh
  curl ifconfig.me
  ```

  - We can set this as env variable using:

  ```sh
  export GITPOD_IP=$(curl ifconfig.me)
  ```

  - You can do `echo $GITPOD_IP` to confirm

  - Copy the IP and paste in the security group configuration. It will auto append `/32` indicating one IP address

- You can set the description as "GITPOD" (all caps). Then create rule.

- Now, you can connect to the database using:

```sh
psql $PROD_CONNECTION_URL
```

- Do `\l` to see any list of databases

- Whenever we launch Gitpod, we'll have a new IP address. This means we will need to update the IP address on our RDS security group at every launch of Gitpod.

- The inbound rule we defined for Postgres has a 'Security group rule ID'. The security group itself has a 'Security group ID'. We'll set these two values as env variables since they are constants unless deleted.

```sh
export DB_SG_ID="sg-***"
gp env DB_SG_ID="sg-***"

export DB_SG_RULE_ID="sgr-***"
gp env DB_SG_RULE_ID="sgr-***"
```

- Now, whenever we need to modify the inbound rule to use current Gitpod IP, we can run the command:

```sh
aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
```

- We can write a script for the above operation. In backend-flask/bin, create a new file _rds-update-sg-rule_ and set it as a bash script to run the 'aws ec2 modify-security-group-rules' command

> Documentation: https://docs.aws.amazon.com/cli/latest/reference/ec2/modify-security-group-rules.html#examples

- Add execute rights:

```sh
chmod u+x /bin/rds-update-sg-rule
```

- We want this script to run at startup of Gitpod. So, we will add a command step for postgres in the _.gitpod.yml_ file

```yml
    command: |
      export GITPOD_IP=$(curl ifconfig.me)
      source "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule"
```

- Next, we need to update 'db-connect' and 'db-schema-load' bash scripts for production:

```sh
if [ "$1" = "prod" ]; then
  echo "Running in production mode"
else
  echo "Running in development mode"
fi
```

- Now, try to run the script to establish connection (in backend-flask directory):

```sh
./bin/db-connect prod
```

- Edit the CONNECTION_URL in _docker-compose_ for production

```yml
      CONNECTION_URL: "${PROD_CONNECTION_URL}"
```

- Do compose up

- Run the script to load schema

```sh
./bin/db-schema-load prod
```

- Try to access frontend cruddur on the browser. This should not have any data as we don't have any data on the system.

## Setup Cognito post confirmation lambda

- We need to implement a custom authorizer for cognito. This is necessary because in setting up the user table (seed.sql), it requires a cognito user id. This will help verify a user at sign-up.

1. Create a Lambda function

- Sign into AWS, and go to Lambda and create a function
  - Check Author from scratch
  - Function name - cruddur-post-confirmation
  - Runtime - Python 3.8
  - Architecture - x86_64
  - Under permissions, check 'Create a new role with basic Lambda permissions'
  - Leave rest unchecked, and create function.

//Create Lambda in same vpc as rds instance//

- Create a new folder for Lambda function (/aws/lambdas/) and create a Lambda function python file ('cruddur-post-confirmation.py) matching the name we gave the lambda function

- Paste the following code in the function:

```py
import json
import psycopg2
import os

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    print('userAttributes')
    print(user)

    user_display_name  = user['name']
    user_email         = user['email']
    user_handle        = user['preferred_username']
    user_cognito_id    = user['sub']
    try:
      print('entered-try')
      sql = f"""
         INSERT INTO public.users (
          display_name, 
          email,
          handle, 
          cognito_user_id
          ) 
        VALUES(%s,%s,%s,%s)
      """
      print('SQL Statement ----')
      print(sql)
      conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
      cur = conn.cursor()
      params = [
        user_display_name,
        user_email,
        user_handle,
        user_cognito_id
      ]
      cur.execute(sql,*params)
      conn.commit() 

    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
    finally:
      if conn is not None:
          cur.close()
          conn.close()
          print('Database connection closed.')
    return event
```

NB: In schema.sql, add column for email and do schema-load again

- Paste the lambda code in the 'Code' section for the created Lambda function on AWS and click 'Deploy'

- Next, under 'Configuration', go to 'Environment variables' and edit to add a new variable. Create an env with name as 'CONNECTION_URL' and value as the "PROD_CONNECTION_URL" value from Gitpod env. Then save.

- Next, under 'Configuration', go to 'Permissions'. Click the Lambda role. Under 'Permissions policies', it should have a basic default AWSLambdaBasicexecutionRole. Under 'Add permissions', Click to create a custom policy. Select JSON and input the following code:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeNetworkInterfaces",
        "ec2:CreateNetworkInterface",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeInstances", #This line is not necessary
        "ec2:AttachNetworkInterface" #This line is not necessary
      ],
      "Resource": "*"
    }
  ]
}
```

- Next, create with the following details: Name: AWSLambdaVPCAccessExecutionRole; Description: So AWS Lambda can create a network card

- Attach the policy and permissions to the Lambda function.

- Now, under 'Configuration' > 'permissions', the 'Resource summary' should have an Amazon EC2 reource added along with the Cloudwatch trigger added previously.

- Still under 'Configuration', go to VPC. Edit and specify the VPC and other network protocols. You can use the defaults if that is where RDS was created since that will contain the security group with Postgres port opened.


- In the 'Code' section, scroll down and Add a layer.

  ```md
  **## DOCUMENTATION**


  ### For Development
  https://github.com/AbhimanyuHK/aws-psycopg2

  This is a custom compiled psycopg2 C library for Python. Due to AWS Lambda missing the required PostgreSQL libraries in the AMI image, we needed to compile psycopg2 with the PostgreSQL libpq.so library statically linked libpq library instead of the default dynamic link.

  `EASIEST METHOD`

  Some precompiled versions of this layer are available publicly on AWS freely to add to your function by ARN reference.

  https://github.com/jetbridge/psycopg2-lambda-layer

  - Just go to Layers + in the function console and add a reference for your region

  Example: `arn:aws:lambda:ca-central-1:898466741470:layer:psycopg2-py38:1` 


  `ALTERNATIVE`

  Alternatively you can create your own development layer by downloading the psycopg2-binary source files from https://pypi.org/project/psycopg2-binary/#files

  - Download the package for the lambda runtime environment: [psycopg2_binary-2.9.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl](https://files.pythonhosted.org/packages/36/af/a9f06e2469e943364b2383b45b3209b40350c105281948df62153394b4a9/psycopg2_binary-2.9.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl)

  - Extract to a folder, then zip up that folder and upload as a new lambda layer to your AWS account

  ### For Production

  Follow the instructions on https://github.com/AbhimanyuHK/aws-psycopg2 to compile your own layer from postgres source libraries for the desired version.
  ```

- Check 'Specify an ARN' and specify one for your region from https://github.com/jetbridge/psycopg2-lambda-layer

- 'Verify' and 'Add'

- Next, we need to add trigger to the Lambda function in cognito

- Go to Cognito. Click on the user pool created.

- Under, 'User pool properties' tab, click on 'Add Lambda trigger'
  - Trgger type: Sign-up
  - Sign-up: Post confirmation trigger
  - Assign Lambda function: Select 'cruddur-post-confirmation'
  - Finally, click on 'Add Lambda trigger'

- Try sign-up on cruddur

- On the lambda page, under 'Monitor' tab, select 'Logs' and view the cloudwatch logs for the Lambda trigger

- If any errors occur, make sure to delete the user in cognito user pool before retrying while debugging

- On the terminal, connect to the production database: `./bin/db-connect prod`

- Do: `SELECT * FROM USERS;` to view the newly created user table. You can do `\x on` for expanded view and run the command again.