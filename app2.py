from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api, reqparse, fields, marshal, marshal_with
from flask_httpauth import HTTPBaiscAuth
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import exc
from flask_marshmallow import Marshmallow
from flask_swagger import swagger
from models import User, Dealer, Customer
from schemas import CustomerSchema
import config

# set app vars
app = Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

# api
api = Api(app)

# database
db = SQLAlchemy(app)

# marshall fields with marshmallow
ma = Marshmallow(app)

# auth
auth = HTTPBaiscAuth()

# errors
errors = {
    'ObjectDoesNotExistError': {
        'message': "The selected object was not found.",
        'status': 404,
    },
    'ResourceDoesNotExist': {
        'message': "A resource with that ID no longer exists.",
        'status': 410,
        'extra': "Any extra information you want.",
    },
}


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@auth.error_handler
def unauthorized():
    """
    Return a 403 instead of 401 to prevent browsers
    from displaying the authentication dialog
    :return: response
    """
    msg = {'code': 403, 'message': 'Unauthorized access'}
    return make_response(jsonify(msg), 403)


@app.route('/api/docs')
def apidocs():
    swag = swagger(app)
    swag['info']['version'] = '1.0'
    swag['info']['title'] = 'OWL Network API'
    return jsonify(swag)


class CustomerListAPI(Resource):

    # auth
    decorators = [auth.login_required]

    def get(self):
        """
        Generate a list of customers for the logged in user
        swagger_from_file: path/to/file.yml
        :return: list
        """
        try:
            customers = db.session.query(Customer).filter(dealer_id=1).all()

            if customers:
                result = CustomerSchema.dump(customers)
                return jsonify(result.data)

        except exc.SQLAlchemy as err:
            msg = {'code': 404, 'message': 'No customers found for the logged in user.'}
            return jsonify(msg)

    def post(self):
        """
        Create a new customer for the logged in user
        swagger_from_file: path/to/file.yml
        :return:
        """
        pass


class CustomerAPI(Resource):

    # auth
    decorators = [auth.login_required]

    def get(self, customer_pk_id):
        """
        Get the customer instance by ID
        swagger_from_file: path/to/file.yml
        :param customer_pk_id:
        :return: API response (customer)
        """
        try:
            customer = db.session.query(Customer).filter(
                Customer.id == customer_pk_id
            ).one()

            if customer:
                result = CustomerSchema.dump(customer)
                return jsonify(result.data)

        except exc.SQLAlchemy as err:
            msg = {'code': 404, 'message': 'No customer found matching input.'}
            return jsonify(msg)

    def put(self, customer_pk_id):
        """
        Partial update of the customer instance by ID
        :param customer_pk_id:
        :return: API response (customer)
        """
        pass


# resource endpoints

api.add_resource(CustomerListAPI, '/api/v1.0/customers', endpoint='customers')
api.add_resource(CustomerAPI, '/api/v1.0/customer/<int:customer_pk_id>', endpoint='customer')


if __name__ == '__main__':
    app.run(debug=True, port=5880)
