from flask import Flask, render_template, request, redirect, url_for
from flask.views import MethodView
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

    if request.method == 'GET':
        return render_template('eod_form.html', denoms=denoms, employees=employees, float_range=float_range)

    if request.method == 'POST':

        # id={{ emp }} + '-hours'
        # id={{ emp }} + '-full'
        # id={{ emp }} + '-partial'

        rf = request.form
        raw_hours = 0.0
        total_hours = 0.0

        for emp in employees:
            print(emp)
            print(employees[emp])
            print(str(rf[emp+'-hours']))
            raw_hours += float(rf[emp + '-hours'])

            if employees[emp] == 'P':
                total_hours += float(rf[emp+'-hours']) * .65
                print('adjusted hours = ' + str(float(rf[emp+'-hours']) * .65)[0:4])
            elif employees[emp] == 'F':
                total_hours += float(rf[emp+'-hours'])
            print('RAW HOURS = ' + str(raw_hours))
            print('TOTAL HOURS = ' + str(total_hours) + '\n')
        return render_template('eod_form.html', denoms=denoms, employees=employees, float_range=float_range)


# class ReportsView(MethodView):
#
#     def __init__(self, template_name):
#         self._template_name = template_name
#         self._rf = request.form

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run()
