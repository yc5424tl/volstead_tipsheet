
from app.main.employee import Employee
from datetime import datetime


class Shift(object):

    def __init__(self, staff: [Employee], cash_subtotals: {str: float}):
        self._staff = staff
        self._cc_tip_pool = 0.00
        self._cash_subtotals = cash_subtotals
        self._shift_hours = 0.00
        self._tip_hours = 0.00
        self._cash_tip_wage = 0.00
        self._cc_tip_wage = 0.00
        self._start_date = None
        self._cash_tip_pool = 0.00

    def get_cash_tip_pool(self):
        tip_pool = 0.00
        for denom in self._cash_subtotals:
            tip_pool += self._cash_subtotals[denom]
        self._cash_tip_pool = tip_pool

    def stringify_date(self):
        return self._start_date.strftime('%A %B %d %Y')

    @property
    def cash_tip_pool(self):
        return self._cash_tip_pool

    @cash_tip_pool.setter
    def cash_tip_pool(self, new_tip_pool):
        self._cash_tip_pool = new_tip_pool

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, new_date: datetime):
        # self._start_date = new_date.strftime('%A %B %d %Y')
        self._start_date = new_date

    @property
    def staff(self) -> [Employee]:
        return self._staff

    @staff.setter
    def staff(self, staff_list: [Employee]) -> None:
        self._staff = staff_list

    @property
    def cc_tip_pool(self) -> float:
        return self._cc_tip_pool

    @cc_tip_pool.setter
    def cc_tip_pool(self, new_total: float) -> None:
        self._cc_tip_pool = new_total

    @property
    def cash_subtotals(self) -> {str: float}:
        return self._cash_subtotals

    @cash_subtotals.setter
    def cash_subtotals(self, new_subtotals: {str: float}) -> None:
        self._cash_subtotals = new_subtotals

    @property
    def shift_hours(self) -> float:
        return self._shift_hours

    @shift_hours.setter
    def shift_hours(self, new_shift_hours: float) -> None:
        self._shift_hours = new_shift_hours

    @property
    def tip_hours(self) -> float:
        return self._tip_hours

    @tip_hours.setter
    def tip_hours(self, new_tip_hours: float) -> None:
        self._tip_hours = new_tip_hours

    @property
    def cash_tip_wage(self):
        return self._cash_tip_wage

    @cash_tip_wage.setter
    def cash_tip_wage(self, new_tip_wage: float):
        self._cash_tip_wage = new_tip_wage

    @property
    def cc_tip_wage(self):
        return self._cc_tip_wage

    @cc_tip_wage.setter
    def cc_tip_wage(self, new_cc_wage):
        self._cc_tip_wage = new_cc_wage


    def build_staff_report(self):
        staff_report = {}
        for emp in self.staff:
            emp_report = {'first_name': emp.first_name,
                          'last_name': emp.last_name,
                          'shift_hours': float(emp.shift_hours),
                          'tip_hours': float(emp.tip_hours),
                          'tip_role': emp.role,
                          'cc_tips': float(emp.cc_tips),
                          'cash_tips': float(emp.cash_tips),
                          'shift_summary': emp.shift_details}
            new_data = {emp.full_name: emp_report}
            staff_report.update(new_data)
        return staff_report

    def build_shift_report(self):
        return {
            'start_date': self.start_date,
            'total_shift_hours': float(self.shift_hours),
            'cc_tip_pool': float(self.cc_tip_pool),
            'cc_tip_wage': float(self.cc_tip_wage),
            'cash_tip_pool': self.get_cash_tip_pool(),
            'cash_tip_wage': float(self.cash_tip_wage),
            'cash_subtotals': self.cash_subtotals,
            'staff_report': self.build_staff_report()
        }




