# encoded 'utf-8'

from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect
from flask_login import current_user

# admin = Admin(name="Volstead's Vault")

class CustomAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        name='dashboard'
        endpoint='control'
        return self.render('admin/index.html', name=name, endpoint=endpoint)

# class AdminView(BaseView):
#     # @expose
#     pass

class UserView(ModelView):

    def __init__(self, *args, **kwargs):
        super(UserView, self).__init__(*args, **kwargs)

    page_size = 50
    can_create = True
    can_delete = True
    can_edit = True
    column_exclude_list = []
    column_editable_list = ['username', 'email',]


class RoleView(ModelView):
    can_create = True
    can_delete = False


class EmployeeView(ModelView):
    can_create = True
    can_edit = True
    page_size = 50
    column_exclude_list = []
    column_editable_list = ['first_name', 'last_name',]



class AuthorizationView(ModelView):
    can_create = True
    can_delete = False


class ShiftReportView(ModelView):
    column_exclude_list = []
    column_searchable_list = ['start_date',]


class EmployeeReportView(ModelView):
    column_exclude_list = []
