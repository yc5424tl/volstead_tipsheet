
from flask_migrate import MigrateCommand, Manager
from vault import create_app

manager = Manager(create_app)
# manager.add_option("-c", "--config", dest="config_module", required=False)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()