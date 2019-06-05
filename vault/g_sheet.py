# coding=utf-8
import json
import string

import gspread
import os
import simplejson
from flask import current_app

from vault.main.employee_data_controller import EmployeeDataController
from vault.main.shift_data_controller import ShiftDataController
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
# from oauth2client import service_account
from google.oauth2 import service_account
from retrying import retry



scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']


if 'HEROKU_ENV' in os.environ:
    # print('os.environ.get(\'GOOGLE_APPLICATION_CREDENTIALS\')')
    # print(str(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))
    # print('GOOGLE_APPLICATION_CREDENTIALS ---- TYPE ===> ' + str(type(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))))
    # # print('json.loads(GOOGLE_APPLICATION_CREDENTIALS) --- TYPE ===>')
    # # print(str(type(json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))))
    #
    # credentials_raw = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    # dbl_quote_creds = '"' + os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') + '"'
    # print(dbl_quote_creds)
    # print('credentials raw = ' + credentials_raw)
    # dbl_quote_json = json.loads(dbl_quote_creds)
    # print('dbl_quote_json next line')
    # print(dbl_quote_json)
    # # service_account_info = json.loads(json.dumps(credentials_raw))
    # # credentials = service_account.Credentials.from_service_account_info(json.loads(service_account_info))
    # # credentials = service_account.Credentials.from_service_account_info(credentials_raw)
    # with open('client_secret.json', 'w') as json_cred_file:
    #     json_cred_file.write(credentials_raw)
    #
    # print('tyring to open file')
    #
    # with open('client_secret.json', 'r') as json_cred_file:
    #     print(json_cred_file.read())
    #
    # credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    creds = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    with open('gcreds.json', 'w') as json_file:
        json.dump(creds, json_file)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(('gcreds.json', scope))
    client = gspread.authorize(credentials)
    sheet = client.open('Copy of Tips').sheet1
    tips_sheet = sheet.spreadsheet.get_worksheet(1)
else:
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(credentials)
    sheet = client.open('Copy of Tips').sheet1
    tips_sheet = sheet.spreadsheet.get_worksheet(1)
# json_cred = os.getenv('GOOGLE_APPLICATION_CREDS')
# cred_dict = json.loads(json_cred)
# cred_dict['private_key'] = cred_dict['private_key'].replace("\\\\n", "\n")
# creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)
# client = gspread.authorize(credentials)
# cred = ServiceAccountCredentials.from_json(os.getenv("GOOGLE_APP_CREDS"), scope)
# cred = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
# cred = ServiceAccountCredentials.from_json(os.getenv('VOL_CLI_SEC'))
# client = gspread.authorize(cred)
# sheet = client.open('Copy of Tips').sheet1
# tips_sheet = sheet.spreadsheet.get_worksheet(1)

ref_date = datetime(year=2018, month=12, day=30)
# TITLE_ROW_OFFSET = 1

# col_titles = tips_sheet.row_values(row=1)[3:-2]

col_map = dict(enumerate(string.ascii_uppercase, 1))

