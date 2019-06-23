
import time
import itertools
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

import gspread
from flask import session, flash, render_template, copy_current_request_context, url_for, request, g
from flask_babel import get_locale
from flask_login import current_user, login_required
from flask_user import roles_required
from numpy import linspace
from retrying import retry

from vault import db, models
from vault.g_sheet import GoogleSheetsMgr
from vault.main import bp
from vault.main.employee_data_controller import EmployeeDataController
from vault.main.shift_data_controller import ShiftDataController
from vault.models import Employee



def get_staff_data(role_id):
    staff = db.session.query(Employee).filter(Employee.role_id == role_id)
    staff_data = []
    for emp in staff:
        new_emp_data_ctrl = EmployeeDataController(first_name=emp.first_name, last_name=emp.last_name, tip_role=emp.default_tip_role)
        staff_data.append(new_emp_data_ctrl)
    return staff_data

shift_hours_range = linspace(0.0, 9.0, num=19, retstep=True)
g_sheet = GoogleSheetsMgr()
g_sheet.tips_sheet = g_sheet.get_worksheet()

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

def list_of_emp(emp_list) -> bool:
    if isinstance(emp_list, list):
        for emp_data in emp_list:
            if not isinstance(emp_data, EmployeeDataController):
                return False
        return True
    return False

def get_shift_date():
    today = datetime.today()
    if int(datetime.now().strftime('%H')) >= 17:
       return today
    else:
        yesterday = today - timedelta(days=1)
        return yesterday



#=====================================================================================================================
# START REPORT @ '/' '/index
#=====================================================================================================================

