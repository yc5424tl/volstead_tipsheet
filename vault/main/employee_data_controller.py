# coding=utf-8
from enum import Enum
from typing import ClassVar
from decimal import Decimal
from vault.models import Employee


class TipShare(Enum):
    SERVICE = 1.00
    SUPPORT = 0.65

class EmployeeDataController(object):

    def __init__(self, first_name: str, last_name: str, tip_role: str) -> ClassVar:
        self._first_name = first_name
        self._last_name = last_name
        self._tip_role = tip_role
        self._shift_hours = 0.00
        self._tip_hours = 0.00
        self._cash_tips = 0.00
        self._cred_tips = 0.00

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    @full_name.setter
    def full_name(self, new_full_name):
        self.full_name = new_full_name

    @property
    def first_name(self) -> str:
        return self.first_name

    @first_name.setter
    def first_name(self, new_first_name):
        self.first_name = new_first_name

    @property
    def last_name(self) -> str:
        return self.last_name

    @last_name.setter
    def last_name(self, new_last_name):
        self.last_name = new_last_name

    @property
    def shift_hours(self):
        return self.shift_hours

    @shift_hours.setter
    def shift_hours(self, new_shift_hours):
        self.shift_hours = new_shift_hours

    @property
    def tip_role(self):
        return self.tip_role

    @tip_role.setter
    def tip_role(self, new_role):
        if new_role == "SERVICE" or "SUPPORT" or "MANAGEMENT":
            self.tip_role = new_role

    @property
    def tip_hours(self):
        if self._tip_role == "SERVICE":
            self._tip_hours = self._shift_hours
            return self._tip_hours
        if self._tip_role == "SUPPORT":
            self._tip_hours = self._shift_hours * 0.65
            return self._tip_hours

    @property
    def cash_tips(self):
        return self._cash_tips

    @cash_tips.setter
    def cash_tips(self, tip_wage):
        self._cash_tips = tip_wage * self._tip_hours

    @property
    def cred_tips(self):
        return self._cred_tips

    @cred_tips.setter
    def cred_tips(self, cred_wage):
        self._cred_tips = cred_wage * self._tip_hours

    @property
    def shift_details(self):
        details = "NAME: %s  SHIFT: %f hours  ROLE: %s  TIP-HOURS: %f hours  CC-TIPS: $%f  CASH-TIPS: $%f" \
                  % (self.first_name + ' ' + self.last_name, float(Decimal(self.shift_hours).quantize(Decimal('.01'))), self.tip_role, float(Decimal(self.tip_hours).quantize(Decimal('.01'))), float(Decimal(self.cred_tips).quantize(Decimal('.01'))), float(Decimal(self.cash_tips).quantize(Decimal('.01'))))
        return details

    @staticmethod
    def instantiate_employees(employee_data_list):

        return [EmployeeDataController(emp.first_name, emp.last_name, emp.default_tip_role) for emp in employee_data_list]
        # employee_dict = dict(JACOB=(   "BOLINE",   "SERVICE"),
        #                      CORY=(    "SCHULLER", "SERVICE"),
        #                      INA=(     "DALE",     "SERVICE"),
        #                      ELEANOR=( "JOHNSON",  "SERVICE"),
        #                      JENNIE=(  "SONG",     "SERVICE"),
        #                      HEIDI=(   "LUNDGREN", "SERVICE"),
        #                      CHRIS=(   "THOMPSON", "SERVICE"),
        #                      MARLEY=(  "BARTLETT", "SERVICE"),
        #                      ADAM=  (  "O'BRIEN",  "SUPPORT"),
        #                      REBECCA=( "MOGCK",    "SUPPORT"),
        #                      HARRISON=("EASTON",   "SERVICE"),
        #                      NATALIE=( 'GOODWIN',  "SUPPORT"))
        # return [EmployeeDataController(emp, employee_dict[emp][0], employee_dict[emp][1]) for emp in employee_dict]
        # print('in instantiate emps')
        # primary_employees = Employee
        # for emp in primary_employees:
        #     print('in for loop')
        #     print('printing emp')
        #     print(emp)
        #     print('after printing emp')
        #     print(emp.first_name)
        #     print(emp.last_name)
        #     print(str(type(emp)))
        # print('after emp loop')
        #
        # return [EmployeeDataController(emp.first_name, emp.last_name, emp.default_tip_role) for emp in primary_employees]


