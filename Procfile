web: gunicorn --log-level=debug vol_app:'create_app()'
init: python manage.py db init
migrate: python manage.py db migrate
upgrade: python manage.py db upgrade
