import os
from django.core.wsgi import get_wsgi_application
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Application started.")

# Настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'printerapp.settings')
django_app = get_wsgi_application()

# Настройки Flask
flask_app = Flask(__name__)

@flask_app.route('/flask')
def hello():
    return 'Hello from Flask!'

# Объединение приложений с помощью DispatcherMiddleware
application = DispatcherMiddleware(django_app, {
    '/flaskapp': flask_app  # Весь трафик по пути /flaskapp будет перенаправлен на приложение Flask
})
