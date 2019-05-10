# coding=utf-8

import gspread
from app.models import Employee
from app.models import Shift
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# class SheetMgr(object):
#     def __init__(self, scope, client_secret, row_offset=1, creds=None, client=None):
#         self._scope = scope
#         self._client_secret = client_secret
#         self._row_offset = row_offset
#         self._creds = creds
#         self._client = client

    # @property
    # def scope(self):
    #     return self._scope
    #
    # @scope.setter
    # def scope(self, new_scope):
    #     self._scope = new_scope
    #
    # @property
    # def client_secret(self):
    #     return self._client_secret
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

cred = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(cred)

sheet = client.open('Copy of Tips').sheet1
tips_sheet = sheet.spreadsheet.get_worksheet(1)

ref_date = datetime(year=2018, month=12, day=30)
TITLE_ROW_OFFSET = 1
# def get_period(period_number: int) -> bool or dict:
#     if 100 > period_number < 1:
#         return False
#     elif 100 >= period_number >= 1:
#         return {'first_date_row': (period_number - 1) * 16 + 2,
#                 'last_date_row': (period_number - 1) * 16 + 15,
#                 'period_total_row': (period_number - 1) * 16 + 16,
#                 'break_row': (period_number - 1) * 16 + 17}


# def get_individual_period_subtotal(period_num: int, col_title: str):
#     target_row = get_period(period_num)['period_total_row']
#     target_cell = COLS[col_title] + str(target_row)
#     subtotal = tips_sheet.acell(target_cell)
#     return subtotal

