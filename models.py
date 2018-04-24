from sqlalchemy import Column, Integer, Numeric, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'auth_user'
    id = Column(Integer, primary_key=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime, nullable=False)
    is_superuser = Column(Boolean(), default=0)
    username = Column(String(100), nullable=False, unique=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(String(75), unique=True, nullable=False)
    is_staff = Column(Boolean())
    is_active = Column(Boolean())
    date_joined = Column(DateTime, onupdate=datetime.now)

    def __init__(self, username=None, password=None, email=None):
        self.username = username
        self.set_password(password)
        self.email = email

    def __repr__(self):
        return 'User {}'.format(self.username)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return int(self.id)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)


class Dealer(db.Model):
    __tablename__ = 'frontend_dealer'
    id = Column(Integer, primary_key=True)
    # account_id = Column(Integer, ForeignKey('auth_user.id'), nullable=True)
    dealer_name = Column(String(255), nullable=False)
    address1 = Column(String(255), nullable=False)
    address2 = Column(String(50), nullable=True)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    postal_code = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(255), nullable=True)
    latitude = Column(Float())
    longitude = Column(Float())
    timezone = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    start_of_billing_cycle = Column(Integer, nullable=False)
    website_url = Column(String(255), nullable=True)
    invoice_notes = Column(Text(), nullable=True)
    API = Column(Boolean())
    API_link = Column(String(255))
    API_method = Column(String(255))
    API_extra_params = Column(Text())
    registration_invite_text = Column(Text())
    logo_image = Column(String(255))
    color_navbar_top = Column(String(32))
    color_navbar_bottom = Column(String(32))

    def __repr__(self):
        return '{}'.format(
            self.dealer_name
        )


class DealerAccount(db.Model):
    __tablename__ = 'frontend_dealer_account'
    id = Column(Integer, primary_key=True)
    dealer_id = Column(ForeignKey('frontend_dealer.id'), nullable=False)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False)

    def __repr__(self):
        if self.id:
            return '{} {}'.format(
                self.dealer_id, self.user_id
            )


class Customer(db.Model):
    __tablename__ = 'frontend_customer'
    id = Column(Integer, primary_key=True)
    dealer_id = Column(ForeignKey('frontend_dealer.id'), nullable=False)
    account_id = Column(ForeignKey('auth_user.id'), nullable=True)
    customer_name = Column(String(255), nullable=False)
    customer_number = Column(String(255), nullable=True)
    address1 = Column(String(255), nullable=False)
    address2 = Column(String(255), nullable=True)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    postal_code = Column(String(255), nullable=False)
    country = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    latitude = Column(Float(), nullable=True)
    longitude = Column(Float(), nullable=True)
    active = Column(Boolean())

    def __repr__(self):
        return '{}'.format(
            self.customer_name
        )


class ServiceAddress(db.Model):
    __tablename__ = 'frontend_serviceaddress'
    id = Column(Integer, primary_key=True)
    customer_id = Column(ForeignKey('frontend_customer.id'), nullable=False)
    customer = relationship('Customer')
    service_address_account_number = Column(String(255), nullable=False)
    address1 = Column(String(255), nullable=False)
    address2 = Column(String(255), nullable=True)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    postal_code = Column(String(255), nullable=False)
    country = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    latitude = Column(Float(), nullable=True)
    longitude = Column(Float(), nullable=True)
    notes = Column(Text())
    routing_zone = Column(String(255), nullable=True)
    product_rate = Column(Numeric(precision=8, scale=5), nullable=True)
    tax_rate = Column(Numeric(precision=8, scale=5), nullable=True)
    management_rate = Column(Numeric(precision=8, scale=5), nullable=True)
    current_balance = Column(Float(), nullable=True)
    short_code = Column(String(255), unique=True, nullable=True)
    coordinates_locked = Column(Boolean(), nullable=True)
    new_tax_rate_id = Column(Integer())
    new_product_rate_id = Column(Integer())
    new_mgt_rate_id = Column(Integer())

    def __repr__(self):
        if self.id:
            return '{} {} {} {} {} {}'.format(
                self.customer,
                self.address1,
                self.address2,
                self.city,
                self.state,
                self.postal_code
            )


class Tank(db.Model):
    __tablename__ = 'frontend_tank'
    service_address_id = Column(Integer, ForeignKey('frontend_serviceaddress.id'), nullable=False)
    service_address = relationship('ServiceAddress')
    capacity = Column(Integer, nullable=True)
    notes = Column(Text())
    usage_billing = Column(Boolean, default=False)
    tank_type = Column(String(255), nullable=True)
    tank_manufacturer = Column(String(255), nullable=True)
    serial_number = Column(String(255), nullable=True)
    manufacture_date = Column(DateTime(), nullable=True)
    install_date = Column(DateTime, nullable=True)
    last_inspection_date = Column(DateTime, nullable=True)
    next_inspection_date = Column(DateTime, nullable=True)
    network_id = Column(String(255), nullable=True)
    receiver_time = Column(DateTime, nullable=True)
    sensor_value = Column(Float(), nullable=True)
    days_to_empty = Column(Integer, nullable=True)

    def __repr__(self):
        if self.id:
            return '{} {}'.format(
                self.service_address,
                self.capacity
            )


class Meter(db.Model):
    __tablename__ = 'frontend_meter'
    service_address_id = Column(Integer, ForeignKey('frontend_serviceaddress.id'), nullable=False)
    service_address = relationship('ServiceAddress')
    meter_current_read = Column(String(255), nullable=True)
    meter_model = Column(String(255), nullable=True)
    meter_multiplier = Column(Integer, nullable=False)
    meter_pulse_per_rev = Column(Integer, nullable=False)
    meter_date_installed = Column(DateTime, nullable=True)
    meter_serial_number = Column(String(255), nullable=True)
    network_id = Column(String(255), nullable=True)
    receiver_time = Column(DateTime, nullable=True)
    sensor_value = Column(Float(), nullable=True)
    meter_notes = Column(Text(), nullable=True)

    def __repr__(self):
        if self.id:
            return '{} {}'.format(
                self.service_address,
                self.meter_current_read
            )
