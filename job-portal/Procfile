release: python backend/manage.py migrate
web: gunicorn --chdir backend backend.wsgi:application --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - --timeout 120
