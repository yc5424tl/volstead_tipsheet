from enum import Enum
from typing import ClassVar


class TipShare(Enum):
    SERVICE = 1.00
    SUPPORT = 0.65


class Employee(object):

    def __init__(self, name: str, role: TipShare) -> ClassVar:

        self._name = name
        self._role = role
        self._shift_hours = 0.00
        self._tip_hours = 0.00
        self._tip_total = 0.00
        self._cc_tips = 0.00

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def shift_hours(self):
        return self._shift_hours

    @shift_hours.setter
    def shift_hours(self, new_shift_hours):
        self._shift_hours = new_shift_hours

    @property
    def role(self):
        if self._role == TipShare.SERVICE:
            return "Service"
        elif self._role == TipShare.SUPPORT:
            return "Support"

    @role.setter
    def role(self, new_role):
        if new_role == TipShare.SERVICE or TipShare.SUPPORT:
            self._role = new_role

    @property
    def tip_hours(self):
        if self._role == TipShare.SERVICE:
            self._tip_hours = self._shift_hours
            return self._tip_hours
        if self._role == TipShare.SUPPORT:
            self._tip_hours = round(self._shift_hours * 0.65, 2)
            return self._tip_hours

    @property
    def tip_total(self):
        return round(self._tip_total, 2)

    @tip_total.setter
    def tip_total(self, tip_wage):
        self._tip_total = round(tip_wage * self._tip_hours, 2)

    @property
    def cc_tips(self):
        return round(self._cc_tips, 2)

    @cc_tips.setter
    def cc_tips(self, cc_wage):
        self._cc_tips = round(cc_wage * self._tip_hours, 2)

    @property
    def shift_details(self):
        details = "NAME: %s  SHIFT: %d hours  ROLE: %s  TIP-HOURS: %d hours  TOTAL-TIPS: $%d " \
                  % (self.name, self.shift_hours, self.role, self.tip_hours, self.tip_total)
        return details
