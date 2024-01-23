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
```
psql cruddur < db/schema.sql -h localhost -U postgres
```

### Create a CONNECTION URI string

CONNECTION URI string is a way of providing all the details that is needed to authenticate to the server. 

Documentation: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING

More documentation here https://stackoverflow.com/questions/3582552/what-is-the-format-for-the-postgresql-connection-string-url shows general format: postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]

```
CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
```

We can test this using:
```
psql postgresql://postgres:password@localhost:5432/cruddur
```

Now, we can set this as env variable:

```
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"

gp env CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
```

- Now, we can authenticate into the server using:

```
psql $CONNECTION_URL
```

- We can set this for production using the details used for RDS on AWS

```
PROD_CONNECTION_URL="postgresql://cruddurroot:cruddurPassword1@cruddur-db-instance.cbkq6ia0u32o.us-east-2.rds.amazonaws.com:5432/cruddur"
```

- Set this as env variable:

```
export PROD_CONNECTION_URL="postgresql://cruddurroot:cruddurPassword1@cruddur-db-instance.cbkq6ia0u32o.us-east-2.rds.amazonaws.com:5432/cruddur"

gp env PROD_CONNECTION_URL="postgresql://cruddurroot:cruddurPassword1@cruddur-db-instance.cbkq6ia0u32o.us-east-2.rds.amazonaws.com:5432/cruddur"
```

Next, we need to write bash scripts to automate some basic sql tasks

- In `backend-flask`, create a folder `bin` and add three files with no extension `db-create`, `db-drop` and `db-schema-load`

- Give execute rights to user for the three files:

```
chmod u+x bin/db-create

chmod u+x bin/db-drop

chmod u+x bin/db-schema-load
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

```
./bin/db-schema-load
```

- Create our tables

https://www.postgresql.org/docs/current/sql-createtable.html

We'll add these in the `schema.sql`

```sql
DROP TABLE IF EXISTS public.users cascade;
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
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```