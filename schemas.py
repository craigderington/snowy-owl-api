from marshmallow_sqlalchemy import ModelSchema


class CustomerSchema(ModelSchema):

    def make_customer(self, data):
        return Customer(**data)

    class Meta:
        fields = ('id', 'customer_name', 'address1', 'city', 'state', 'postal_code', 'customer_number')


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


class ServiceAddressSchema(ModelSchema):

    def make_service_address(self, data):
        return ServiceAddress(**data)

    class Meta:
        fields = ('id', 'customer_id', 'service_address_account_number')


serviceaddress_schema = ServiceAddressSchema()
serviceaddresses_schema = ServiceAddressSchema(many=True)
