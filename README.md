Requirements

Steps to set up local web server
1. Install python  dependencies

2. Apply migrations to create initial database

python manage.py makemigrations
python manage.py migrate

3. Create an admin user (needed to create accounts for features that require login)

python manage.py createsuperuser

4. Launch the webserver

python manage.py runserver


