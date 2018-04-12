from app import ma
from flask_marshmallow import ValidationError, pre_load


# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class CustomerSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'customer_name', 'address1', 'city', 'state', 'postal_code', 'customer_number')
        _links = ma.Hyperlinks({
            'self': ma.URLFor('customer_detail', id='<id>'),
            'collection': ma.URLFor('customers')
        })


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


