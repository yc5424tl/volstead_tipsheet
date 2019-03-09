from flask_script import Manager


from volstead_tipsheet import app



manager = Manager(app)


if __name__ == '__main__':
    manager.run()
