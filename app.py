
# from flask import Flask, render_template, request, copy_current_request_context
# from flask_bootstrap import Bootstrap
# from flask_sqlalchemy import SQLAlchemy
# from config import Config
# from numpy import linspace
# import datetime
import datetime
from flask import Flask, copy_current_request_context, request, render_template
from flask_bootstrap import Bootstrap
# from flask_sqlalchemy import SQLAlchemy
from numpy import linspace

from config import Config
from employee import Employee, TipShare
from shift import Shift
import os

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
# db = SQLAlchemy(app)

denominations = {'100.00': 0.0, '50.00': 0.0, '20.00': 0.0, '10.00': 0.0, '5.00': 0.0, '1.00': 0.0, '0.25': 0.0}

shift_hours_range = linspace(0.0, 9.0, num=19, retstep=True)


def instantiate_employees():

    employee_dict = dict(JAKE="SERVICE",
                         CORY="SERVICE",
                         SAM="SERVICE",
                         INA="SERVICE",
                         ELEANEOR="SERVICE",
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

    def get_tip_wage(tip_hours: float, cash_total: float) -> float:
        return cash_total / tip_hours

    def get_emp_tips(emps: [Employee], tip_wage: float):
        for emp in emps:
            emp._tip_total = emp.tip_hours * tip_wage

    if request.method == 'GET':
        return render_template('eod_form.html',
                               denominations=denominations,
                               employees=employees,
                               float_range=shift_hours_range)

    if request.method == 'POST':
        rf = request.form
        shift = Shift(employees, denominations)
        analyze_hours(shift, rf)
        total_cash = get_cash_subtotal(shift, rf)
        # print("tip hours " + str(shift.tip_hours))
        # print("total cash : " + str(total_cash))
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
        print('DENOM SUBTOTAL FOR ' + str(denom) + ' EQUALS ' + str(subtotal))
        if subtotal > 0:
            modulated_subtotal = float(subtotal) % float(denom)
            print('MODULATED SUBTOTAL = ' + str(modulated_subtotal))
            if modulated_subtotal != 0:
                return False

    return True


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=port)

