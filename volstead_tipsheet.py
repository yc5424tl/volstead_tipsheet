from flask import Flask, render_template, request, redirect, url_for
from flask.views import MethodView
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import Config
from numpy import linspace
import datetime

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)



@app.route('/', methods=['GET', 'POST'])
def front_page():

    denoms = ['100\'s', '50\'s', '20\'s', '10\'s', '5\'s', '1\'s', 'Q\'s']

    denominations = ['100.00', '50.00', '20.00', '10.00', '5.00', '1.00', '0.25']

    employees = dict(JAKE='SERVICE',
                     CORY='SERVICE',
                     SAM='SERVICE',
                     INA='SERVICE',
                     ELANEOR='SERVICE',
                     JENNIE='SERVICE',
                     HEIDI='SERVICE',
                     CHRIS='SERVICE',
                     MARLEY='SERVICE',
                     ADAM='SUPPORT',
                     MOCK='SUPPORT')

    float_range = linspace(0.0, 9.0, num=19, retstep=True)

    if request.method == 'GET':
        return render_template('eod_form.html',
                               denoms=denoms,
                               denominations=denominations,
                               employees=employees,
                               float_range=float_range)

    if request.method == 'POST':

        # id={{ emp }} + '-hours'
        # id={{ emp }} + '-full'
        # id={{ emp }} + '-partial'

        rf = request.form
        shift_hours = 0.0
        tip_hours = 0.0
        valid_cash = False
        cash_total = 0
        tip_hourly = 0.0
        emp_hours = {}
        emp_tips = {}
        emp_cc_tips = {}
        report_total = 0
        cc_hourly = 0.0
        tips_recount = 0

        for emp in employees:

            print(emp)
            print(employees[emp])
            print(str(rf[emp+'-hours']))

            shift_hours += float(rf[emp + '-hours'])

            if employees[emp] == 'SUPPORT':
                emp_tip_hours = float(rf[emp+'-hours']) * .65
                tip_hours += emp_tip_hours
                print('adjusted hours = ' + str(round(float(rf[emp+'-hours']) * .65, 2)))
                emp_hours[emp] = emp_tip_hours

            elif employees[emp] == 'SERVICE':
                emp_tip_hours = float(rf[emp+'-hours'])
                tip_hours += emp_tip_hours
                emp_hours[emp] = emp_tip_hours

            print('SHIFT HOURS = ' + str(shift_hours))
            print('TIP HOURS = ' + str(tip_hours) + '\n')

        if rf is not None:
            print('rf is not None')
            valid_cash = validate_cash_inputs(denominations, rf)
        if rf is None:
            print('rf is None')

        if valid_cash:
            for denom in denominations:
                cash_total += float(rf[denom])
                print('cash total = ' + str(cash_total))

        if cash_total > 0:
            tip_hourly += round(cash_total / tip_hours, 2)
            print('TIP WAGE = ' + str(tip_hourly))

        for emp in emp_hours:
            emp_tip_hours = emp_hours[emp]
            emp_cash = emp_tip_hours * tip_hourly
            emp_tips[emp] = emp_cash

        for emp in emp_tips:
            print(emp + '\'s share is ' + str(round(emp_tips[emp], 2)))
            tips_recount += emp_tips[emp]

        print('Subtotal of all shares = ' + str(tips_recount))

        report_total = float(rf['report-tips'])

        if report_total > 0:
            cc_hourly = round(report_total / tip_hours, 2)
            print('CC WAGE = ' + str(cc_hourly))

            for emp in emp_hours:
                tip_hours = emp_hours[emp]
                emp_cc_total = tip_hours * cc_hourly
                emp_cc_tips[emp] = emp_cc_total

            for emp in emp_cc_tips:
                print('CC Tips for ' + emp + ' = ' + str(round(emp_cc_tips[emp], 2)))

        today = datetime.date.today()
        print('Today is ' + today.isoformat())
        print('Today is ' + today.strftime('%A %B %d, %Y'))

        return render_template('eod_form.html',
                               denoms=denoms,
                               denominations=denominations,
                               employees=employees,
                               float_range=float_range)


def validate_cash_inputs(denomination_list, request_form):
    denominations = denomination_list
    rf = request_form
    for denom in denominations:
        subtotal = float(rf[denom])
        print('DENOM SUBTOTAL FOR ' + str(denom) + ' EQUALS ' + str(subtotal))
        if subtotal > 0:
            modulated_subtotal = float(subtotal) % float(denom)
            print('MODULATED SUBTOTAL = ' + str(modulated_subtotal))
            if modulated_subtotal != 0:
                return False

    return True


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run()
