#! .env/bin/python
# coding: utf-8

import random
from datetime import datetime
from datetime import timedelta
import hashlib
import time
import config
import redis
from flask import Flask, make_response, redirect, request, Response, render_template, url_for, flash, g, jsonify
from flask_marshmallow import Marshmallow, ValidationError
from flask_swagger import swagger
from flask_mail import Mail, Message
from flask_sslify import SSLify
from flask_session import Session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy, Pagination
from flask_sqlalchemy import text, and_, exc, func
from celery import Celery
from models import User, Dealer, Customer
from schemas import CustomerSchema

# debug
debug = False

# app config
app = Flask(__name__)
sslify = SSLify(app)
app.secret_key = config.SECRET_KEY

# session persistence
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('127.0.0.1:6379')
app.config['SESSION_PERMANENT'] = True
sess = Session()
sess.init_app(app)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER

# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)

# define our login_manager
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "/auth/login"
login_manager.login_message = "Login required to access this API."
login_manager.login_message_category = "primary"

# disable strict slashes
app.url_map.strict_slashes = False

# Celery config
app.config['CELERY_BROKER_URL'] = config.CELERY_BROKER_URL
app.config['CELERY_RESULT_BACKEND'] = config.CELERY_RESULT_BACKEND
app.config['CELERY_ACCEPT_CONTENT'] = config.CELERY_ACCEPT_CONTENT
app.config.update(accept_content=['json', 'pickle'])

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Config mail
mail = Mail(app)

# set app vars
app = Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

# database
db = SQLAlchemy(app)

# marshall fields with marshmallow
ma = Marshmallow(app)

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


# load the user
@login_manager.user_loader
def load_user(id):
    try:
        return db.session.query(User).get(int(id))
    except exc.SQLAlchemyError as db_err:
        return None


# run before each request
@app.before_request
def before_request():
    g.user = current_user


# tasks sections, for async functions, etc...
@celery.task(serializer='pickle')
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    with app.app_context():
        mail.send(msg)


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


# default routes
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    """
    OWL API Routes: Full List
    :return: list
    """
    endpoints = {
        '/': 'api/v1.0/index',
        'customers': '/api/v1.0/customers',
        'customer/<id>': '/api/v1.0/customer/<id>',
        'service-addresses': '/api/v1.0/service-addresses',
        'service-address/<id>': '/api/v1.0/service-address/<id>',
        'tanks': '/api/v1.0/tanks',
        'tank/<id>': '/api/v1.0/tank/<id>',
        'tank/<id>/history': '/api/v1.0/tank/<id>/history',
        'tank/<id>/history/<limit>': '/api/v1.0/tank/<id>/history/<limit>',
        'tank/<id>/provision/<radio-id>': '/api/v1.0/tank/<id>/provision/<radio-id>',
        'tank/<id>/deprovision/<radio-id>': '/api/v1.0/tank/<id>/deprovision/<radio-id>',
        'meters': '/api/v1.0/meters',
        'meter/<id>': '/api/v1.0/meter/<id>',
        'radios': '/api/v1.0/radios',
        'radio/<id>': '/api/v1.0/radio/<id>',
        'radio/lookup/<id>': '/api/v1.0/radio/lookup/<id>',
    }

    resp = jsonify(endpoints)
    resp.status_code = 200
    return resp


@app.route('/customers', methods=['GET', 'POST'])
def get_customers():
    """
    The Customer List/Create API Endpoint
    GET: List all customers
    POST: Create a new customer
    :return: list or pk
    """

    id = get_dealer(current_user.id)

    if request.method == 'GET':
        
        customers = db.session.query(Customer).filter(
            Customer.dealer_id == id
        ).all()

        if customers:
            resp = jsonify(customers)
            resp.status_code = 200
            return resp
    
    elif request.method == 'POST':
        data = request.get_json()

        try:
            customer = CustomerSchema.load(data)

            new_customer = Customer(customer)
            db.session.add(new_customer)
            db.session.commit()

            return CustomerSchema.jsonify(customer)

        except ValidationError as err:
            return err.messages


@app.route('/customer/<int:customer_pk_id>', methods=['GET', 'PUT'])
def get_customer(customer_pk_id):
    """
    The Customer API Endpoint
    GET: Customer instance by ID
    PUT: Update Customer Instance
    :return: customer_pk
    """
    id = get_dealer(current_user.id)

    if request.method == 'GET':
        pass
    elif request.method == 'PUT':
        pass


