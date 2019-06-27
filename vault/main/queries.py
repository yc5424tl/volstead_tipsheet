from sqlalchemy import and_

from vault.models import Authorization, Employee, EmployeeReport, Role, ShiftReport, User
from datetime import datetime

def earnings_for_year(emp: Employee, year: int):

    shift_range_start = datetime.strptime(f'12/31{str(year-1)}', '%m/%d/%Y')
    shift_range_end = datetime.strptime(f'12/30/{str(year)}', '%m/%d/%Y')

    # EmployeeReport.query.filter_by(employee_id=emp.id).join(ShiftReport, and_(EmployeeReport.c.shift_id == shift.c.id, shift_range_start < ShiftReport.c.start_date < shift_range_end))

    EmployeeReport.join(ShiftReport, and_(EmployeeReport.c.shift_id == ShiftReport.c.id, shift_range_start < ShiftReport.start_date < shift_range_end)).filter_by(emp.id).sum(EmployeeReport.cred_tips)

    reports = EmployeeReport.query.filter_by(employee_id=emp.id).all()

    shifts = ShiftReport.query.filter_by(shift_range_start <= ShiftReport.start_date <= shift_range_end)

