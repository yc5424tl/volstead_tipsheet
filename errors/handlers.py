from flask import render_template
from volsteads import mongo
from volsteads.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    mongo.db.session.rollback()
    return render_template('500.html'), 500