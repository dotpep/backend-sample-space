# Docker/K8s command HandBook

Src:

- [Getting started guide by Docker](https://docs.docker.com/get-started)

## Docker

### Basics

- Build image uses Dockerfile in the current directory : `docker build -t <image-name> .`
- run container `docker run -dp 127.0.0.1:3000:3000 <image-name>` flags: (run in the backgroud: `-d`), (`-p`: create a port mapping `HOST:CONTAINER`)

- show list of containers: `docker ps` (Get the ID)
- stop container: `docker stop <the-container-id>`
- once is stopped you can remove: `docker rm <the-container-id>`
- force remove (will rm without stop): `docker rm -f <the-container-id>`

- show list of images: `docker image ls`

### Sharing image Docker Hub

- `docker login`
- `docker tag` gives new name for image: `docker tag <image-name> YOUR-USER-NAME/new-image-repository-name`
- publish to docker hub: `docker push YOUR-USER-NAME/repository-name`
- or use `YOUR-USER-NAME/repository-name:tagname`

### Container's Filesystem

- Start an ubuntu container that will create a file named /data.txt with a random number between 1 and 10000.

```bash
docker run -d ubuntu bash -c "shuf -i 1-10000 -n 1 -o /data.txt && tail -f /dev/null"
```

- access terminal in the container (`docker exec` command to get container access)
- `docker exec <container-id> cat /data.txt` or any command instead `cat` like `ls`, `pwd`

> Use `docker exec` when you run a program inside an existing running container. Example: `docker exec my-container ls`

- `docker run -it ubuntu ls /` (`-it` flag allows running commands inside the container interactively)

> Use `docker run` when you create and start a new container from an image (want to initialize container and run a specific command inside it). Example: `docker run -it my-image ls`

### Container volumes

> Volumes is special folder or storage area that a Docker container uses to save and retrieve data.

- Create `docker volume create volume-name-todo-db`
- Start app but with some options: `docker run -dp 127.0.0.1:3000:3000 --mount type=volume,src=volume-name-todo-db,target=/etc/todos image-name-getting-started`
- Show where data is stored when you use volume: `docker volume inspect volume-name-todo-db`

### Bind mounts

- Start `bash` in an `ubuntu` container with a bind mount: `docker run -it --mount type=bind,src="$(pwd)",target=/src ubuntu bash`

---

- Run container with bind mount (in Powershell)

```ps
docker run -dp 127.0.0.1:3000:3000 `
    -w /app --mount "type=bind,src=$pwd,target=/app" `
    node:18-alpine `
    sh -c "yarn install && yarn run dev"
```

- `-w /app` sets the working directory, `node:18-alpine` use image, execute command `sh -c "yarn install && yarn run dev"`

### Multi container apps

- Create network: `docker network create todo-app`
- Start MySQL:

```ps
docker run -d `
    --network todo-app --network-alias mysql `
    -v todo-mysql-data:/var/lib/mysql `
    -e MYSQL_ROOT_PASSWORD=secret `
    -e MYSQL_DATABASE=db-name-todos `
    mysql:8.0
```

- To confirm you have the database up and running, connect to the database and verify that it connects.
- `docker exec -it <mysql-container-id> mysql -u root -p` and you can specify database that you want to use by `mysql -u root -p db-name-todos`

---

- Start Your App with MySQL:

```ps
docker run -dp 127.0.0.1:3000:3000 `
  -w /app -v "$(pwd):/app" `
  --network todo-app `
  -e MYSQL_HOST=mysql `
  -e MYSQL_USER=root `
  -e MYSQL_PASSWORD=secret `
  -e MYSQL_DB=todos `
  node:18-alpine `
  sh -c "yarn install && yarn run dev"
```

- Look at logs of node.js apps to see it uses MySQL and connected well:
- `docker logs -f <container-id>`

- Connect to the mysql database and prove that the items are being written to the database:
- `docker exec -it <mysql-container-id> mysql -p todos`

## Docker Compose

> Compose uses to share, create and run one yaml file to run multiple services/containers.

---

- Define and app service (file: `compose.yaml`):

```yaml
services:
  app:
    image: node:18-alpine
    command: sh -c "yarn install && yarn run dev"
    ports:
      - 127.0.0.1:3000:3000
    working_dir: /app
    volumes:
      - ./:/app
    environment:
      MYSQL_HOST: mysql
      MYSQL_USER: root
      MYSQL_PASSWORD: secret
      MYSQL_DB: todos
```

---

- Define the MySQL service (file: `compose.yaml`):

```yaml
services:
  app:
    # The app service definition
  mysql:
    image: mysql:8.0
    volumes:
      - todo-mysql-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: todos

volumes:
  todo-mysql-data:
```

---

- Final version of `compose.yaml` file:

```yaml
services:
  app:
    image: node:18-alpine
    command: sh -c "yarn install && yarn run dev"
    ports:
      - 127.0.0.1:3000:3000
    working_dir: /app
    volumes:
      - ./:/app
    environment:
      MYSQL_HOST: mysql
      MYSQL_USER: root
      MYSQL_PASSWORD: secret
      MYSQL_DB: todos

  mysql:
    image: mysql:8.0
    volumes:
      - todo-mysql-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: todos

volumes:
  todo-mysql-data:
```

---

- Run the Application stack:
- `docker compose up -d` (`-d` flags run everything in the background)
- Look at loogs: `docker compose logs -f` or for specific service using `docker compose logs -f app` app is defined in yaml service name
- Tear it all down: `docker compose down`

---

- Enter to mysql shell:
- `docker compose exec <service-name-mysql> mysql -u root -p todos`

## Image-building, Dockerfile

- Use the docker image history command to see the layers in the getting-started image you created.
- `docker image history getting-started`

---

- Layer caching:
- NotImplemented

## Docker Cloud (Deploying Conteiners)

> [Source code here](https://github.com/dotpep/backend-sample-space/Docker/Services_Docker_Cloud\practice-example)

Docker:

- `docker build -t hello-world .` (create image of Dockerfile)
- `docker run -p 80:80 hello-world` (run image)
- `docker run -p 80:80 -v ${PWD}/src:/var/www/html hello-world` (run with volume for checking HOST|Container and automatically update container when change detected in files by `-v` volume flags and `${PWD}/src:/var/www/html` directory specify `HOST:CONTAINER` folders to check it up)

---

Docker Compose:

```yml
version: '3.3'

services:
  product-service:
    build: ./product
    volumes:
      - ./product:/usr/src/app
    ports:
      - 5001:80

  website:
    image: php:apache
    volumes:
      - ./website:/var/www/html
    ports:
      - 5000:80
    depends_on:
      - product-service
```

- `docker-compose up`

## K8s kubectl
