from app import admin, db
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from app.models import User, Post

class UserView(ModelView):
    column_exclude_list = ('password_hash',)
    can_create = True
    # can_edit = False
    can_delete = True
    column_searchable_list = ['email']
    column_filters = ['username']
    # Для быстрого редактирования в списке представления
    column_editable_list = ['username']

class PostView(ModelView):
    pass

class AnalyticsView(BaseView):
    @expose('/')
    def analitics(self):
        return self.render('admin/analytics.html')

admin.add_view(UserView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(AnalyticsView(name='Analytics'))
