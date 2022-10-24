from flask_restx import Resource, fields, marshal_with
from flask_jwt_extended import create_access_token
from app.api import rest_api
from app.api.parsers import auth_post_parser
from app.models import User

ns = rest_api.namespace('Auth', description='Operations with auth-token', path='/api/auth')

# auth_fields = ns.model('Model',{
# 'username': fields.String(),
# 'password': fields.String(),
# })

@ns.route('/')
class AuthApi(Resource):

    def authenticate(self, username, password):
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return None
        return user
    
    @ns.expect(auth_post_parser)
    def post(self):
        args = auth_post_parser.parse_args()
        user = self.authenticate(args['username'], args['password'])
        if not user:
            return {"msg": "Bad username or password"}, 401
        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token}, 200
