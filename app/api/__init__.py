# from flask_restful import Api
from flask_restx import Api
from flask import Blueprint, json
# from app.api.routes import rest_api as rest_api_post

bp = Blueprint('rest_api', __name__)
rest_api = Api(
    bp,
    title='My Title',
    version='1.0',
    description='A description',
    doc='/api/doc/',
    security='bearerAuth',
    authorizations={
        'bearerAuth':{
            'type':'apiKey',
            'in':'header',
            'name':'Authorization',
            'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"}
            })

# rest_api.add_namespace(rest_api_post)



from app.api import post, parsers, auth, user


