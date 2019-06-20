
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
import time

import gspread
from flask import session, flash
from flask import render_template, copy_current_request_context, url_for, request, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from flask_user import roles_required
from numpy import linspace, os
from vault.main import bp
from vault.main.employee_data_controller import EmployeeDataController
from vault.main.shift_data_controller import ShiftDataController
from vault import db, models
# from vault.models import Employee, ShiftReport, EmployeeReport
from vault.g_sheet import GoogleSheetsMgr
from vault.models import Employee, Role
from retrying import retry


# primary_staff = Employee.query.filter_by(role_id=1).all()
# primary_staff = Employee.query.filter_by(==1).all()
# primary_staff = db.Session.query(db.Employee, db.    Role).join(Role).filter(id=1).all()
# primary_staff = db.session.query(Employee).filter(Employee.role_id==Role.id).filter(Role.id==1)

# primary_staff =  Employee.query.filter_by(role_id = 1)
# alternate_staff = Employee.query.filter_by(role_id=2)
primary_staff = db.session.query(Employee).filter(Employee.role_id == 1)
# primary_staff_data = []
# for emp in primary_staff:
#     primary_staff_data.append([emp.first_name, emp.last_name, emp.default_tip_role])
#     print('in staff loop, current employee is {} {}. Role={}'.format(emp.first_name, emp.last_name, emp.role_id))
primary_staff_data = []
for emp in primary_staff:
    print('in staff loop, current employee is {} {}. Role={}'.format(emp.first_name, emp.last_name, emp.role_id))
    new_emp_data_ctrl = EmployeeDataController(first_name=emp.first_name, last_name=emp.last_name, tip_role=emp.default_tip_role)
    primary_staff_data.append(new_emp_data_ctrl)

# employee_data = [EmployeeDataController(emp.first_name, emp.last_name, emp.default_tip_role) for emp in primary_staff]



shift_hours_range = linspace(0.0, 9.0, num=19, retstep=True)
# employees = EmployeeDataController.instantiate_employees(employee_data) # list of EmployeeDataController objects
# shift = ShiftDataController(employee_data)
# shift = ShiftDataController(primary_staff_data)
g_sheet = GoogleSheetsMgr()
g_sheet.tips_sheet = g_sheet.get_worksheet()
# ringers  = db.Session.query()

# primary_staff = db.session.query(Employee).filter(Employee.role_id==Role.id).filter(Role.id==1)


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_online = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

def redirect_url(default='auth.login'):
    return request.args.get('next') or request.referrer or url_for(default)

def stringify_date(date: datetime):
    return date.strftime('%A %B %d %Y')


