import threading

from flask import Flask, render_template, request, copy_current_request_context
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import Config
from numpy import linspace
import datetime

from employee import Employee, TipShare
from shift import Shift

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)

denominations = {'100.00': 0.0, '50.00': 0.0, '20.00': 0.0, '10.00': 0.0, '5.00': 0.0, '1.00': 0.0, '0.25': 0.0}

shift_hours_range = linspace(0.0, 9.0, num=19, retstep=True)


def instantiate_employees():

    employee_dict = dict(JAKE=TipShare.SERVICE,
                         CORY=TipShare.SERVICE,
                         SAM=TipShare.SERVICE,
                         INA=TipShare.SERVICE,
                         ELANEOR=TipShare.SERVICE,
                         JENNIE=TipShare.SERVICE,
                         HEIDI=TipShare.SERVICE,
                         CHRIS=TipShare.SERVICE,
                         MARLEY=TipShare.SERVICE,
                         ADAM=TipShare.SUPPORT,
                         MOCK=TipShare.SUPPORT)

    return [Employee(emp, employee_dict[emp]) for emp in employee_dict]


employees = instantiate_employees()


@app.route('/', methods=['GET', 'POST'])
def front_page():

    @copy_current_request_context
    def analyze_hours(working_shift: Shift, req_form: request.form):
        for target_emp in shift.staff:
            if target_emp.role == TipShare.SUPPORT:
                target_emp.shift_hours = float(req_form[target_emp.name + '-hours'])
                target_emp._tip_hours = round(target_emp.shift_hours * 0.65, 2)
                working_shift.tip_hours += target_emp.tip_hours
            elif target_emp.role == TipShare.SERVICE:
                target_emp.shift_hours = float(req_form[target_emp.name + '-hours'])
                target_emp._tip_hours = target_emp.shift_hours
                working_shift.tip_hours += target_emp.tip_hours

    @copy_current_request_context
    def get_cash_subtotal(working_shift: Shift, req_form: request.form) -> float:
        cash_subtotal = 0.0
        for denom in working_shift.cash_subtotals:
            working_shift.cash_subtotals[denom] = float(req_form[denom])
            cash_subtotal += working_shift.cash_subtotals[denom]
        return cash_subtotal

    def get_tip_wage(tip_hours: float, cash_total: float) -> float:
        return round(cash_total / tip_hours, 2)

    def get_emp_tips(emps: [Employee], tip_wage: float):
        for emp in emps:
            print(emp.name + ' TIP HOURS: ' + str(emp.tip_hours))
            emp._tip_total = emp.tip_hours * tip_wage
            print('CASH TIP: ' + str(emp.tip_total))

    if request.method == 'GET':
        return render_template('eod_form.html',
                               denominations=denominations,
                               employees=employees,
                               float_range=shift_hours_range)

    if request.method == 'POST':

        rf = request.form

        # staff = request.args['employees']
        shift = Shift(employees, denominations)

        analyze_hours(shift, rf)

        total_cash = get_cash_subtotal(shift, rf)
        print('TOTAL CASH: ' + str(total_cash))

        shift._tip_wage = get_tip_wage(shift.tip_hours, total_cash)
        print('TIP WAGE: ' + str(shift.tip_wage))

        get_emp_tips(shift.staff, shift.tip_wage)

        shift._report_total = float(rf['report-tips'])

        for emp in shift.staff:
            details = emp.shift_details
            print(details)

        if shift.report_total > 0:
            shift.cc_wage = round(shift.report_total / shift.tip_hours, 2)
            print('CC WAGE = ' + str(shift.cc_wage))

            for emp in shift.staff:
                emp._cc_tips = round(shift.cc_wage * emp.tip_hours)
                print(emp.name + ' CC TIPS: ' + str(emp.cc_tips))

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        # print('Today is ' + today.isoformat())
        # print('Today is ' + today.strftime('%A %B %d, %Y'))
        print('Shift Start Date: ' + yesterday.strftime('%A %B %d %Y'))
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

# def analyze_hours(shift: Shift, rf: request.form):
#     for emp in shift.staff:
#         if emp.role == TipShare.SUPPORT:
#             emp.shift_hours = float(rf[emp+'-hours'])
#             emp.tip_hours = emp.shift_hours * 0.65
#             shift.tip_hours += emp.tip_hours
#         elif emp.role == TipShare.SERVICE:
#             emp.shift_hours = float(rf[emp+'-hours'])
#             emp.tip_hours = emp.shift_hours
#             shift.tip_hours += emp.tip_hours


# def get_cash_subtotal(shift: Shift, rf: request.form) -> float:
#     cash_subtotal = 0.0
#     for denom in shift.cash_subtotals:
#         shift.cash_subtotals[denom] = float(rf[denom])
#         cash_subtotal += shift.cash_subtotals[denom]
#     return cash_subtotal




if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run()

