from flask import render_template, request
from ...vault import db
from ...vault.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@bp.app_errorhandler(429)
def too_many_requests(error):
    wait_time = request.headers['Retry-after']
    return render_template('429.html', retry_after=wait_time), 429