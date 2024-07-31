# Task Management API

## How to Start the Project

### Clone the Project

To clone the project, run the following command:

```sh
git clone git@github.com:mariomthree/task-management-api.git
```

### Setup Environment

```sh
cd task-management-api
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```sh
pip3 install django
pip3 install djangorestframework
pip3 install django-cors-headers
pip3 install drf-spectacular
```

### Start the Project

```sh
cd src
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

### Access the Documentation in Browser

```
http://127.0.0.1:8000/api/docs
```

