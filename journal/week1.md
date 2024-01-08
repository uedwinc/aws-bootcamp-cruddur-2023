# App Containerization

This can either be done on containers individually or multiple containers using docker-compose

## Containerize Individually

1. Containerize Backend

- In the backend directory, create and write a [Dockerfile](backend-flask/Dockerfile)

- Build the Dockerfile (run from working directory)

  ```
  docker build -t backend-flask ./backend-flask
  ```

- Run the container

  ```
  docker run --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' -d backend-flask
  ```

- Open the port in the ports tab and Confirm on the browser (add /api/activities/home)

2. Containerize Frontend

- Go to the frontend directory and run `npm install`

- In the frontend directory, create and write a [Dockerfile](frontend-react-js/Dockerfile)

- Build the container

    ```
    docker build -t frontend-react-js ./frontend-react-js
    ```

- Run container

    ```
    docker run -p 3000:3000 -d frontend-react-js
    ```

## Containerize using docker compose

1. `cd` into the working directory

2. Create and write a [docker-compose.yml](/docker-compose.yml) file

3. Right click on the docker-compose file and click 'Compose up' or do `docker compose up`

4. Open the ports and launch on browser

5. Try to signup on the webapp

---

## Container Security Best Practices

This comprises:
- Docker and host configuration
  - Keep Host & Docker Updated to latest security Patches
  - Docker daemon & containers should run in non-root user mode
- Securing images
  - Image Vulnerability Scanning
  - Trusting a Private vs Public Image Registry
- Secret management
  - No Sensitive Data in Docker files or Images
  - Use Secret Management Services to Share secrets
- Data security
  - Read only File system and Volume for Docker
  - Separate databases for long term storage
- Application security
  - Use DevSecOps practices while building application security
  - Ensure all Code is tested for vulnerabilities before production use
- Monitoring containers
  - Use DevSecOps practices while building application security
  - Ensure all Code is tested for vulnerabilities before production use
- Compliance framework
  - Use DevSecOps practices while building application security
  - Ensure all Code is tested for vulnerabilities before production use

---

## Adding DynamoDB Local and Postgres

We are going to use Postgres and DynamoDB local in future labs
We can bring them in as containers and reference them externally

Lets integrate the following into our existing docker compose file:

### Postgres

```yaml
services:
  db:
    image: postgres:13-alpine
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - '5432:5432'
    volumes: 
      - db:/var/lib/postgresql/data
volumes:
  db:
    driver: local
```

To install the postgres client into Gitpod

```sh
  - name: postgres
    init: |
      curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
      echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
      sudo apt update
      sudo apt install -y postgresql-client-13 libpq-dev
```

### DynamoDB Local

```yaml
services:
  dynamodb-local:
    # https://stackoverflow.com/questions/67533058/persist-local-dynamodb-data-in-volumes-lack-permission-unable-to-open-databa
    # We needed to add user:root to get this working.
    user: root
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ./data"
    image: "amazon/dynamodb-local:latest"
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal
```

Example of using DynamoDB local
https://github.com/100DaysOfCloud/challenge-dynamodb-local

## Working with the Databases

- First, do `docker compose up` to run all containers

### Using DynamoDB local

#### Create a table

```sh
aws dynamodb create-table \
    --endpoint-url http://localhost:8000 \
    --table-name Music \
    --attribute-definitions \
        AttributeName=Artist,AttributeType=S \
        AttributeName=SongTitle,AttributeType=S \
    --key-schema AttributeName=Artist,KeyType=HASH AttributeName=SongTitle,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
    --table-class STANDARD
```

#### Create an Item

```sh
aws dynamodb put-item \
    --endpoint-url http://localhost:8000 \
    --table-name Music \
    --item \
        '{"Artist": {"S": "No One You Know"}, "SongTitle": {"S": "Call Me Today"}, "AlbumTitle": {"S": "Somewhat Famous"}}' \
    --return-consumed-capacity TOTAL  
```

#### List Tables

```sh
aws dynamodb list-tables --endpoint-url http://localhost:8000
```

#### Get Records

```sh
aws dynamodb scan --table-name Music --query "Items" --endpoint-url http://localhost:8000
````

#### References

https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tools.CLI.html

### Using Postgres

- After installing the postgres client, you can create a database user using:

```sh
psql -U postgres --host localhost
```

- Now, you can run the following postgres commands:

```
\t
\d
\dl
\l
```

- Finally, do `\q` to quit