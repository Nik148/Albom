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

class MyBaseView(BaseView):

    def is_accessible(self):
        return admin_permission.can() or moderator_permission.can()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.explore'))

class UserForAdminView(ModelView):

    column_exclude_list = ('password_hash',)
    can_create = True
    can_edit = True
    can_delete = True
    column_searchable_list = ['email']
    column_filters = ['username']
    # Для быстрого редактирования в списке представления
    # column_editable_list = ['username']

    
    def is_accessible(self):
        return admin_permission.can()

class UserForModeratorView(ModelView):

    column_exclude_list = ('password_hash',)
    can_create = False
    can_edit = False
    can_delete = False
    column_searchable_list = ['email']
    column_filters = ['username']
    
    def is_accessible(self):
        return moderator_permission.can()
    # Для быстрого редактирования в списке представления
    # column_editable_list = ['username']


class PostForAdminView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    def is_accessible(self):
        return admin_permission.can()

class PostForModeratorView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False

    def is_accessible(self):
        return moderator_permission.can()

class AnalyticsView(MyBaseView):
    @expose('/')
    def analitics(self):
        return self.render('admin/analytics.html')

class ClaimView(MyBaseView):
    @expose('/')
    def list_claim(self):
        return self.render('admin/analytics.html')

admin = Admin(index_view=MyAdminIndexView())
admin.add_view(UserForAdminView(User, db.session, category='Models', endpoint='user_admin'))
admin.add_view(UserForModeratorView(User, db.session, category='Models', endpoint='user_moderator'))
admin.add_view(PostForAdminView(Post, db.session, category='Models', endpoint='post_admin'))
admin.add_view(PostForModeratorView(Post, db.session, category='Models', endpoint='post_moderator'))
admin.add_sub_category(name='Models', parent_name='Models')
admin.add_view(AnalyticsView(name='Analytics', endpoint='analitics'))
admin.add_view(ClaimView(name='Claim', endpoint='claim'))
