

from app import create_app
app = create_app()

from app.models import User

@app.shell_context_processor
def make_shell_context():

    return {'db': app.db, 'User': User}