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

Common PSQL commands:

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

### Create (and dropping) our database

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

- We need to add the create extension to schema.sql

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