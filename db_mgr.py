# coding=utf-8
from pymongo.errors import DuplicateKeyError
from employee import Employee
from logging import Logger
from pymongo import MongoClient
from flask.ext.pymongo import pymongo
import os
from shift import Shift

mongo = pymongo

class DbController(object):

    def __init__(self, db_port: int, db_host: str, db=None):
        self._db_port = db_port
        self._db_host = db_host
        self._db = db

    def connect_db(self) -> bool:
        try:
            connection = MongoClient(self._db_host, self._db_port)
            self._db = connection[os.getenv('VOL_DB_NAME')]
            self._db.authenticate(os.getenv('VOL_DB_USER'), os.getenv('VOL_DB_PW'))
            # print(self._db.last_status())
            return True
        except ConnectionError:
            return False

    def create_emp_index(self) -> bool:
        try:
            self._db.employee.create_index([('last_name', pymongo.ASCENDING), ('first_name', pymongo.ASCENDING)], unique=True, name='Employee Index')
            return True
        except KeyError:
            return False

    def add_new_emp(self, emp: {Employee}):
        try:
            self._db.employee.update({'first_name': emp.first_name,
                                      'last_name': emp.last_name,
                                      'shift_hours': emp.shift_hours,
                                      'tip_hours': emp.tip_hours,
                                      'tip_role': emp.role,
                                      'tip_total': emp.tip_total})
        except DuplicateKeyError:
            Logger.log(msg='Operation to add new employee encountered a duplicate key.')

    @staticmethod
    def build_staff_report(staff: [Employee]) -> []:
        staff_report = {}
        for emp in staff:
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
        # staff_report.append(emp_report)
        # return staff_report_ = client.open('Copy of Tips').sheet1
        # tips_sheet = sheet.spreadsheet.get_worksheet(1)

    @staticmethod
    def build_shift_report(shift: Shift) -> dict:
        shift.get_cash_tip_pool()
        shift_report = {
            'start_date': shift.start_date,
            'total_shift_hours': float(shift.shift_hours),
            'total_tip_hours': float(shift.tip_hours),
            'cc_tip_pool': float(shift.cc_tip_pool),
            'cc_tip_wage': float(shift.cc_tip_wage),
            'cash_tip_pool': float(shift.cash_tip_pool),
            'cash_tip_wage': float(shift.cash_tip_wage),
            'cash_subtotals': shift.cash_subtotals,
            'staff_report': None
        }
        return shift_report

    def submit_daily_report(self, daily_report) -> bool:
            self._db.test_daily_report.update_one({}, {"$set": daily_report}, upsert=True)
            return True
