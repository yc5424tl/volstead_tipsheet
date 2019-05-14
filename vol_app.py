# coding=utf-8

from app import create_app

app = create_app()

from app.models import User, ShiftReport, Employee, EmployeeReport, UserRoles, Role

@app.shell_context_processor
def make_shell_context():

    return {'db': app.db,
            'User': User,
            'ShiftReport': ShiftReport,
            'Employee': Employee,
            'EmployeeReport': EmployeeReport,
            'Role': Role,
            'UserRoles': UserRoles}