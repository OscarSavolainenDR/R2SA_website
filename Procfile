
release: python manage.py makemigrations --no-input
release: python manage.py migrate --no-input

web: gunicorn backend_v3.wsgi --log-file -
celery: celery worker -A backend_v3 -l info -c 4
