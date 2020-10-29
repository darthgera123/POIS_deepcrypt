from wtforms import Form, StringField, IntegerField, validators

class DataForm(Form):
    number = IntegerField('Number')