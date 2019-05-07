# encoded in UTF-8

from flask import render_template
from volsteads.app import app
from volsteads import mongo

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    mongo.db.session.rollback()
    return render_template('500.html')