# coding=utf-8
from vault import create_app

app = create_app()
app.app_context().push()

from vault.models import User, ShiftReport, Employee, EmployeeReport, Role

@app.shell_context_processor
def make_shell_context():
    return {'db': app.db,
            'User': User,
            'ShiftReport': ShiftReport,
            'Employee': Employee,
            'EmployeeReport': EmployeeReport,
            'Role': Role}