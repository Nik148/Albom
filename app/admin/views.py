from app import db, admin_permission, moderator_permission
from flask_admin import BaseView, expose, AdminIndexView, Admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, Post
from flask_login import current_user
from flask import redirect, url_for, current_app


class MyAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return admin_permission.can() or moderator_permission.can()

    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    @expose('/')
    def index(self):
        return self.render('admin/analytics.html',)

class AccessToView(BaseView):

    def is_accessible(self):
        return admin_permission.can() or moderator_permission.can()

class UserView(ModelView, AccessToView):

    column_exclude_list = ('password_hash',)
    can_create = False
    can_edit = False
    can_delete = False
    column_searchable_list = ['email']
    column_filters = ['username']
    # Для быстрого редактирования в списке представления
    # column_editable_list = ['username']

    
    def is_accessible(self):
        return admin_permission.can()

class PostView(ModelView, AccessToView):
    def is_accessible(self):
        return admin_permission.can()

class AnalyticsView(AccessToView):

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.index'))
    @expose('/')
    def analitics(self):
        return self.render('admin/analytics.html')

class ClaimView(AccessToView):
    @expose('/')
    def list_claim(self):
        return self.render('admin/analytics.html')

admin = Admin(index_view=MyAdminIndexView())
admin.add_view(UserView(User, db.session, category='Models'))
admin.add_view(PostView(Post, db.session, category='Models'))
admin.add_sub_category(name='Models', parent_name='Models')
admin.add_view(AnalyticsView(name='Analytics'))
admin.add_view(ClaimView(name='Claim'))
