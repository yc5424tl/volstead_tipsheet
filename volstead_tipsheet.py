from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import Config
from numpy import linspace

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)


@app.route('/', methods=['GET', 'POST'])
def front_page():

    if request.method == 'GET':

        denoms = ['100\'s', '50\'s', '20\'s', '10\'s', '5\'s', '1\'s', 'Q\'s']


        employees = dict(JAKE='F',
                         CORY='F',
                         SAM='F',
                         INA='F',
                         ELANEOR='F',
                         JENNIE='F',
                         HEIDI='F',
                         CHRIS='F',
                         MARLEY='F',
                         ADAM='P',
                         MOCK='P')

        float_range = linspace(0.0, 9.0, num=19, retstep=True)

        return render_template('eod_form.html', denoms=denoms, employees=employees, float_range=float_range)

    if request.method == 'POST':
        return None


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run()