@bp.route('/', methods=['GET', "POST'"])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def start_report():

    if request.method == 'GET':
        primary_staff_data = get_staff_data(role_id=1)
        alt_staff_data = get_staff_data(role_id=2)
        shift = ShiftDataController(staff=primary_staff_data, alt_staff=alt_staff_data)
        return render_template('start_report.html', float_range=shift_hours_range, shift=shift)


    if request.method == 'POST':
        rf = request.form
        primary_staff_data = get_staff_data(role_id=1)
        alt_staff_data = get_staff_data(role_id=2)
        shift = ShiftDataController(staff=primary_staff_data, alt_staff=alt_staff_data)

        for emp in itertools.chain(shift.staff, shift.alt_staff):
            if models.Employee.query.filter_by(first_name=emp.first_name).filter_by(last_name=emp.last_name).count() == 0:
                new_emp_record = models.Employee(first_name=emp.first_name, last_name=emp.last_name)
                db.session.add(new_emp_record)
            hours_tag_id = emp.first_name + emp.last_name + '-hours'
            hours = float(rf[hours_tag_id])
            if hours > 0.0:
                shift.shift_hours += hours
                emp._shift_hours = hours
                staff_role_tag_id = emp.first_name + emp.last_name + '-radio'
                emp._tip_role = rf[staff_role_tag_id]
                if emp.tip_role == 'SUPPORT':
                    emp._tip_hours = Decimal(emp.shift_hours * 0.65).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
                    shift.tip_hours += emp.tip_hours
                if emp.tip_role == 'SERVICE':
                    emp._tip_hours = emp.shift_hours
                    shift.tip_hours += emp.tip_hours

        db.session.commit()

        for denom in shift.cash_subtotals:
            shift.cash_subtotals[denom] = float(rf[denom])
            shift.cash_tip_pool += float(rf[denom])

        shift.cash_tip_wage = float(Decimal(shift.cash_tip_pool / shift.tip_hours).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
        shift.cred_tip_pool = float(rf['report-tips'])
        shift.cred_tip_wage = float(Decimal(shift.cred_tip_pool / shift.tip_hours).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

        for emp in itertools.chain(shift.staff, shift.alt_staff):
            emp._cash_tips = float(Decimal(Decimal(shift.cash_tip_wage) * Decimal(emp.tip_hours)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
            emp._cred_tips = float(Decimal(Decimal(shift.cred_tip_wage) * Decimal(emp.tip_hours)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

        shift.start_date = get_shift_date()

        session['shift'] = shift.serialize()

        if shift.shift_hours and shift.cash_tip_pool and shift.cred_tip_pool:
            return render_template('view_report.html', shift=shift, stringify_date=stringify_date)

        else:
            error = "Total hours, total cash tips, and total credit tips must be non zero."
            return render_template('start_report.html', float_range=shift_hours_range, error=error)


#=====================================================================================================================
# REGISTER USER @ '/register_user'
#=====================================================================================================================

@bp.route('/register_user', methods=['GET', 'POST'])
@roles_required('Admin')
@login_required
def register_user():
    return render_template('register.html')


#=====================================================================================================================
# SUBMIT REPORT @ '/submit_report'
#=====================================================================================================================

@bp.route('/submit_report', methods=['GET','POST'])
@login_required
def submit_report():

    @copy_current_request_context
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def write_to_g_sheets(shift_ctrl):
        g_sheet_mgr = GoogleSheetsMgr()
        g_sheet_mgr.tips_sheet = g_sheet_mgr.get_worksheet()
        g_sheet_mgr.insert_new_row_for_shift(shift_ctrl)
        g_sheet_mgr.check_previous_subtotals(shift_ctrl.start_date)
        g_sheet_mgr.end_of_period_check(shift_ctrl.start_date)
        return render_template('report_archived_confirmation.html', daily_report=shift_ctrl)

    shift_data = session['shift']

    shift = ShiftDataController(
        staff         =[EmployeeDataController(first_name=e['first_name'], last_name=e['last_name'], tip_role=e['tip_role'], shift_hours=float(e['shift_hours']),   tip_hours=float(e['tip_hours']), cash_tips=float(e['cash_tips']), cred_tips=float(e['cred_tips'])) for e in shift_data['staff']],
        alt_staff     =[EmployeeDataController(first_name=a['first_name'], last_name=a['last_name'], tip_role=a['tip_role'], shift_hours=float(a['shift_hours']), tip_hours=float(a['tip_hours']), cash_tips=float(a['cash_tips']), cred_tips=float(a['cred_tips'])) for a in shift_data['alt_staff']],
        shift_hours   = float(shift_data['shift_hours']),
        tip_hours     = float(shift_data['tip_hours']),
        cash_tip_pool = float(shift_data['cash_tip_pool']),
        cred_tip_pool = float(shift_data['cred_tip_pool']),
        cash_tip_wage = float(shift_data['cash_tip_wage']),
        cred_tip_wage = float(shift_data['cred_tip_wage']),
        start_date    = get_shift_date())

    primary_staff_data = get_staff_data(role_id=1)
    alt_staff_data = get_staff_data(role_id=2)

    if list_of_emp(primary_staff_data) and list_of_emp(alt_staff_data) and isinstance(shift, ShiftDataController):
        new_shift_report = models.ShiftReport.populate_fields(shift)
        db.session.add(new_shift_report)
        db.session.commit()
        new_shift_id = new_shift_report.id

        for emp_report in itertools.chain(shift.staff, shift.alt_staff):

            current_emp = models.Employee.query.filter_by(first_name=emp_report.first_name).filter_by(last_name=emp_report.last_name).first()
            new_employee_report = models.EmployeeReport.populate_fields(employee_report=emp_report, shift_id=new_shift_id, employee_id=current_emp.id)
            if new_employee_report.shift_hours > 0.0:
                db.session.add(new_employee_report)

        db.session.commit()

        try:
            write_to_g_sheets(shift)
        except gspread.exceptions.APIError:
            msg = 'Resource Unavailable Temporarily, Wait 5 Minutes before navigating away from this page.'
            flash(msg)
            time.sleep(301)
            write_to_g_sheets(shift)

        return render_template('report_archived_confirmation.html', daily_report=shift)
    return render_template('404.html')


#=====================================================================================================================
# PRIVACY POLICY @ '/privacy_policy
#=====================================================================================================================

@bp.route('/privacy_policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')