@app.route('/service-addresses', methods=['GET', 'POST'])
def service_addresses():
    """
    The Service Address List/Create API Endpoint
    GET: List all Service Addresses
    :return: list or pk
    """
    pass


@app.route('/service-address/<int:serviceaddress_pk_id>', methods=['GET', 'PUT'])
def service_addresses(serviceaddress_pk_id):
    """
    The Service Address API Endpoint
    GET: Service Addresses Instance by ID
    :return: list or pk
    """
    pass


@app.route('/tanks', methods=['GET', 'POST'])
def tanks():
    """
    The Tank List or Create API Endpoint
    :return: list or pk
    """
    pass


@app.route('/tank/<int:tank_pk_id>', methods=['GET', 'PUT'])
def tank(tank_pk_id):
    """
    The Tank List or Create API Endpoint
    GET:  Tank instance by ID
    :return: tank or pk
    """
    pass


@app.route('/tank/<int:tank_pk_id>/history')
def tank_history(tank_pk_id):
    """
    Tank Data History API Endpoint by Tank ID
    :param tank_pk_id:
    :return:
    """
    pass


@app.route('/tank/<int:tank_pk_id>/history/<int:num_records>')
def tank_history(tank_pk_id, num_records):
    """
    Tank Data History API Endpoint by Tank ID and
    Number of Records to Return in the Response
    :param tank_pk_id:
    :return:
    """
    pass


@app.route('/radios', methods=['GET'])
def radios():
    """
    The Radio List API Endpoint
    :return: list
    """
    pass


@app.route('/radio/<int:radio_pk_id>', methods=['GET', 'PUT'])
def radio(radio_pk_id):
    """
    The Radio List API Endpoint
    GET: Radio instance by ID
    PUT: Partial Update on API exposed fields
    :return: list
    """
    pass


@app.route('/radio/lookup/<int:dealer_radio_id>', methods=['GET'])
def radio_lookup():
    """
    The Radio Lookup by Dealer Radio ID API Endpoint
    :return: radio
    """
    pass


@app.route('/meters', methods=['GET', 'POST'])
def meters():
    """
    The Meter List or Create API Endpoint
    :return: list or pk
    """
    pass


@app.route('/meter/<int:meter_pk_id>', methods=['GET', 'PUT'])
def meter():
    """
    The Meter API Endpoint
    GET: meter instance
    PUT: Update meter instance
    :return: meter or pk
    """
    pass


@app.route('/tank/<int:tank_pk_id>/provision/<int:radio_pk_id>', methods=['POST'])
def provision_radio(tank_pk_id, radio_pk_id):
    """
    The Provison Radio API Endpoint
    :param tank_pk_id:
    :param radio_pk_id:
    :return: response
    """
    pass


@app.route('/tank/<int:tank_pk_id>/deprovision/<int:radio_pk_id>', methods=['POST'])
def deprovision_radio(tank_pk_id, radio_pk_id):
    """
    The deprovison Radio API Endpoint
    :param tank_pk_id:
    :param radio_pk_id:
    :return: response
    """
    pass


def get_dealer(id):
    """
    Get the Dealer ID for the Current User
    :param id:
    :return: dealer_id
    """

    try:
        dealer = db.session.query(Dealer).filter(
            Dealer.account_id == id
        ).one()

        dealer_id = dealer.id

    except exc.SQLAlchemyError:
        raise

    return dealer_id




@app.route('/login', methods=['GET'])
def login_redirect():
    """
    Redirect to auth/login
    :return: redirect url
    """
    return redirect(url_for('login'), 302)


@app.route("/auth/login", methods=['GET', 'POST'])
def login():

    form = UserLoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            user = db.session.query(User).filter_by(username=username).first()

            if user is None or not user.check_password(password):
                flash('Username or password is invalid!  Please try again...')
                return redirect(url_for('login'))

            # login the user and redirect
            login_user(user)
            flash('You have been logged in successfully...', 'success')
            return redirect(request.args.get('next') or url_for('index'))

        except exc.SQLAlchemyError as db_err:
            flash('Database returned error {}'.format(str(db_err)))
            return redirect(url_for('login'))

    return render_template(
        'login.html',
        form=form
    )


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(err):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(err):
    return render_template('500.html'), 500


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def send_email(to, subject, msg_body, **kwargs):
    """
    Send Mail function
    :param to:
    :param subject:
    :param template:
    :param kwargs:
    :return: celery async task id
    """
    msg = Message(
        subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to, ]
    )
    msg.body = 'message'
    msg.html = msg_body
    send_async_email.delay(msg)


if __name__ == '__main__':
    app.run(debug=True, port=5880)
