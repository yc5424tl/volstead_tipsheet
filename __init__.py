# coding=utf-8
from config import Config
from flask import Flask
from flask.ext.mongoalchemy import MongoAlchemy

app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = Config.DB_NAME
app.config['MONGOALCHEMY_SERVER'] = Config.DB_HOST
app.config['']

from volsteads.errors import bp as errors_bp
app.register_blueprint(errors_bp)

# from volsteads import routes, models