from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields

blp = Blueprint('test', __name__, description='Operations on test')

@blp.route('/test')
class Test(MethodView):
    def get(self):
        return {'hello': 'world'}