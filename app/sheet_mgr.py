# coding=utf-8

import gspread
import simplejson

from app.main.employee import Employee
from app.main.shift import Shift
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

cred = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(cred)
sheet = client.open('Copy of Tips').sheet1
tips_sheet = sheet.spreadsheet.get_worksheet(1)

ref_date = datetime(year=2018, month=12, day=30)
TITLE_ROW_OFFSET = 1



def get_row_by_timedelta(timedelta_days: int) -> int:
    full_pay_period_row_groups = (timedelta_days // 14)
    full_periods_remainder = timedelta_days % 14
    target_row_int = ((16 * full_pay_period_row_groups) + full_periods_remainder) + TITLE_ROW_OFFSET
    return target_row_int



def get_timedelta_days(target_date: datetime) -> int:
    formatted_date = datetime(year=int(target_date.strftime('%Y')),
                              month=int(target_date.strftime('%m')),
                              day=int(target_date.strftime('%d')))
    timedelta_day_gap = formatted_date - ref_date
    numeric_day_gap = timedelta_day_gap.days
    return numeric_day_gap



def get_first_match(query: str) -> gspread.Cell or None:
    return tips_sheet.find(query)



def insert_shift_for_emp(shift_row: int, employee: Employee) -> bool:
    emp_col = get_first_match(employee._full_name.casefold()).col
    if emp_col:
        tips_sheet.update_cell(row=shift_row, col=emp_col, value=simplejson.dumps(employee.cc_tips, use_decimal=True))
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
            cont = insert_shift_for_emp(shift_row=shift_row, employee=emp)
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

def check_previous_subtotals(shift_date: datetime):
    timedelta_d = get_timedelta_days(shift_date)
    current_per_index = timedelta_d % 14
    completed_periods = timedelta_d // 16
    pool_col = get_first_match('Total Pool').col
    if completed_periods >= 1:
        for period in range(1, completed_periods):
            subtotal_row = (period * 16) + 1 # + TITLE_ROW_OFFSET
            period_pool_subtotal = tips_sheet.cell(row=subtotal_row, col=pool_col).value
            print('Period Pool Subtotal = ' + str(period_pool_subtotal))
            if period_pool_subtotal is None:
                insert_subtotals_row(subtotal_row)


def end_of_period_check(shift_date: datetime):
    timedelta_days = get_timedelta_days(shift_date)
    period_index = timedelta_days % 14
    completed_periods = timedelta_days // 16
    if period_index == 0:
        subtotal_row = (completed_periods * 16) + 1
        insert_subtotals_row(subtotal_row)

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
            subtotal_row = -1 # -1 == False

    elif period_index == 0:
        subtotal_row = ((complete_periods * 16) + 1 + period_index)

    return subtotal_row