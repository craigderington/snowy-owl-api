from wtforms import Form, BooleanField, StringField, PasswordField, validators


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = StringField('Email Address', [validators.Length(min=6, max=35)])
