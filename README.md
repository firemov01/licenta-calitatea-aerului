# Django Project

This is a Django project that uses Docker for easy setup and deployment.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:

   ```
   git clone https://github.com/firemov01/licenta-calitatea-aerului.git
   ```

2. Navigate to the project directory:

   ```
   cd yourrepository
   ```

3. Build the Docker images:

   ```
   docker-compose build
   ```

4. Start the Docker containers:
   ```
   docker-compose up
   ```

Your Django application should now be running at [http://localhost:8000](http://localhost:8000). The Flower monitoring tool is available at [http://localhost:5555](http://localhost:5555).

## Creating a User

To create a user, you need to run the Django `createsuperuser` command inside the Docker container.

1. Open a new terminal window.

2. Run the following command to execute the `createsuperuser` command inside the Docker container:

   ```
   docker exec -it django python manage.py createsuperuser
   ```

3. Follow the prompts to create a new user.

## Stopping the Application

To stop the application, press `Ctrl+C` in the terminal where the containers are running.

To remove the containers, run:
`  docker-compose down
 `

## Enter django bash

1. Open a new terminal window.

2. Run the following command to execute the `bash` command inside the Docker container:
   ```
   docker exec -it django bash
   ```
3. To exit the bash, run:
   ```
   exit
   ```

## Make migrations

1. Open a new terminal window.

2. Run the following command to execute the `makemigrations` command inside the Docker container:
   ```
   docker exec -it django python manage.py makemigrations
   ```
3. Run the following command to execute the `migrate` command inside the Docker container:
   ```
   docker exec -it django python manage.py migrate
   ```

## Further Reading

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
