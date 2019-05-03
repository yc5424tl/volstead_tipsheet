# coding=utf-8
import datetime
import os

from decimal import Decimal, ROUND_HALF_UP

import flask
# import google_auth_oauthlib
from flask import Flask, copy_current_request_context, request, render_template, url_for
from flask_bootstrap import Bootstrap
from numpy import linspace

import sheet_mgr
import db_mgr
from config import Config
from employee import Employee
from shift import Shift

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
denominations = {'100.00': 0.00, '50.00': 0.00, '20.00': 0.00, '10.00': 0.00, '5.00': 0.00, '1.00': 0.00, '0.25': 0.00}
shift_hours_range = linspace(0.0, 9.0, num=19, retstep=True)


def instantiate_employees():

    employee_dict = dict(JAKE=("BOLINE", "SERVICE", "Jacob Boline"),
                         CORY=("SCHULLER", "SERVICE", "Cory"),
                         INA=("DALE", "SERVICE", "Ina"),
                         ELEANOR=("JOHNSON", "SERVICE", "Eleanor"),
                         JENNIE=("SONG", "SERVICE", ""),
                         HEIDI=("HEIDI", "SERVICE", "Heidi"),
                         CHRIS=("THOMPSON", "SERVICE", "Chris"),
                         MARLEY=("BARTLETT", "SERVICE", "Marley"),
                         ADAM=("O'BRIEN", "SUPPORT", "Adam O'Brien"),
                         REBECCA=("MOGCK", "SUPPORT", "Rebecca M"))

    return [Employee(emp, employee_dict[emp][0], employee_dict[emp][1]) for emp in employee_dict]


employees = instantiate_employees()
shift = Shift(employees, denominations)

db_ctr = db_mgr.DbController(int(os.getenv('VOL_DB_PORT')), os.getenv('VOL_DB_HOST'))
db_ctr.connect_db()


def redirect_url(default='front_page'):
    return request.args.get('next') or request.referrer or url_for(default)


def validate_cash_inputs(denomination_list, request_form):
    denoms = denomination_list
    rf = request_form

    for denom in denoms:
        subtotal = float(rf[denom])
        if subtotal > 0:
            modulated_subtotal = float(subtotal) % float(denom)
            if modulated_subtotal != 0:
                return False
    return True


@app.route('/submit_report', methods=['POST'])
def submit_report():
    if request.method == 'POST':
        if employees and shift:
            shift_report = db_ctr.build_shift_report(shift)
            shift_report['staff_report'] = db_ctr.build_staff_report(employees)
            if db_ctr.submit_daily_report(shift_report):
                print('report submitted to db')

            return render_template('submit_success.html', daily_report=shift_report)


# @app.route('/oauth2callback', methods=['POST'])
# def oauth2_callback():
#
#     state = flask.session['state']
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret.json', scopes=['https://www.googleapis.com/auth/'])


@app.route('/privacy_policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')


@app.route('/', methods=['GET', 'POST'])
def front_page():
    @copy_current_request_context
    def analyze_hours(working_shift: Shift, req_form: request.form):
        for target_emp in shift.staff:

            target_emp.shift_hours = float(req_form[target_emp.first_name + '-hours'])
            shift.shift_hours += target_emp.shift_hours

            if target_emp.role == "SUPPORT":
                target_emp._tip_hours = Decimal(target_emp.shift_hours * 0.65).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
                working_shift.tip_hours += target_emp.tip_hours

            elif target_emp.role == "SERVICE":
                target_emp._tip_hours = target_emp.shift_hours
                working_shift.tip_hours += target_emp.tip_hours

        return True

    @copy_current_request_context
    def get_cash_subtotal(working_shift: Shift, req_form: request.form) -> float:
        cash_subtotal = 0.00

        for denom in working_shift.cash_subtotals:
            working_shift.cash_subtotals[denom] = float(req_form[denom])
            cash_subtotal += working_shift.cash_subtotals[denom]

        shift.cash_tip_pool = cash_subtotal
        return cash_subtotal

    def get_tip_wage(total_tip_hours: float, cash_total: float) -> float:
        return Decimal(cash_total / total_tip_hours).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    def get_emp_tips(shift_staff: [Employee], tip_wage: float):
        for employee in shift_staff:
            employee._cash_tips = Decimal(Decimal(employee.tip_hours) * Decimal(tip_wage)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    def stringify_date(date: datetime.datetime):
        return date.strftime('%A %B %d %Y')

    if request.method == 'GET':
        return render_template('eod_form.html',
                               denominations=denominations,
                               employees=employees,
                               float_range=shift_hours_range)

    if request.method == 'POST':
        rf = request.form
        tip_hours = 0.00

        for emp in employees:
            hours_tag_id = emp.first_name + '-hours'
            hours = float(rf[hours_tag_id])
            tip_hours += hours

            if hours > 0:
                role_tag_id = emp.first_name + '-radio'
                role_radio_value = rf[role_tag_id]
                emp.role = role_radio_value

        if not (tip_hours > 0):
            error = "Form Submitted with Zero Tip Hours"
            return render_template('eod_form.html',
                                   denominations=denominations,
                                   employees=employees,
                                   float_range=shift_hours_range,
                                   error=error)

        analyze_hours(shift, rf)
        total_cash = get_cash_subtotal(shift, rf)
        shift._cash_tip_wage = get_tip_wage(shift.tip_hours, total_cash)
        get_emp_tips(shift.staff, shift.cash_tip_wage)
        shift._cc_tip_pool = float(rf['report-tips'])

        if shift.cc_tip_pool > 0.00:
            shift.cc_tip_wage = Decimal(shift.cc_tip_pool / shift.tip_hours).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            for emp in shift.staff:
                emp._cc_tips = Decimal(Decimal(shift.cc_tip_wage) * Decimal(emp.tip_hours)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        today = datetime.datetime.today()
        if int(datetime.datetime.now().strftime('%H')) >= 17:
            # shift._start_date = today.strftime('%A %B %d %Y')  # Day of Week, Month, Day, Year
            shift._start_date = today
        else:
            yesterday = today - datetime.timedelta(days=1)
            # shift._start_date = yesterday.strftime('%A %B %d %Y')
            shift._start_date = yesterday

        return render_template('report.html', denominations=denominations, employees=shift.staff, float_range=shift_hours_range, shift=shift, stringify_date=stringify_date)

        # TO GET ROW FOR SPREADSHEET
        # Target Date = MM/DD/YYYY
        # Reference Date = 12/31/2018
        # Target_Date - Reference_date
        # ref_date = datetime.datetime(year=2018, month=12, day=31)
        # target_date = datetime.datetime(year=int(target_date.strftime('%Y')), month=int(target_date.strftime('%m')), day=int(target_date.strftime('%d')))
        # days_since = target_date - ref_date
        # days_since_numeric_value = days_since.days

        # period = (days_since_numeric_value // 16) + 1  **first part gives # of full periods, add one to get the current period

        # each period takes 16 rows, plus one row at the beginning

        # row_in_period = days_since_numeric_value % 16

        # row = 16 * (period - 1) + 1 + row_in_period

        # return render_template(redirect_url())


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=port)
