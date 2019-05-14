# coding=utf-8

from enum import Enum
from typing import ClassVar
from decimal import Decimal


class TipShare(Enum):
    SERVICE = 1.00
    SUPPORT = 0.65


class Employee(object):

    def __init__(self, first_name: str, last_name: str, role: str) -> ClassVar:
        self._first_name = first_name
        self._last_name = last_name
        self._role = role
        self._shift_hours = 0.00
        self._tip_hours = 0.00
        self._cash_tips = 0.00
        self._cc_tips = 0.00

    @property
    def _full_name(self):
        return self.first_name + ' ' + self.last_name

    @_full_name.setter
    def _full_name(self, new_full_name):
        self._full_name = new_full_name

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
    def role(self):
        return self._role

    @role.setter
    def role(self, new_role):
        if new_role == "SERVICE" or "SUPPORT":
            self._role = new_role

    @property
    def tip_hours(self):
        if self._role == "SERVICE":
            self._tip_hours = self._shift_hours
            return self._tip_hours
        if self._role == "SUPPORT":
            self._tip_hours = self._shift_hours * 0.65
            return self._tip_hours

    @property
    def cash_tips(self):
        return self._cash_tips

    @cash_tips.setter
    def cash_tips(self, tip_wage):
        self._cash_tips = tip_wage * self._tip_hours

    @property
    def cc_tips(self):
        return self._cc_tips

    @cc_tips.setter
    def cc_tips(self, cc_wage):
        self._cc_tips = cc_wage * self._tip_hours

    @property
    def shift_details(self):
        details = "NAME: %s  SHIFT: %f hours  ROLE: %s  TIP-HOURS: %f hours  CC-TIPS: $%f  CASH-TIPS: $%f" \
                  % (self.first_name + ' ' + self.last_name, float(Decimal(self.shift_hours).quantize(Decimal('.01'))), self.role, float(Decimal(self.tip_hours).quantize(Decimal('.01'))), float(Decimal(self.cc_tips).quantize(Decimal('.01'))), float(Decimal(self.cash_tips).quantize(Decimal('.01'))))
        return details