@bp.route('/', methods=['GET', "POST'"])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def start_report():
    shift = ShiftDataController(primary_staff_data)

    @copy_current_request_context
    def analyze_hours(working_shift: ShiftDataController, req_form: request.form):
        for target_emp in working_shift.staff:
            target_emp.shift_hours = float(req_form[target_emp.first_name + '-hours'])
            working_shift._shift_hours += target_emp.shift_hours

            if target_emp.tip_role == "SUPPORT":
                target_emp._tip_hours = Decimal(target_emp.shift_hours * 0.65).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
                working_shift.tip_hours += target_emp.tip_hours

            elif target_emp.tip_role == "SERVICE":
                target_emp._tip_hours = target_emp.shift_hours
                working_shift.tip_hours += target_emp.tip_hours

        return True

    @copy_current_request_context
    def get_cash_subtotal(working_shift: ShiftDataController, req_form: request.form) -> float:
        cash_subtotal = 0.00

        for denom in working_shift.cash_subtotals:
            working_shift.cash_subtotals[denom] = float(req_form[denom])
            cash_subtotal += working_shift.cash_subtotals[denom]

        working_shift.cash_tip_pool = cash_subtotal
        return cash_subtotal

    def get_tip_wage(shift_tip_hours: float, cash_total: float) -> float:
        return float(Decimal(cash_total / shift_tip_hours).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

    def get_emp_tips(shift_staff: [EmployeeDataController], tip_wage: float):
        for employee in shift_staff:
            employee._cash_tips = float(Decimal(Decimal(employee.tip_hours) * Decimal(tip_wage)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))



    if request.method == 'GET':
        return render_template('start_report.html',
                               denominations=shift.cash_subtotals,
                               employees=shift.staff,
                               float_range=shift_hours_range,
                               shift=shift)

    if request.method == 'POST':
        rf = request.form
        tip_hours = 0.00
        shift.shift_hours = 0.0
        shift.tip_hours = 0.0

        for staff in shift.staff:
            hours_tag_id = staff.first_name + '-hours'
            hours = float(rf[hours_tag_id])
            tip_hours += hours

            if models.Employee.query.filter_by(first_name=emp.first_name).filter_by(last_name=emp.last_name).count() == 0:
                new_emp_record = models.Employee(first_name=emp.first_name, last_name=emp.last_name)
                db.session.add(new_emp_record)

            if hours > 0:
                role_tag_id = emp.first_name + '-radio'
                role_radio_value = rf[role_tag_id]
                emp.tip_role = role_radio_value

        if not (tip_hours > 0):
            error = "Form Submitted with Zero Tip Hours"
            return render_template('start_report.html',
                                   denominations=shift.cash_subtotals,
                                   employees=shift.staff,
                                   float_range=shift_hours_range,
                                   error=error)

        db.session.commit()
        analyze_hours(shift, rf)
        total_cash = get_cash_subtotal(shift, rf)
        shift._cash_tip_wage = get_tip_wage(tip_hours, total_cash)
        get_emp_tips(shift.staff, shift.cash_tip_wage)
        shift._cred_tip_pool = float(rf['report-tips'])

        if shift.cred_tip_pool > 0.00:
            shift.cred_tip_wage = float(Decimal(shift.cred_tip_pool / shift.tip_hours).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
            for staff in shift.staff:
                staff._cred_tips = float(Decimal(Decimal(shift.cred_tip_wage) * Decimal(staff.tip_hours)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

        today = datetime.today()
        if int(datetime.now().strftime('%H')) >= 17:
            shift._start_date = today
        else:
            yesterday = today - timedelta(days=1)
            shift._start_date = yesterday

        session['shift'] = shift.serialize()
        return render_template('view_report.html',
                               denominations=shift.cash_subtotals,
                               employees=shift.staff,
                               float_range=shift_hours_range,
                               shift=shift,
                               stringify_date=stringify_date)


@bp.route('/register_user', methods=['GET', 'POST'])
@roles_required('Admin')
@login_required
def register_user():
    return render_template('register.html')


def list_of_emp(emp_list) -> bool:
    if isinstance(emp_list, list):
        for emp_data in emp_list:
            if not isinstance(emp_data, EmployeeDataController):
                return False
        return True
    return False


@bp.route('/submit_report', methods=['GET','POST'])
@login_required
def submit_report():


    @copy_current_request_context
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def write_to_g_sheets():
        g_sheet_mgr = GoogleSheetsMgr()
        g_sheet_mgr.tips_sheet = g_sheet_mgr.get_worksheet()
        print('before g_sheet funcs')
        print(g_sheet_mgr.insert_new_row_for_shift(shift))
        print('after insert_new_row_for_shift')
        g_sheet_mgr.check_previous_subtotals(shift.start_date)
        print('after check_previous_subtotals')
        g_sheet_mgr.end_of_period_check(shift.start_date)
        print('after end_of_period_check')

        return render_template('report_archived_confirmation.html', daily_report=shift)

    @copy_current_request_context
    def get_start_date():
        today = datetime.today()
        if int(datetime.now().strftime('%H')) >= 17:
            return today
        else:
            yesterday = today - timedelta(days=1)
            return yesterday

    shift_data = session['shift']
    emp_list = [EmployeeDataController(first_name=e['first_name'], last_name=e['last_name'], tip_role=e['tip_role'], shift_hours=e['shift_hours'], tip_hours=e['tip_hours'], cash_tips=e['cash_tips'], cred_tips=e['cred_tips']) for e in shift_data['staff']]

    shift = ShiftDataController(staff=emp_list, shift_hours=shift_data['shift_hours'], tip_hours=shift_data['tip_hours'], cash_tip_pool=shift_data['cash_tip_pool'], cred_tip_pool=shift_data['cred_tip_pool'], cash_tip_wage=shift_data['cash_tip_wage'], cred_tip_wage=shift_data['cred_tip_wage'], start_date=get_start_date())

    # shift_data = request.form['shift_data']
    # print(shift_data)
    # print(str(type(shift_data)))
    # print(shift_data.staff)
    # print(str(shift_data.shift_hours))
    # print(str(shift_data.tip_hours))
    # print(str(shift_data.cash_tip_pool))
    # print(str(shift_data.cash_tip_wage))

    # if request.method == 'POST':


    # if list_of_emp(employees) and isinstance(shift, ShiftDataController):
    if list_of_emp(primary_staff_data) and isinstance(shift, ShiftDataController):


        new_shift_report = models.ShiftReport.populate_fields(shift)
        db.session.add(new_shift_report)
        db.session.commit()
        new_shift_id = new_shift_report.id


        for employee_report in shift.staff:
            current_emp = models.Employee.query.filter_by(first_name=employee_report.first_name).filter_by(last_name=employee_report.last_name).first()
            new_employee_report = models.EmployeeReport.populate_fields(employee_report=employee_report, shift_id=new_shift_id, employee_id=current_emp.id)
            db.session.add(new_employee_report)

        db.session.commit()

        try:
            write_to_g_sheets()
            # g_sheet_mgr = GoogleSheetsMgr()
            # g_sheet_mgr.tips_sheet = g_sheet_mgr.get_worksheet()
            #
            # print('before g_sheet funcs')
            # print(g_sheet_mgr.insert_new_row_for_shift(shift))
            # print('after insert_new_row_for_shift')
            # g_sheet_mgr.check_previous_subtotals(shift.start_date)
            # print('after check_previous_subtotals')
            # g_sheet_mgr.end_of_period_check(shift.start_date)
            # print('after end_of_period_check')
            #
            # return render_template('report_archived_confirmation.html', daily_report=shift)

        except gspread.exceptions.APIError:
            msg = 'Resource Unavailable Temporarily, Wait 5 Minutes before navigating away from this page.'
            flash(msg)
            time.sleep(301)
            write_to_g_sheets()




# else:
#     print('ERR - request method is ->')
#     print(request.method)


@bp.route('/privacy_policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')
