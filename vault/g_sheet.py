# coding=utf-8

import string
import gspread
import os
import simplejson
import json
import ast

from vault.main.employee_data_controller import EmployeeDataController
from vault.main.shift_data_controller import ShiftDataController
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
# from oauth2client import service_account
from retrying import retry
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials, _service_account_info



scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']


if 'HEROKU_ENV' in os.environ:
    # credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    # json_creds = os.getenv("G_SRV_ACCT_CRED")
    # print('json_creds ->')
    # print(json_creds)
    # with open('g_srv_acct_cred.json', 'w+') as json_file:
    #     json_file.write(json_creds)
    #     json_file.close()
    # creds_dict = json.loads(json_creds)
    # creds_dict["private_key"] = creds_dict["private_key"].replace("\\\n", "\n")
    # creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    json_creds = json.loads(os.environ.get('G_SRV_ACCT_CRED'))
    print('json_creds ->')
    print(json_creds)
    json_creds = "'" + json_creds + "'"
    credentials = ServiceAccountCredentials.from_json(json_creds)
    client = gspread.authorize(credentials)

    # creds = ServiceAccountCredentials.from_json_keyfile_name('g_srv_acct_cred.json', scope)
    # client = gspread.authorize(creds)
    sheet = client.open('Copy of Tips').sheet1
    tips_sheet = sheet.spreadsheet.get_worksheet(1)

else:
    print('not in heroku env')
    # credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    # credentials = ServiceAccountCredentials.from_json
    json_pycharm = os.environ.get('G_SRV_ACCT_CRED')
    print('json_pycharm ->')
    print(json_pycharm)
    for x in range(0,5):
        print('')
    json_1 = os.environ.get('G_SRV_ACCT_CRED_1')
    print('json_1 ->')
    print(json_1)
    for x in range(0,5):
        print('')
    json_2 = os.environ.get('G_SRV_ACCT_CRED_2')
    print('json_2 ->')
    print(json_2)
    for x in range(0,5):
        print('')

    full_json = json_1.join(json_2)

    print('before config:set')
    os.system('heroku config:set PRIVATE_KEY=%s' % full_json)
    print('after config:set')
    # credentials = ServiceAccountCredentials.from_json()
    json_data = os.environ.get('G_SRV_ACCT_CRED_1').join(os.environ.get('G_SRV_ACCT_CRED_2'))
    print('json_data ->')
    print(json_data)
    print('type json_data = ' + str(type(json_data)))

    try:
        lit_eval = ast.literal_eval(json_data)
        print('lit_eval type == ' + str(type(lit_eval)))
        print(lit_eval)
        print('end lit_eval')
        print('')
    except:
        print('exception with lit eval')

    try:
        json_data_eval = eval(json_data)
        print('json_data_eval ->')
        print(json_data_eval)
        print('type = ' + str(type(json_data_eval)))
        print('')
    except:
        print('exception eval json_data')


    print()
    for x in range(0,5):
        print('')

    print('json_pycharm == json_1.join(json_2) ->')
    print(json_pycharm == json_1.join(json_2))

    credentials = service_account.ServiceAccountCredentials.from_json(json.dumps(ast.literal_eval(json_data)))
    print('credentials type = ' + str(type(credentials)))
    cred_dict = dict(credentials)
    print('cred_dict type = ' + str(type(cred_dict)))
    print('')
    print('cred_dict ->')
    for key in cred_dict:
        print('KEY---> ' + key)
        print('VALUE-> ' + cred_dict[key])
    for x in range(0,3):
        print('')
    client = gspread.authorize(credentials)
    sheet = client.open('Copy of Tips').sheet1


ref_date = datetime(year=2018, month=12, day=30)
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
        emp_col = self.emp_col_dict[employee.full_name.casefold()]
        if emp_col:
            tips_sheet.update_cell(row=shift_row, col=emp_col, value=simplejson.dumps(employee.cred_tips, use_decimal=True))
            return True
        return False


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
            return True
        return False

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
        timedelta_d = self.get_timedelta_days(shift_date)
        completed_periods = timedelta_d // 16
        pool_col = self.get_first_match('Total Pool').col
        if completed_periods >= 1:
            for period in range(1, completed_periods + 1):
                subtotal_row = period * 16  # do not add 1 for offset
                period_pool_subtotal = tips_sheet.cell(row=subtotal_row, col=pool_col).value
                if period_pool_subtotal is None or period_pool_subtotal is '':
                    self.insert_subtotals_row(subtotal_row)


    def end_of_period_check(self, shift_date: datetime):
        timedelta_days = self.get_timedelta_days(shift_date)
        period_index = timedelta_days % 14
        completed_periods = timedelta_days // 16
        if period_index == 0:
            subtotal_row = (completed_periods * 16) + 1
            self.insert_subtotals_row(subtotal_row)