class GoogleSheetsMgr(object):

    def __init__(self):
        self.emp_col_dict = self.refresh_emp_col_dict()
        self.title_row_offset = 1

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    # 305 secs total, just over the documented 5 min window used by Google to rate limit API calls
    def refresh_emp_col_dict(self):
        self.emp_col_dict = {}
        col_titles = tips_sheet.row_values(row=1)
        for col in col_titles[2:-2]:
            col_num = tips_sheet.find(col).col
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

    @staticmethod
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def get_first_match(query: str) -> gspread.Cell or None:
        return tips_sheet.find(query)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def insert_shift_for_emp(self, shift_row: int, employee: EmployeeDataController) -> bool:
        # emp_col = get_first_match(employee.full_name.casefold()).col
        emp_col = self.emp_col_dict[employee.full_name.casefold()]
        if emp_col:
            tips_sheet.update_cell(row=shift_row, col=emp_col, value=simplejson.dumps(employee.cred_tips, use_decimal=True))
            return True
        return False

    # @staticmethod
    # def bulk_insert_emp_reports(self, shift: ShiftDataController, shift_row: int) -> bool:
    #
    #     cell_list = tips_sheet.range(first_row=shift_row, first_col=3, last_row=shift_row, last_col=tips_sheet.row_values(row=1)[-2].col)
    #
    #     print('cell list next line')
    #     print('cell_list = ' + cell_list)
    #
    #     emp_join = {emp.full_name: col_map[int(col_num)] for (emp, col_num) in (shift.staff,  tips_sheet.row_values(row=1)[3:-2].col)}
    #
    #     print('emp_join values = ')
    #     for k in emp_join:
    #         print(k + ': ' + emp_join[k])
    #
    #
    #     # tips_sheet.update_cells([(tips_sheet.cell.row=shift_row, col=get_first_match(employee.full_name.casefold()).col, value=simplejson.dumps(employee.cred_tips, use_decimal=True)) for employee in shift.staff])
    #     return True



    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=35)
    def insert_shift_pool(self, shift_row: int, shift_pool: float) -> bool:
        if shift_row > 1 and shift_pool > 0:
            pool_col = self.get_first_match('Total Pool').col
            if pool_col:
                tips_sheet.update_cell(row=shift_row, col=pool_col, value=shift_pool)
            return True
        return False

    @staticmethod
    def insert_date_for_shift(shift_row: int, shift_date: datetime) -> bool:
        if shift_row > 1 and (datetime.today() - shift_date).days >= 0:
            tips_sheet.update_cell(row=shift_row, col=1, value=shift_date.strftime('%m/%d/%Y'))
            print('shift date added')
            return True
        print('shift date NOT added')
        return False

    def insert_new_row_for_shift(self, shift: ShiftDataController) -> bool:
        shift_timedelta = self.get_timedelta_days(shift.start_date)
        shift_row = self.get_row_by_timedelta(shift_timedelta)
        insert_pool = self.insert_shift_pool(shift_row, shift.cred_tip_pool)
        insert_date = self.insert_date_for_shift(shift_row, shift.start_date)

        if insert_pool and insert_date:
        #     if self.bulk_insert_emp_reports(shift, shift_row):
        #         return True
        #     else:
        #         return False
            for emp in shift.staff:
                cont = self.insert_shift_for_emp(shift_row=shift_row, employee=emp)
                if not cont:
                    return False
            return True

    @staticmethod
    def insert_subtotals_row(target_row: int) -> bool:
        try:
            tips_sheet.update_cell(row=target_row, col=1, value='Period Totals')
            target_cols = tips_sheet.row_values(row=1)
            first_row = target_row - 14
            last_row = target_row - 1
            for col in target_cols[1:-2]:

                col_num = tips_sheet.find(col).col
                data_subset = tips_sheet.range(first_row, col_num, last_row, col_num)
                subtotal = 0.0
                for cell in data_subset:
                    if cell.value != '':
                        subtotal += float(int(cell.value))
                tips_sheet.update_cell(row=target_row, col=col_num, value=subtotal)
            return True

        except gspread.exceptions.APIError:
            print('gspread.exceptions.APIError in insert_subtotals_row')
            pass



    def check_previous_subtotals(self, shift_date: datetime):
        print('in check_previous_subtotals')
        timedelta_d = self.get_timedelta_days(shift_date)
        print('timedelta_d = ' + str(timedelta_d))
        completed_periods = timedelta_d // 16
        print('completed periods == ' + str(completed_periods))
        pool_col = self.get_first_match('Total Pool').col
        if completed_periods >= 1:
            for period in range(1, completed_periods + 1):
                subtotal_row = period * 16  # do not add 1 for offset
                print('subtotal row = ' + str(subtotal_row))
                period_pool_subtotal = tips_sheet.cell(row=subtotal_row, col=pool_col).value
                print('period_pool_subtotal == ' + str(period_pool_subtotal) + str(type(period_pool_subtotal)))
                if period_pool_subtotal is None or period_pool_subtotal is '':
                    self.insert_subtotals_row(subtotal_row)


    def end_of_period_check(self, shift_date: datetime):
        timedelta_days = self.get_timedelta_days(shift_date)
        period_index = timedelta_days % 14
        completed_periods = timedelta_days // 16
        if period_index == 0:
            subtotal_row = (completed_periods * 16) + 1
            self.insert_subtotals_row(subtotal_row)


    # def get_subtotal_row_if_first_second_last_day(shift_date: datetime) -> int:
    #     timedelta_days = get_timedelta_days(shift_date)
    #     period_index = timedelta_days % 14
    #     complete_periods = timedelta_days // 16
    #     subtotal_row = -1
    #
    #     if period_index == 1 or 2:
    #         subtotal_row = 16 * complete_periods
    #         pool_col = get_first_match('Total Pool').col
    #         period_pool_subtotal = tips_sheet.cell(row=subtotal_row, col=pool_col).value
    #         if period_pool_subtotal != '':
    #             subtotal_row = -1 # -1 == False
    #
    #     elif period_index == 0:
    #         subtotal_row = ((complete_periods * 16) + 1 + period_index)
    #
    #     return subtotal_row