
# from guess_language import guess_language
# from volsteads.main.forms import EditProfileForm, PostForm
# from volsteads.translate import translate
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from flask import render_template, copy_current_request_context, url_for, request, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from numpy import linspace
from volsteads import mongo
from volsteads.models import Employee, Shift
from volsteads.main import bp
from volsteads import db
import sheet_mgr as g_sheet

denominations = {'100.00': 0.00, '50.00': 0.00, '20.00': 0.00, '10.00': 0.00, '5.00': 0.00, '1.00': 0.00, '0.25': 0.00}
shift_hours_range = linspace(0.0, 9.0, num=19, retstep=True)


def instantiate_employees():
    employee_dict = dict(JAKE=("BOLINE", "SERVICE"),
                         CORY=("SCHULLER", "SERVICE"),
                         INA=("DALE", "SERVICE"),
                         ELEANOR=("JOHNSON", "SERVICE"),
                         JENNIE=("SONG", "SERVICE"),
                         HEIDI=("LUNDGREN", "SERVICE"),
                         CHRIS=("THOMPSON", "SERVICE"),
                         MARLEY=("BARTLETT", "SERVICE"),
                         ADAM=("O'BRIEN", "SUPPORT"),
                         REBECCA=("MOGCK", "SUPPORT"))
    return [Employee(emp, employee_dict[emp][0], employee_dict[emp][1]) for emp in employee_dict]

employees = instantiate_employees()
shift = Shift(employees, denominations)

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        mongo.db.session.commit()
    g.locale = str(get_locale())

def redirect_url(default='auth.login'):
    return request.args.get('next') or request.referrer or url_for(default)


@bp.route('/', methods=['GET', "POST'"])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def start_report():
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

    def stringify_date(date: datetime):
        return date.strftime('%A %B %d %Y')

    if request.method == 'GET':
        return render_template('start_report.html',
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
            return render_template('start_report.html',
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

        today = datetime.today()
        if int(datetime.now().strftime('%H')) >= 17:
            # today.strftime('%A %B %d %Y')  # Day of Week, Month, Day, Year
            shift._start_date = today
        else:
            yesterday = today - timedelta(days=1)
            shift._start_date = yesterday

        return render_template('view_report.html', denominations=denominations, employees=shift.staff, float_range=shift_hours_range, shift=shift,
                               stringify_date=stringify_date)



@bp.route('/submit_report', methods=['POST'])
@login_required
def submit_report():
    if request.method == 'POST':
        if employees and shift and employees == {Employee} and type(shift) == Shift:
            shift_report = db.build_shift_report(shift) # -> dict
            staff_report = db.build_staff_report(employees)
            staff_report_dict = {'staff_report': staff_report}
            shift_report = shift_report.update(staff_report_dict)

            try:
                db.submit_daily_report(shift_report)
                print('report submitted to db')
            except Exception:
                print('failure submitting report to db')
                print(Exception.with_traceback(), Exception.__str__())

            try:
                if g_sheet.insert_new_row_for_shift(shift):
                    subtotals_row = g_sheet.subtotals_check(shift.start_date)
                    if subtotals_row == -1:
                        print('Previous period subtotal row already complete.')
                    else:
                        if g_sheet.insert_subtotals_row(target_row=subtotals_row):
                            print('Subtotals row for ' + shift.start_date + ' inserted at row ' + str(subtotals_row))
                        else:
                            print('Error while adding subtotals for ' + shift.start_date + ' to row ' + str(subtotals_row))
            except Exception:
                print('Failure during sheet interaction')
                print(Exception.with_traceback(), Exception.__str__())

            return render_template('report_archived_confirmation.html', daily_report=shift_report)


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
