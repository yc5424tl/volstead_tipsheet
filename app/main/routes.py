
# from guess_language import guess_language
# from volsteads.main.forms import EditProfileForm, PostForm
# from volsteads.translate import translate

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from flask import jsonify, render_template, session, copy_current_request_context, url_for, request, g, app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from flask_user import roles_required

from numpy import linspace
from app.main import bp
from app.main.employee_data_controller import EmployeeDataController

from app.main.shift_data_controller import ShiftDataController
# from config import Config
import app.sheet_mgr as g_sheet
import app.models as models
from app import db

shift_hours_range = linspace(0.0, 9.0, num=19, retstep=True)

employees = EmployeeDataController.instantiate_employees()
shift = ShiftDataController(employees)

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()
    g.locale = str(get_locale())

def redirect_url(default='auth.login'):
    return request.args.get('next') or request.referrer or url_for(default)

def stringify_date(date: datetime):
    return date.strftime('%A %B %d %Y')


@bp.route('/', methods=['GET', "POST'"])
@bp.route('/index', methods=['GET', 'POST'])
# @login_required
def start_report():
    @copy_current_request_context
    def analyze_hours(working_shift: ShiftDataController, req_form: request.form):
        for target_emp in shift.staff:

            target_emp.shift_hours = float(req_form[target_emp.first_name + '-hours'])
            shift._shift_hours += target_emp.shift_hours

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

        shift.cash_tip_pool = cash_subtotal
        return cash_subtotal

    def get_tip_wage(shift_tip_hours: float, cash_total: float) -> float:
        return float(Decimal(cash_total / shift_tip_hours).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

    def get_emp_tips(shift_staff: [EmployeeDataController], tip_wage: float):
        for employee in shift_staff:
            employee._cash_tips = float(Decimal(Decimal(employee.tip_hours) * Decimal(tip_wage)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))



    if request.method == 'GET':
        return render_template('start_report.html',
                               denominations=shift.cash_subtotals,
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
                emp.tip_role = role_radio_value

        if not (tip_hours > 0):
            error = "Form Submitted with Zero Tip Hours"
            return render_template('start_report.html',
                                   denominations=shift.cash_subtotals,
                                   employees=employees,
                                   float_range=shift_hours_range,
                                   error=error)

        analyze_hours(shift, rf)
        total_cash = get_cash_subtotal(shift, rf)
        shift._cash_tip_wage = get_tip_wage(tip_hours, total_cash)
        get_emp_tips(shift.staff, shift.cash_tip_wage)
        shift._cred_tip_pool = float(rf['report-tips'])

        if shift.cred_tip_pool > 0.00:
            shift.cred_tip_wage = float(Decimal(shift.cred_tip_pool / shift.tip_hours).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
            for emp in shift.staff:
                emp._cred_tips = float(Decimal(Decimal(shift.cred_tip_wage) * Decimal(emp.tip_hours)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

        today = datetime.today()
        if int(datetime.now().strftime('%H')) >= 17:
            # today.strftime('%A %B %d %Y')  # Day of Week, Month, Day, Year
            shift._start_date = today
        else:
            yesterday = today - timedelta(days=1)
            shift._start_date = yesterday



        shift_data = {'shift_hours': str(shift.shift_hours),
                            'tip_hours': str(shift.tip_hours),
                            'cash_tip_wage': str(shift.cash_tip_wage),
                            'cred_tip_wage': str(shift.cred_tip_wage),
                            'cash_tip_pool': str(shift.cash_tip_pool),
                            'cred_tip_pool': str(shift.cred_tip_pool),
                            'start_date': stringify_date(shift.start_date)}
        print('shift_data = ' + str(shift_data))
        print('shift_data_type = ' + str(type(shift_data)))
        session['shift'] = jsonify(shift_data)

        for emp in employees:
            emp_data = {
                'tip_hours': str(emp.tip_hours),
                'shift_hours': str(emp.shift_hours),
                'tip_role': str(emp.tip_role),
                'cred_tips': str(emp.cred_tips),
                'cash_tips': str(emp.cash_tips),
                'first_name': str(emp.first_name),
                'last_name': str(emp.last_name)
            }
            print('emp_date = ' + str(emp_data))
            session_title = emp.first_name + ' ' + emp.last_name
            session[session_title] = jsonify(emp_data)


        subtotals_data = {x: shift.cash_subtotals[x] for x in ('0.25', '1.00', '5.00', '10.00', '20.00', '50.00', '100.00')}
        session['subtotals'] = jsonify(subtotals_data)

        return render_template('view_report.html',
                               denominations=shift.cash_subtotals,
                               employees=shift.staff,
                               float_range=shift_hours_range,
                               shift=shift,
                               stringify_date=stringify_date)


@bp.route('/register_user', methods=['GET', 'POST'])
# @login_required
# @roles_required('Admin')
def register_user():
    return render_template('register.html')

def list_of_emp(emp_list) -> bool:
    if isinstance(emp_list, list):
        for emp in emp_list:
            if not isinstance(emp, EmployeeDataController):
                print('isinstance(emp, Employee) = ' + str(isinstance(emp, EmployeeDataController)))
                return False
        return True
    return False


@bp.route('/submit_report', methods=['POST'])
# @login_required
def submit_report():
    session_shift = json.loads(session['shift'])
    print('shift: ')
    print(session_shift)
    if request.method == 'POST':
        session_shift = session['shift']
        session_shift = json.loads(session_shift)
        print('isinstance(employees, {Employee} = ' + str(list_of_emp(employees)))
        print('isinstance(shift, Shift) = ' + str(isinstance(session_shift, ShiftDataController)))
        if list_of_emp(employees) and isinstance(session_shift, ShiftDataController):
            print('Correct types for shift and employees passed.')
            print('session_shift.start_date on next line')
            print(str(session_shift.start_date))
            print('after start_date print')
            g_sheet.insert_new_row_for_shift(session_shift)
            # CHECK if prior subtotal rows have data
            g_sheet.check_previous_subtotals(session_shift.start_date)
            # CHECK if start_date is last day in period
            g_sheet.end_of_period_check(session_shift.start_date)

            print('session_shift.cash_tip_wage is float = ' + str(isinstance(session_shift.cash_tip_wage, float)))
            print('session_shift.cash_tip_wage is Decimal = ' + str(isinstance(session_shift.cash_tip_wage, Decimal)))
            print('Decimal value = ' + str(session_shift.cash_tip_wage))
            print('Cast Decimal to Float value = ' + str(float(session_shift.cash_tip_wage)))

            new_shift_report = models.ShiftReport()
            new_shift_report.populate_fields(session_shift)
            db.session.add(new_shift_report)
            new_shift_id = new_shift_report.id
            print('new_shift_id = ' + str(new_shift_id))

            new_cash_subtotals = models.CashSubtotals()
            new_cash_subtotals.populate_fields(session_shift, new_shift_id)
            db.session.add(new_cash_subtotals)
            print('passed db.session.add(new_cash_subtotals) ln 179: routes.py')


            for employee_report in session_shift.staff:
                print('beginning for employee_report in session_shift.staff loop')
                query_name = employee_report.first_name + ' ' + employee_report.last_name
                print('query_name = ' + query_name)
                target_employee = models.Employee.query.filter_by(full_name=query_name).first()
                print('target_employee first/last name = ' + target_employee.first_name + ' ' + target_employee.last_name)
                target_employee_id = target_employee.id
                print('target_employee_id = ' + str(target_employee_id))
                employee_id = models.Employee.query.get(full_name=query_name).id
                new_employee_report = models.EmployeeReport()
                new_employee_report.populate_fields(employee=employee_report, shift_id=new_shift_id, employee_id=employee_id)




            db.session.commit()




            # shift_report = shift.build_shift_report() # -> dict
            # staff_report = db.build_staff_report(employees)
            # staff_report_dict = {'staff_report': staff_report}
            # shift_report = shift_report.update(staff_report_dict)

            # try:
            #     db.submit_daily_report(shift_report)
            #     print('report submitted to db')
            # except Exception:
            #     print('failure submitting report to db')
            #     print(Exception.with_traceback(), Exception.__str__())
            #
            # try:
            #     if g_sheet.insert_new_row_for_shift(shift):
            #         subtotals_row = g_sheet.subtotals_check(shift.start_date)
            #         if subtotals_row == -1:
            #             print('Previous period subtotal row already complete.')
            #         else:
            #             if g_sheet.insert_subtotals_row(target_row=subtotals_row):
            #                 print('Subtotals row for ' + shift.start_date + ' inserted at row ' + str(subtotals_row))
            #             else:
            #                 print('Error while adding subtotals for ' + shift.start_date + ' to row ' + str(subtotals_row))
            # except Exception:
            #     print('Failure during sheet interaction')
            #     print(Exception.with_traceback(), Exception.__str__())

            return render_template('report_archived_confirmation.html', daily_report=session_shift)


@bp.route('/privacy_policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')


# def index():
#     form = PostForm()
#     if form.validate_on_submit():
#         # language = guess_language(form.post.data)
#         #if language == 'UNKNOWN' or len(language) > 5:
#         #    language = ''
#         # post = Post(body=form.post.data, author=current_user, language=language)
#         # mongo.db.session.add(post)
#         # mongo.db.session.commit()
#         flash(_('Added to live website.'))
#         return redirect(url_for('main.index'))
#     # page = request.args.get('page', 1, type=int)
#     #
#     return render_template('start_report.html', title=_('Home'), form=form)

#
    # posts = local_user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    # prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    # return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)