def get_row_by_timedelta(timedelta_days: int) -> int:
    full_pay_period_row_groups = (timedelta_days // 14)
    full_periods_remainder = timedelta_days % 14
    target_row_int = ((16 * full_pay_period_row_groups) + full_periods_remainder) + TITLE_ROW_OFFSET
    return target_row_int

def get_timedelta_days(target_date: datetime) -> int:
    formatted_date = datetime(year=int(target_date.strftime('%Y')), month=int(target_date.strftime('%m')), day=int(target_date.strftime('%d')))
    timedelta_day_gap = formatted_date - ref_date
    numeric_day_gap = timedelta_day_gap.days
    # (datetime(year=int(day.strftime('%Y')), month=int(day.strftime('%m')), day=int(day.strftime('%d'))) - ref_date).days
    return numeric_day_gap






  # TO GET ROW FOR SPREADSHEET
        # Target Date = MM/DD/YYYY
        # Reference Date = 12/31/2018
        # Target_Date - Reference_date
        # ref_date = datetime.datetime(year=2018, month=12, day=31)
        # target_date = datetime.datetime(year=int(target_date.strftime('%Y')), month=int(target_date.strftime('%m')), day=int(target_date.strftime('%d')))
        # days_since = target_date - ref_date
        # days_since_numeric_value = days_since.days
        # period = (days_since_numeric_value // 16) + 1  **first part gives # of full periods, add one to get the current period
        # each period takes 16 rows, plus one row at the beginning
        # row_in_period = days_since_numeric_value % 16
        # row = 16 * (period - 1) + 1 + row_in_period

def get_first_match(query: str) -> gspread.Cell or None:
    return tips_sheet.find(query)

def insert_shift_for_emp(shift_row: int, emp_name: str, new_value: float) -> bool:
    emp_col = get_first_match(emp_name).col
    if emp_col:
        tips_sheet.update_cell(row=shift_row, col=emp_col, value=new_value)
        return True
    return False

def insert_shift_pool(shift_row: int, shift_pool: float) -> bool:
    if shift_row > 1 and shift_pool > 0:
        pool_col = get_first_match('Total Pool').col
        if pool_col:
            tips_sheet.update_cell(row=shift_row, col=pool_col, value=shift_pool)
        return True
    return False

def insert_date_for_shift(shift_row: int, shift_date: datetime) -> bool:
    if shift_row > 1 and (datetime.today() - shift_date).days >= 0:
        tips_sheet.update_cell(row=shift_row, col=1, value=shift_date.strftime('%m/%d/%Y'))
        return True
    return False

def insert_new_row_for_shift(shift: Shift) -> bool:
    shift_timedelta = get_timedelta_days(shift.start_date)
    shift_row = get_row_by_timedelta(shift_timedelta)
    insert_pool = insert_shift_pool(shift_row, shift.cc_tip_pool)
    insert_date = insert_date_for_shift(shift_row, shift.start_date)
    if insert_pool and insert_date:
        for emp in shift.staff:
            cont = insert_shift_for_emp(shift_row, emp.full_name, emp.cc_tips)
            if not cont:
                print('Error when inserting employee shift data')
                return False
    return True


def insert_subtotals_row(target_row: int) -> bool:
    tips_sheet.update_cell(row=target_row, col=1, value='Period Totals')
    target_cols = tips_sheet.row_values(row=1)
    first_row = target_row - 14
    last_row = target_row - 1
    for col in target_cols[1:-2]:
        col_num = tips_sheet.find(col).col
        cell_data = tips_sheet.range(first_row=first_row, first_col=col_num, last_row=last_row, last_col=col_num)
        subtotal = 0
        for cell in cell_data:
            subtotal += cell.value
        tips_sheet.update_cell(row=target_row, col=col_num, value=subtotal)
    return True


# def check_if_new_period(shift_date: datetime):
#     timedelta_days = get_timedelta_days(shift_date)
#     day_of_period = timedelta_days % 14
#     print('day out of 14 in current period = ' + str(day_of_period))
#     if day_of_period == 1:
#         prior_periods = timedelta_days // 16
#         subtotal_row = 16 * prior_periods
#         target_cols = tips_sheet.row_values(row=1)
#         for col in target_cols[1:-2]:
#             col_num = tips_sheet.find(col).col
#             first_row = subtotal_row - 14
#             last_row = subtotal_row - 1
#             cell_data = tips_sheet.range(first_row=first_row, first_col=col_num, last_row=last_row, last_col=col_num)
#             subtotal = 0
#             for x in cell_data:
#                 subtotal += x.value
#             tips_sheet.update_cell(row=subtotal_row, col=col, value=subtotal)


# def is_end_of_period(timedelta_days: int) -> bool:
#     day_of_period = timedelta_days % 14
#     print('day out of 14 in current period = ' + str(day_of_period))
#     if day_of_period == 0:
#         return True
#     else:
#         return False


# def get_date_row(day):
#     return 16 * ((datetime(year=int(day.strftime('%Y')), month=int(day.strftime('%m')), day=int(day.strftime('%d'))) - ref_date).days // 16) + ((datetime(year=int(day.strftime('%Y')), month=int(day.strftime('%m')), day=int(day.strftime('%d'))) - ref_date).days % 16) + 3



# should just set up a daily check for 2 conditions:
#       1: Is it the last day of the pay period?
#           Yes -> Compute period subtotals

#       2: Has the previous period's subtotals been computed?
#           No -> Compute previous period subtotals


def get_subtotal_row_if_first_second_last_day(shift_date: datetime) -> int:
    timedelta_days = get_timedelta_days(shift_date)
    period_index = timedelta_days % 14
    complete_periods = timedelta_days // 16
    subtotal_row = -1
    if period_index == 1 or 2:
        subtotal_row = 16 * complete_periods
        pool_col = get_first_match('Total Pool').col
        period_pool_subtotal = tips_sheet.cell(row=subtotal_row, col=pool_col).value
        if period_pool_subtotal != '':
            subtotal_row = -1
    elif period_index == 0:
        subtotal_row = ((complete_periods * 16) + 1 + period_index)
    return subtotal_row

def subtotals_check(shift_date: datetime) -> int:
    timedelta_days = get_timedelta_days(shift_date)
    period_index = timedelta_days % 14
    periods_completed = timedelta_days // 16
    subtotal_row = -1

    if period_index in range(1, 14):
        subtotal_row = 16 * periods_completed
        pool_col = get_first_match('Total Pool').col
        period_pool_subtotal = tips_sheet.cell(row=subtotal_row, col=pool_col).value
        if period_pool_subtotal != '':
            subtotal_row = -1

    elif period_index == 0:
        subtotal_row = ((periods_completed * 16) + 1 + period_index)

    return subtotal_row








# def get_col_titles():
#     return tips_sheet.col_values()
# FUNCTIONS TO WRITE -

#  find_col_by_emp_name()
#       worksheet.col_values() -> list
#       worksheet.find(query) -> first cell matching query
#
#
#    gspread.models.Cell(row, col, value=)
#
#  add_report_data()
#       for emp in report.staff:
#           find_col_by_emp_name()
#           write_emp_cell_data()
#       enter_tip_pool_data()
#
#   compute_period_subtotals()
#
#   check_previous_period_for_completed_subtotals(datetime)
#
#   POSSIBLE UI OPTIONS IF IT IS EASIER THAN USING GOOGLE SHEETS DIRECTLY
#   add_new_employee()
#
#
#
# # print(get_individual_period_subtotal(3, 'Jacob Boline').value)
# test_date = datetime(year=2019, month=3, day=10)
# # days = get_timedelta_days(test_date)
# # print('days = ' + str(days))
# # row = get_row_by_date(days)
# # print('row = ' + str(row))
# # end_of_period = is_end_of_period(days)
# # print(end_of_period)
# # print('COL TITLES: ' + get_col_titles())
# # cell_query = 'Jacob Boline'
# # result = get_first_match(cell_query)
# # print(str(result.col) + ', ' +  str(result.row))
# # print(type(result.col))
# # print(type(result.row))
# # col_titles = tips_sheet.row_values(row=1)
# # for title in col_titles[1:-2]:
# #     print('title: ' + title)
# #     print('value: ' + str(tips_sheet.find(title).col))
#
# blank_cell_value = tips_sheet.cell(row=129, col=2).value
# print("blank cell value == None: ")
# print(blank_cell_value is None)
# print('blank_cell_value = "": ')
# print(blank_cell_value == '')
# print('blank cell value = ' + blank_cell_value)