# DynamoDB and Serverless Caching

---
> Setting up

+ Business Use Case 1:- Create an Amazon DynamoDB

- Make sure you are in your correct region
- On AWS console, search and click "DynamoDB"
- Click 'Create table'
- Give the table a name
- Specify 'Partition key'
- Define 'Sort key' or leave empty
- For table settings, you can choose Default settings or Customize settings
- Add tags and Create table
- Click on the table name to go into it
- Click on 'Explore table items' to see what the table looks like
- You can use 'create item' to create some items by entering a value for the attribute partition key
- So we have created database table which development can access.
- This can be accessed using the regional endpoint (https://docs.aws.amazon.com/general/latest/gr/rande.html#regional-endpoints) pattern eg https://dynamodb.us-west-2.amazonaws.com/table-name

+ Business Use Case 2:- Add an Amazon DynamoDB Accelerator (DAX)

- In the DynamoDB console, go to DAX > Clusters
- Give the cluster a name
- You can keep all other settings as defaults to minimize cost and click 'Next'
- Configure VPC and go Next
- Define IAM role. Specify the DynamoDB table it should access. Leave Encriptions turned on and go Next.
- For Parameter group, you can choose Existing. Leave all else as defaults, add tags and click Next.
- Review and Create cluster
- Consider cost (clusters cost money)

> Security Best Practices

1. Server side - AWS

2. Client application side

---

## Implementation of DynamoDB

- In _requirements.txt_, add `boto3`

- Now install in backend-flask directory:

```sh
pip install -r requirements.txt
```

- Do `docker-compose up` to start up DynamoDB local

- Cleanup the bin dir: Move all the different scripts into their own specialized new directories and rename where necessary. We will need to adjust filepath references within the scripts

- Create a ddb directory in bin for DynamoDB scripts
- Add the following files: schema-load, seed, drop, list-tables

Docs for DynamoDB with boto3 SDK: 
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
- https://docs.aws.amazon.com/code-library/latest/ug/python_3_dynamodb_code_examples.html

- In **/ddb/schema-load**, provision script to create table:

```py
#!/usr/bin/env python3

import boto3
import sys

attrs = {
  'endpoint_url': 'http://localhost:8000'
}

if len(sys.argv) == 2:
  if "prod" in sys.argv[1]:
    attrs = {}

ddb = boto3.client('dynamodb',**attrs)

table_name = 'cruddur-messages'


response = ddb.create_table(
  TableName=table_name,
  AttributeDefinitions=[
    {
      'AttributeName': 'pk',
      'AttributeType': 'S'
    },
    {
      'AttributeName': 'sk',
      'AttributeType': 'S'
    },
  ],
  KeySchema=[
    {
      'AttributeName': 'pk',
      'KeyType': 'HASH'
    },
    {
      'AttributeName': 'sk',
      'KeyType': 'RANGE'
    },
  ],
  #GlobalSecondaryIndexes=[
  #],
  BillingMode='PROVISIONED',
  ProvisionedThroughput={
      'ReadCapacityUnits': 5,
      'WriteCapacityUnits': 5
  }
)

print(response)
```

- Give execute permission to the script

```sh
chmod u+x /bin/ddb/schema-load
```

- Run schema-load

```sh
./bin/ddb/schema-load
```

- This should return information about the table

- In **/ddb/list-table**, provision script to list tables:

```sh
#! /usr/bin/bash
set -e # stop if it fails at any point

if [ "$1" = "prod" ]; then
  ENDPOINT_URL=""
else
  ENDPOINT_URL="--endpoint-url=http://localhost:8000"
fi

aws dynamodb list-tables $ENDPOINT_URL \
--query TableNames \
--output table
```

- Give execute permission to the script

```sh
chmod u+x /bin/ddb/list-tables
```

- Now, run the script to return the list of tables:

```sh
./bin/ddb/list-tables
```

- In **/ddb/drop**, provision script to drop specified table:

```sh
#! /usr/bin/bash

set -e # stop if it fails at any point

if [ -z "$1" ]; then
  echo "No TABLE_NAME argument supplied eg ./bin/ddb/drop cruddur-messages prod "
  exit 1
fi
TABLE_NAME=$1

if [ "$2" = "prod" ]; then
  ENDPOINT_URL=""
else
  ENDPOINT_URL="--endpoint-url=http://localhost:8000"
fi

echo "deleting table: $TABLE_NAME"

aws dynamodb delete-table $ENDPOINT_URL \
  --table-name $TABLE_NAME
```

- Give execute permission to the script

```sh
chmod u+x /bin/ddb/drop
```

- Now, run the script to drop the specified table:

```sh
./bin/ddb/drop cruddur-messages
```

- We need to run mysql: Create database, load schema and enter seed data
- Edit `/db/seed` to include email values

```sh
./bin/db/setup
```

- In **/ddb/seed**, provision python script to create mock data in table

- Give execute permission to the script

```sh
chmod u+x /bin/ddb/seed
```

- Now, run the script

```sh
./bin/ddb/seed
```

- This should seed data into the local database

- In `/ddb/` directory, create a new file `scan` and instrument for python sdk. The scan is to show the contents of the cruddur-messages.

```py
#!/usr/bin/env python3

import boto3

attrs = {
  'endpoint_url': 'http://localhost:8000'
}
ddb = boto3.resource('dynamodb',**attrs)
table_name = 'cruddur-messages'

table = ddb.Table(table_name)
response = table.scan()

items = response['Items']
for item in items:
  print(item)
```

- Give execute permission to the script

```sh
chmod u+x /bin/ddb/scan
```

- Now, run the script

```sh
./bin/ddb/scan
```

- Create a new directory `/ddb/patterns/` and add the following files in it: _get-conversation_ and _list-conversations_

- Enter the code for both files

+ For _get-conversation_:

- Give execute permission to the script

```sh
chmod u+x /bin/ddb/patterns/get-conversation
```

- Now, run the script

```sh
./bin/ddb/patterns/get-conversation
```

+ For _list-conversations_:

- Give execute permission to the script

```sh
chmod u+x /bin/ddb/patterns/list-conversations
```

- Edit `/lib/db.py` to define query_value and print_sql and other parameters

- Now, run the script

```sh
./bin/ddb/patterns/list-conversations
```

- Let's add command in _.gitpod.yml_ to install requirements.txt

- We need to create a dynamodb library, _ddb.py_ in /lib directory

- In /bin directory, create a folder "cognito" and file 'list-users'. 

- On the terminal, you can list users using cli command:

```sh
aws cognito-idp list-users --user-pool-id=enter-cognito-user-pool-id-here
```

- We want to implement this in /bin/cognito/list-users using an sdk script:

```py
#!/usr/bin/env python3

import boto3
import os
import json

userpool_id = os.getenv("AWS_COGNITO_USER_POOL_ID")
client = boto3.client('cognito-idp')
params = {
  'UserPoolId': userpool_id,
  'AttributesToGet': [
      'preferred_username',
      'sub'
  ]
}
response = client.list_users(**params)
users = response['Users']

print(json.dumps(users, sort_keys=True, indent=2, default=str))

dict_users = {}
for user in users:
  attrs = user['Attributes']
  sub    = next((a for a in attrs if a["Name"] == 'sub'), None)
  handle = next((a for a in attrs if a["Name"] == 'preferred_username'), None)
  dict_users[handle['Value']] = sub['Value']

print(json.dumps(dict_users, sort_keys=True, indent=2, default=str))
```

- Set the cognito user pool id as env variable:

```sh
export AWS_COGNITO_USER_POOL_ID=""

gp env AWS_COGNITO_USER_POOL_ID=""
```

- Update this in the docker-compose file (replace the hard coded value with reference to env)

- Give execute permission to the 'list-users' script

```sh
chmod u+x /bin/cognito/list-users
```

- Run the script

```sh
./bin/cognito/list-users
```

- Now that we can list out the users, we need to create a new script to update the cognito user ids in our database

- In "bin/db/", create a new file 'update_cognito_user_ids'

- Give execute permission to the 'update_cognito_user_ids' script

```sh
chmod u+x /bin/db/update_cognito_user_ids
```

- Update /db/setup to execute the `update_cognito_user_ids` script

- Make sure the database is running (docker-compose), then run the 'setup' script

```sh
./bin/db/setup
```

- If there is an issue with the 'update_cognito_user_ids' step, try to run it alone

- You can connect to sql database to confirm the cognito user id is updated:

```sh
./bin/db/connect
\x auto
SELECT * FROM users;
```

- Modify _app.py_

- Modify /services/message_groups.py

- In /db/sql, create a new directory, "users". Create an sql file, 'uuid_from_cognito_user_id.sql' and enter the query:

```sql
SELECT
  users.uuid
FROM public.users
WHERE 
  users.cognito_user_id = %(cognito_user_id)s
LIMIT 1
```

- Implement token authorization for MessageGroupPage.js, MessageGroupsPage.js files in 'frontend-react-js/src/pages/' and MessageForm.js in 'frontend-react-js/src/components/'

```js
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
```

- Create a 'CheckAuth' file in new dir frontend-react-js/src/lib/. This should hold the amplify authentication function

- We will edit the HomeFeedPage.js, MessageGroupsPage.js and MessageGroupPage.js to use this function

- Load cruddur homepage and see if it returns correctly

- To check if the messages section of cruddur is working, let's seed data into dynamodb

```sh
./bin/ddb/schema-load

./bin/ddb/seed
```

- Now, set the endpoint_url for ddb in docker-compose

```yml
      AWS_ENDPOINT_URL: "http://dynamodb-local:8000"
```

- Restart docker compose

- Now, check the messages section of cruddur

- Go to 'App.js' and set MessageGroupPage to return message_group_uuid instead of @handle

- Also, in MessageGroupPage.js, we want to change the endpoint for that from @handle to params.message_group_uuid

- Do the same for MessageGroupItem.js in /components

- Edit ddb.py, list-conversations.py and get-conversation.py

- Edit app.py to instrument messages

- Edit /services/messages.py to replace mock data

- Edit /lib/ddb.py to define list_messages

- Update /src/components/MessageForm.js

- Update app.py and /services/create_message.py

- Create a new file /db/sql/users/create_message_users.sql

- On cruddur, try to create a message

- Edit App.js in frontend-resct-js

- Create a new file /frontend-react-js/src/pages/MessageGroupNewPage.js

- Edit app.py

- In /services/, create a new file 'users_short.py'

- Create a new file /db/sql/users/short.sql

- In /components/, create a new file, 'MessageGroupNewItem.js'

- Update MessageGroupFeed.js

- Update MessageForm.js

- Update create_message.py

- Next, update ddb.py to define create_message_group

- Now, in the message section with the newly added user 'Londo', try to send a message on cruddur