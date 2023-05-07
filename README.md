Requirements

(Tested using anaconda Python 3.8.3)

Steps to set up local web server
1. Install python  dependencies

  pip3 install Django==3.1.7

  pip3 install django-bootstrap3

  pip3 install celery==4.4.2

  pip3 install elasticsearch_dsl

2. Apply migrations to create initial database

  python manage.py makemigrations
  python manage.py migrate --run-syncdb

NOTE: sometimes the command below is helpful if testing the database

  python manage.py migrate --run-syncdb

2b. Collect static files

  python manage.py collectstatic

3. Create an admin user (needed to create accounts for features that require login)

  python manage.py createsuperuser

4. Launch the webserver

  python manage.py runserver

5. Log into the admin site and create a user account (e.g. 'lbpm_user')

http://127.0.0.1:8000/admin/

6. Log into the account from

http://127.0.0.1:8000/accounts/login/

