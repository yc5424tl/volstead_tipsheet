# coding=utf-8

import json
import os
import string
from datetime import datetime

import gspread
import simplejson
from flask import current_app
from oauth2client.service_account import ServiceAccountCredentials
from retrying import retry

from vault.main.employee_data_controller import EmployeeDataController
from vault.main.shift_data_controller import ShiftDataController

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']


ref_date = datetime(year=2018, month=12, day=30)
col_map = dict(enumerate(string.ascii_uppercase, 1))


class GoogleSheetsMgr(object):
    def __init__(self):
        self.tips_sheet = self.get_worksheet()
        self.emp_col_dict = self.refresh_emp_col_dict()
        self.title_row_offset = 1
        self.credentials = None
        self.client = None
        self.tips_sheet = None

    def get_worksheet(self):
        if 'HEROKU_ENV' in os.environ:
            json_cred = json.loads(os.environ.get('G_SRV_ACCT_CRED'))
            self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict=json_cred, scopes=scope)
            self.client = gspread.authorize(self.credentials)
            sheet = self.client.open('Copy of Tips').sheet1
            tips_sheet = sheet.spreadsheet.get_worksheet(1)
            return tips_sheet

        else:
            self.credentials = ServiceAccountCredentials.from_json_keyfile_name('volsteads-f7fca2360881.json', scope)
            self.client = gspread.authorize(self.credentials)
            sheet = self.client.open('Copy of Tips').sheet1
            tips_sheet = sheet.spreadsheet.get_worksheet(1)
            return tips_sheet

    # 305 secs total, just over the documented 5 min window used by Google to rate limit API calls
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def refresh_emp_col_dict(self):
        self.emp_col_dict = {}
        col_titles = self.tips_sheet.row_values(row=1)
        for col in col_titles[2:-2]:
            col_num = self.tips_sheet.find(col).col
            self.emp_col_dict[col] = col_num
        return self.emp_col_dict

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def get_row_by_timedelta(self, timedelta_days: int) -> int:
        full_pay_period_row_groups = (timedelta_days // 14)
        full_periods_remainder = timedelta_days % 14
        target_row_int = ((16 * full_pay_period_row_groups) + full_periods_remainder) + self.title_row_offset
        return target_row_int

    @staticmethod
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def get_timedelta_days(target_date: datetime) -> int:
        formatted_date = datetime(year=int(target_date.strftime('%Y')),
                                  month=int(target_date.strftime('%m')),
                                  day=int(target_date.strftime('%d')))
        timedelta_day_gap = formatted_date - ref_date
        numeric_day_gap = timedelta_day_gap.days
        return numeric_day_gap

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def get_first_match(self, query: str) -> gspread.Cell or None:
        return self.tips_sheet.find(query)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def insert_shift_for_emp(self, shift_row: int, employee: EmployeeDataController) -> bool:
        emp_col = self.emp_col_dict[employee.full_name]
        if emp_col:
            self.tips_sheet.update_cell(row=shift_row, col=emp_col, value=simplejson.dumps(employee.cred_tips, use_decimal=True))
            return True
        return False

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def insert_shift_pool(self, shift_row: int, shift_pool: float) -> bool:
        if shift_row > 1 and shift_pool > 0:
            pool_col = self.get_first_match('TOTAL POOL').col
            if pool_col:
                self.tips_sheet.update_cell(row=shift_row, col=pool_col, value=shift_pool)
            return True
        return False


    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def insert_date_for_shift(self, shift_row: int, shift_date: datetime) -> bool:
        if shift_row > 1 and (datetime.today() - shift_date).days >= 0:
            self.tips_sheet.update_cell(row=shift_row, col=1, value=shift_date.strftime('%m/%d/%Y'))
            return True
        return False

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def insert_new_row_for_shift(self, shift: ShiftDataController) -> bool:
        shift_timedelta = self.get_timedelta_days(shift.start_date)
        shift_row = self.get_row_by_timedelta(shift_timedelta)
        insert_pool = self.insert_shift_pool(shift_row, shift.cred_tip_pool)
        insert_date = self.insert_date_for_shift(shift_row, shift.start_date)
        if insert_pool and insert_date:
            for emp in shift.staff:
                cont = self.insert_shift_for_emp(shift_row=shift_row, employee=emp)
                if not cont:
                    return False
            return True
        else:
            return False


    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def insert_subtotals_row(self, target_row: int) -> bool:
        try:
            self.tips_sheet.update_cell(row=target_row, col=1, value='Period Totals')
            target_cols = self.tips_sheet.row_values(row=1)
            first_row = target_row - 14
            last_row = target_row - 1
            for col in target_cols[1:-2]:
                col_num = self.tips_sheet.find(col).col
                data_subset = self.tips_sheet.range(first_row, col_num, last_row, col_num)
                subtotal = 0.0
                for cell in data_subset:
                    if cell.value != '':
                        subtotal += float(int(cell.value))
                self.tips_sheet.update_cell(row=target_row, col=col_num, value=subtotal)
            return True
        except gspread.exceptions.APIError:
            current_app.logger.error('gspread.exceptions.APIError in insert_subtotals_row')
            return False


    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def check_previous_subtotals(self, shift_date: datetime):

        timedelta_d = self.get_timedelta_days(shift_date)
        completed_periods = timedelta_d // 16
        pool_col = self.get_first_match('TOTAL POOL').col

        if completed_periods >= 1:

            for period in range(1, completed_periods + 1):
                subtotal_row = period * 16  # do not add 1 for offset
                period_pool_subtotal = self.tips_sheet.cell(row=subtotal_row, col=pool_col).value

                if period_pool_subtotal is None or period_pool_subtotal is '':
                    self.insert_subtotals_row(subtotal_row)


    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def end_of_period_check(self, shift_date: datetime):

        timedelta_days = self.get_timedelta_days(shift_date)
        period_index = timedelta_days % 14
        completed_periods = timedelta_days // 16

        if period_index == 0:
            subtotal_row = (completed_periods * 16) + 1
            self.insert_subtotals_row(subtotal_row)
