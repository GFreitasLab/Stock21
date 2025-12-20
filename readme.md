# Stock21

**Stock21** is a simple and lightweight inventory management web application aimed at small and medium-sized pizzerias.

## Features

* User management: registration, login, and roles such as employee and administrator.
* Ingredient and Product management: allowing creation, modification, viewing, and deletion.
* Record of movements and generation of billing reports by date.

## Technologies

### Backend

* **Language:** [Python](https://www.python.org/) - High-level, simple, and powerful programming language, widely used for automation and data science.
* **Framework:** [Django](https://www.djangoproject.com/) - Python web framework that allows creating complete applications quickly, securely, and scalably.
* **Database:** [Sqlite3](https://sqlite.org/index.html) - Lightweight and embedded relational database, ideal for testing and small projects.
* **Database Visualization:** [Django Schema Viewer](https://pypi.org/project/django-schema-viewer/) - Visualize the relationships between Django Models and the database structure interactively.

### Frontend

* **Templates:** [Django Templates](https://docs.djangoproject.com/en/5.2/topics/templates/) - Django's native template system that allows generating dynamic HTML pages from backend variables.
* **Style:** [Tailwind CSS](https://www.google.com/search?q=) - Utility-first CSS framework that facilitates creating responsive and modern interfaces with pre-defined classes.

### DevOps

* **Docker:** [Docker](https://docs.docker.com/get-started/) – Tool that creates isolated environments (containers) to run applications in a standardized way on any machine.
* **Docker Compose:** [Docker Compose](https://docs.docker.com/compose/) – Tool that orchestrates multiple containers simultaneously, using a YAML file to configure everything with a single command.

## Project Structure

```
devspizza
├── core                # Main project settings
│   ├── asgi.py
│   ├── decorators.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── accounts            # Module responsible for managing users
│   ├── models.py
│   ├── templates
│   │   ├── ...
│   ├── urls.py
│   └── views.py
├── movements           # Module responsible for managing movements
│   ├── models.py
│   ├── templates
│   │   ├── ...
│   ├── urls.py
│   └── views.py
├── stock               # Module responsible for managing inventory
│   ├── models.py
│   ├── templates
│   │   ├── ...
│   ├── urls.py
│   └── views.py
├── static              # Static files used by Django (JavaScript)
└── templates           # HTML templates not associated with any module
├── .gitignore          # File to explicitly specify files to be ignored by Git
├── .venv               # Python Virtual Environment (Ignored by Git)
├── .env                # Environment variables for Docker and Django configuration
├── db.sqlite3          # Database
├── docker-compose.yml  # Tells step-by-step how to set up the environment for the project
├── Dockerfile          # Brings everything together in one place and runs multiple services with a single command
├── manage.py           # Django command-line utility for administrative tasks
├── readme.md           # Project documentation
├── requirements.txt    # List of python dependencies for this project

```

## Prerequisites

* **Docker** and **Docker Compose**
* **Git**

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/GGB0T11/Stock21.git
cd Stock21

```


2. **Define environment variables:**
Create the `.env` file in the project root with the following variables:
```env
SECRET_KEY=your_django_secret_key     # Generate a unique and complex key for production
DEBUG=True                            # Set to False for production
DB_ENGINE=django.db.backends.sqlite3  # Sqlite3 for simple projects
DB_NAME=db.sqlite3                    # Database name
ALLOWED_HOSTS=* # Allowed hosts, by default, all

```


3. **Build Docker Compose:**
```bash
docker-compose up --build

```



## Running the Application

### Using Docker Compose (Recommended)

```bash
# Builds and starts all services
docker-compose up --build

# Runs in the background
docker-compose up -d

# Stops the service
docker-compose down

```

After starting the service you can access:

* **Application**: http://localhost:8000
* **Database Visualization**: [http://127.0.0.1:8000/schema-viewer/](http://127.0.0.1:8000/schema-viewer/)

## First Access

For the first use of the application, it is necessary to create a superuser. This superuser is essential to allow creating other users in the system later. To do this, run the following command in your terminal:

1. **Creating the Superuser:**
Run the command below in your terminal:
```bash
docker-compose exec backend python manage.py createsuperuser

```


Follow the prompts to configure your name, email, and password.

### License

This Project is under the MIT license - see the [LICENSE](https://github.com/GFreitasLab/Stock21/blob/main/LICENSE) file for more details
