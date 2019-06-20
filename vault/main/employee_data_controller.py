# coding=utf-8
from decimal import Decimal
from enum import Enum


class TipShare(Enum):
    SERVICE = 1.00
    SUPPORT = 0.65

class EmployeeDataController(object):

    def __init__(self, first_name: str, last_name: str, tip_role: str, shift_hours=0.00, tip_hours=0.00, cash_tips=0.00, cred_tips=0.00):
        self._first_name = first_name
        self._last_name = last_name
        self._tip_role = tip_role
        self._shift_hours = shift_hours
        self._tip_hours = tip_hours
        self._cash_tips = cash_tips
        self._cred_tips = cred_tips

    def serialize(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'tip_role': self.tip_role,
            'shift_hours': self.shift_hours,
            'tip_hours': self.tip_hours,
            'cash_tips': self.cash_tips,
            'cred_tips': self.cred_tips
        }


    @property
    def full_name(self):
        return self._first_name + ' ' + self._last_name

    @full_name.setter
    def full_name(self, new_full_name):
        self.full_name = new_full_name

    @property
    def first_name(self) -> str:
        return self._first_name

    @first_name.setter
    def first_name(self, new_first_name):
        self._first_name = new_first_name

    @property
    def last_name(self) -> str:
        return self._last_name

    @last_name.setter
    def last_name(self, new_last_name):
        self._last_name = new_last_name

    @property
    def shift_hours(self):
        return self._shift_hours

    @shift_hours.setter
    def shift_hours(self, new_shift_hours):
        self._shift_hours = new_shift_hours

    @property
    def tip_role(self):
        return self._tip_role

    @tip_role.setter
    def tip_role(self, new_role):
        if new_role == "SERVICE" or "SUPPORT" or "MANAGEMENT":
            self._tip_role = new_role

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
                  % (self._first_name + ' ' + self._last_name, float(Decimal(self._shift_hours).quantize(Decimal('.01'))), self._tip_role, float(Decimal(self._tip_hours).quantize(Decimal('.01'))), float(Decimal(self._cred_tips).quantize(Decimal('.01'))), float(Decimal(self._cash_tips).quantize(Decimal('.01'))))
        return details




