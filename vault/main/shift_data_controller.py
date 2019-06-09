# coding=utf-8
import json
from .employee_data_controller import EmployeeDataController
from datetime import datetime

denominations = {x:0.0 for x in ['0.25', '1.00', '5.00', '10.00', '20.00', '50.00', '100.00']}

class ShiftDataController(object):

    def __init__(self, staff: [EmployeeDataController]):
        self._staff = staff
        self._shift_hours = 0.00
        self._tip_hours = 0.00
        self._cash_tip_pool = 0.00
        self._cred_tip_pool = 0.00
        self._cash_tip_wage = 0.00
        self._cred_tip_wage = 0.00
        self._start_date = None
        self._cash_subtotals = denominations

    def get_cash_tip_pool(self):
        tip_pool = 0.00
        for denom in self._cash_subtotals:
            tip_pool += self._cash_subtotals[denom]
        self._cash_tip_pool = tip_pool

    def stringify_date(self):
        return self._start_date.strftime('%A %B %d %Y')


    def datify_string(self, date_str: str):
        self.start_date = datetime.strptime(date_str, '%A %B %d %Y')

    def build_staff_reports(self):
        staff_reports = {}
        for emp in self.staff:
            emp_report = {'first_name': emp.first_name,
                          'last_name': emp.last_name,
                          'shift_hours': float(emp.shift_hours),
                          'tip_hours': float(emp.tip_hours),
                          'tip_role': emp.role,
                          'cred_tips': float(emp.cred_tips),
                          'cash_tips': float(emp.cash_tips),
                          'shift_summary': emp.shift_details}
            new_data = {emp.first_name + ' ' + emp.last_name: emp_report}
            staff_reports.update(new_data)
        return staff_reports

    def build_shift_report_dict(self):
        return {
            'start_date':          self.start_date,
            'shift_hours':   float(self.shift_hours),
            'tip_hours':     float(self.tip_hours),
            'cred_tip_pool': float(self.cred_tip_pool),
            'cred_tip_wage': float(self.cred_tip_wage),
            'cash_tip_pool':       self.get_cash_tip_pool(),
            'cash_tip_wage': float(self.cash_tip_wage),
            'cash_subtotals':      self.cash_subtotals,
            'staff_report':        self.build_staff_reports()
        }

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
        self._start_date = new_date

    @property
    def staff(self) -> [EmployeeDataController]:
        return self._staff

    @staff.setter
    def staff(self, staff_list: [EmployeeDataController]) -> None:
        self._staff = staff_list

    @property
    def cred_tip_pool(self) -> float:
        return self._cred_tip_pool

    @cred_tip_pool.setter
    def cred_tip_pool(self, new_total: float) -> None:
        self._cred_tip_pool = new_total

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
    def cash_tip_wage(self) -> float:
        return self._cash_tip_wage

    @cash_tip_wage.setter
    def cash_tip_wage(self, new_tip_wage: float):
        self._cash_tip_wage = new_tip_wage

    @property
    def cred_tip_wage(self) -> float:
        return self._cred_tip_wage

    @cred_tip_wage.setter
    def cred_tip_wage(self, new_cc_wage) -> None:
        self._cred_tip_wage = new_cc_wage

    @property
    def staff_reports(self) -> dict:
        return self.staff_reports

    @staff_reports.setter
    def staff_reports(self, new_report: dict) -> None:
        self.staff_reports = new_report

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)






