from flask_restx import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required
from flask import abort, url_for
from app.api import rest_api
from app.models import User

ns = rest_api.namespace('User', description='Operation with user', path='/api/user')

# def get_user_links(user_id):
#     return ns.model('User links',{
# 'self': fields.String(attribute=lambda x: url_for('rest_api.User_user_api', user_id=user_id))
# })

# user_links = ns.model('User links',{
# 'self': fields.String(attribute=lambda x: url_for('rest_api.User_user_api', user_id=x.id))
# })

class UserLinks(fields.Raw):
    def format(self, value):
        return {
            'self': url_for('rest_api.User_user_api', user_id=value.id),
            }

user_fields = {
'id': fields.Integer(),
'username': fields.String(),
'email': fields.String(),
'about_me': fields.String(),
'last_seen': fields.DateTime(),
'post_count': fields.Integer(attribute=lambda x: x.posts.count()),
'followers_count': fields.Integer(attribute=lambda x: x.followers.count()),
'followed_count': fields.Integer(attribute=lambda x: x.followed.count()),
'links': UserLinks(attribute=lambda x:x)
}

@ns.route('/<int:user_id>')
class UserAPI(Resource):
    @marshal_with(user_fields)
    @jwt_required()
    def get(self, user_id):
        # print(url_for('main.profile', username='Nik'))
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404)
        return user, 200
