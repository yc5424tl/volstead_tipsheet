# coding=utf-8

import gspread
import simplejson

from app.main.employee_data_controller import EmployeeDataController
from app.main.shift_data_controller import ShiftDataController
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
    print('in get_timedelta_days')
    print('year = ' + str(datetime(year=int(target_date.strftime('%Y')))))
    print('month = ' + str(datetime(month=int(target_date.strftime('%m')))))
    print('day = ' + str(datetime(day=int(target_date.strftime('%d')))))
    formatted_date = datetime(year=int(target_date.strftime('%Y')),
                              month=int(target_date.strftime('%m')),
                              day=int(target_date.strftime('%d')))
    timedelta_day_gap = formatted_date - ref_date
    print('timedelta_day_gap = ' + str(timedelta_day_gap))
    numeric_day_gap = timedelta_day_gap.days
    print('numeric_day_gap = ' + str(numeric_day_gap) + ' is type ' + str(type(numeric_day_gap)))
    return numeric_day_gap



def get_first_match(query: str) -> gspread.Cell or None:
    return tips_sheet.find(query)



def insert_shift_for_emp(shift_row: int, employee: EmployeeDataController) -> bool:
    emp_col = get_first_match(employee.full_name.casefold()).col
    if emp_col:
        tips_sheet.update_cell(row=shift_row, col=emp_col, value=simplejson.dumps(employee.cred_tips, use_decimal=True))
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



def insert_new_row_for_shift(shift: ShiftDataController) -> bool:
    print('shift.start_date = ' + str(shift.start_date))
    shift_timedelta = get_timedelta_days(shift.start_date)
    print('shift_timedelta = ' + str(shift_timedelta))
    shift_row = get_row_by_timedelta(shift_timedelta)
    insert_pool = insert_shift_pool(shift_row, shift.cred_tip_pool)
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
    print('Timedelta.Days = ' + str(timedelta_d))
    current_per_index = timedelta_d % 14
    print(str('Current Period Index (1-13 and 14(0)) = ' + str(current_per_index)))
    completed_periods = timedelta_d // 16
    print('Completed Periods = ' + str(completed_periods))
    pool_col = get_first_match('Total Pool').col
    print('Total Pool Column = ' + str(pool_col))
    if completed_periods >= 1:
        for period in range(1, completed_periods):
            subtotal_row = period * 16 # + TITLE_ROW_OFFSET
            print('Row for subtotal = ' + str(subtotal_row))
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