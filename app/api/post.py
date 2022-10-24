from flask_restx import Resource, fields, marshal_with, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import abort, current_app
from app import db
from app.api import rest_api
from app.models import Post
from app.api.parsers import post_get_parser, post_post_parser, post_put_parser

ns = rest_api.namespace('Posts', description='Operation with posts', path='/api/post')
post_fields = {
'id': fields.Integer(),
'body': fields.String(),
'timestamp': fields.DateTime(),
'author': fields.String(attribute=lambda x: x.author.username),
}

@ns.route('/')
class PostListApi(Resource):
    @ns.expect(post_get_parser)
    @marshal_with(post_fields)
    @jwt_required()
    def get(self):
        args = post_get_parser.parse_args()
        page = args['page'] or 1
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'])
        return posts.items, 200

    @ns.expect(post_post_parser)
    @jwt_required()
    def post(self):
        args = post_post_parser.parse_args()
        new_post = Post(body=args['body'])
        new_post.user_id = get_jwt_identity()
        db.session.add(new_post)
        db.session.commit()
        return {'id': new_post.id}, 201



@ns.route('/<int:post_id>')
class PostApi(Resource):
    @marshal_with(post_fields)
    @jwt_required()
    def get(self, post_id):
        post = Post.query.filter_by(id=post_id).first()
        if not post:
            abort(404)
        return post, 200

    @ns.expect(post_put_parser)    
    @jwt_required()
    def put(self, post_id=None):
        if not post_id:
            abort(404)
        post = Post.query.filter_by(id=post_id).first()
        if not post:
            abort(404)
        if get_jwt_identity() != post.user_id:
            abort(401)
        args = post_put_parser.parse_args()
        if args['body']:
            post.body = args['body']
        db.session.merge(post)
        db.session.commit()
        return {'id': post.id}, 201

    @jwt_required()
    def delete(self, post_id=None):
        if not post_id:
            abort(404)
        post = Post.query.filter_by(id=post_id).first()
        if not post:
            abort(404)
        if get_jwt_identity() != post.user_id:
            abort(401)
        db.session.delete(post)
        db.session.commit()
        return {'status': 'succes'}, 204