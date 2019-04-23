
import datetime
from flask import Flask, copy_current_request_context, request, render_template, url_for
from flask_bootstrap import Bootstrap
# from flask_sqlalchemy import SQLAlchemy
from numpy import linspace

from config import Config
from employee import Employee, TipShare
from shift import Shift
import os

from pymongo import MongoClient


app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)

db_uri = os.environ['PROD_MONGODB']
# client = MongoClient(db_uri, connectTimeout=30000, socketTimeoutMS=None, socketKeepAlive=True)
client = MongoClient(db_uri)
print(client.server_info)
db = client.get_database('volsteads_db')
print( db.list_collection_names() )
# db = SQLAlchemy(app)

denominations = {'100.00': 0.0, '50.00': 0.0, '20.00': 0.0, '10.00': 0.0, '5.00': 0.0, '1.00': 0.0, '0.25': 0.0}

shift_hours_range = linspace(0.0, 9.0, num=19, retstep=True)


def instantiate_employees():

    employee_dict = dict(JAKE="SERVICE",
                         CORY="SERVICE",
                         SAM="SERVICE",
                         INA="SERVICE",
                         ELEANOR="SERVICE",
                         JENNIE="SERVICE",
                         HIEDI="SERVICE",
                         CHRIS="SERVICE",
                         MARLEY="SERVICE",
                         ADAM="SUPPORT",
                         MOGCK="SUPPORT")

    return [Employee(emp, employee_dict[emp]) for emp in employee_dict]


employees = instantiate_employees()


@app.route('/', methods=['GET', 'POST'])
def front_page():

    @copy_current_request_context
    def analyze_hours(working_shift: Shift, req_form: request.form):
        for target_emp in shift.staff:
            if target_emp.role == "SUPPORT":
                target_emp.shift_hours = float(req_form[target_emp.name + '-hours'])
                target_emp._tip_hours = target_emp.shift_hours * 0.65
                working_shift.tip_hours += target_emp.tip_hours
            elif target_emp.role == "SERVICE":
                target_emp.shift_hours = float(req_form[target_emp.name + '-hours'])
                target_emp._tip_hours = target_emp.shift_hours
                working_shift.tip_hours += target_emp.tip_hours

    @copy_current_request_context
    def get_cash_subtotal(working_shift: Shift, req_form: request.form) -> float:
        cash_subtotal = 0.0
        for denom in working_shift.cash_subtotals:
            working_shift.cash_subtotals[denom] = float(req_form[denom])
            cash_subtotal += working_shift.cash_subtotals[denom]
        shift.tip_pool = cash_subtotal
        return cash_subtotal

    def get_tip_wage(total_tip_hours: float, cash_total: float) -> float:
        return cash_total / total_tip_hours

    def get_emp_tips(shift_staff: [Employee], tip_wage: float):
        for employee in shift_staff:
            employee._tip_total = employee.tip_hours * tip_wage


    def redirect_url(default='front_page'):
        return request.args.get('next') or request.referrer or url_for(default)

    if request.method == 'GET':
        return render_template('eod_form.html',
                               denominations=denominations,
                               employees=employees,
                               float_range=shift_hours_range)

    if request.method == 'POST':
        rf = request.form
        tip_hours = 0.0
        for emp in employees:
            hours_tag_id = emp.name + '-hours'
            hours = rf[hours_tag_id]
            tip_hours += float(hours)

            role_tag_id = emp.name + '-radio'
            role_radio_value = rf[role_tag_id]
            emp.role(role_radio_value)




        if not (tip_hours > 0):
            error="Form Submitted with Zero Tip Hours"
            return render_template('eod_form.html',
                                   denominations=denominations,
                                   employees=employees,
                                   float_range=shift_hours_range,
                                   error=error)


        shift = Shift(employees, denominations)
        analyze_hours(shift, rf)
        total_cash = get_cash_subtotal(shift, rf)

        shift._tip_wage = get_tip_wage(shift.tip_hours, total_cash)
        get_emp_tips(shift.staff, shift.tip_wage)
        shift._report_total = float(rf['report-tips'])

        if shift.report_total > 0.0:
            shift.cc_wage = shift.report_total / shift.tip_hours
            for emp in shift.staff:
                emp._cc_tips = shift.cc_wage * emp.tip_hours

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        shift._start_date = yesterday.strftime('%A %B %d %Y')

        return render_template('report.html',
                               denominations=denominations,
                               employees=shift.staff,
                               float_range=shift_hours_range,
                               shift=shift,
                               )


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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=port)

