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