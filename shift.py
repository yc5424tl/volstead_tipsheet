import datetime

from employee import Employee


class Shift(object):

    def __init__(self, staff: [Employee], cash_subtotals: {str: float}):
        self._staff = staff
        self._report_total = 0.0
        self._cash_subtotals = cash_subtotals
        self._tip_hours = 0.0
        self._tip_wage = 0.0
        self._cc_wage = 0.0
        self._start_date = None

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, new_date: datetime.date):
        self._start_date = new_date.strftime('%A %B %d %Y')

    @property
    def staff(self) -> [Employee]:
        return self._staff

    @staff.setter
    def staff(self, staff_list: [Employee]) -> None:
        self._staff = staff_list

    @property
    def report_total(self) -> float:
        return self._report_total

    @report_total.setter
    def report_total(self, new_total: float) -> None:
        self._report_total = new_total

    @property
    def cash_subtotals(self) -> {str: float}:
        return self._cash_subtotals

    @cash_subtotals.setter
    def cash_subtotals(self, new_subtotals: {str: float}) -> None:
        self._cash_subtotals = new_subtotals

    @property
    def tip_hours(self) -> float:
        return self._tip_hours

    @tip_hours.setter
    def tip_hours(self, new_tip_hours: float) -> None:
        self._tip_hours = new_tip_hours

    @property
    def tip_wage(self):
        return self._tip_wage

    @tip_wage.setter
    def tip_wage(self, new_tip_wage: float):
        self._tip_wage = new_tip_wage

    @property
    def cc_wage(self):
        return self._cc_wage

    @cc_wage.setter
    def cc_wage(self, new_cc_wage):
        self._cc_wage = new_cc_wage
