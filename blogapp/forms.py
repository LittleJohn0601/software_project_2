# blogapp/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, FloatField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, ValidationError, NumberRange
from blogapp.models import User


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=64, message='Username must be between 3 and 64 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    company_name = StringField('Company Name', validators=[
        Length(max=100, message='Company name cannot exceed 100 characters')
    ])
    user_type = SelectField('User Type', choices=[
        ('user', 'User'), 
        ('admin', 'Admin')
    ], validators=[DataRequired(message='Please select user type')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered')


# TODO: Add your PeakShift forms here
# Example forms for your industrial energy system:

# class FactoryForm(FlaskForm):
#     """工厂信息表单"""
#     name = StringField('Factory Name', validators=[DataRequired()])
#     location = StringField('Location')
#     industry_type = SelectField('Industry Type', choices=[
#         ('aluminum', 'Aluminum Smelting'),
#         ('steel', 'Steel Manufacturing'),
#         ('chemical', 'Chemical Industry'),
#         ('other', 'Other')
#     ])
#     submit = SubmitField('Save')

# class PowerSourceForm(FlaskForm):
#     """电力来源配置表单"""
#     source_type = SelectField('Power Source', choices=[
#         ('coal', 'Coal Power'),
#         ('wind', 'Wind Power'),
#         ('solar', 'Solar Power'),
#         ('hydro', 'Hydro Power')
#     ])
#     percentage = FloatField('Percentage (%)', validators=[
#         NumberRange(min=0, max=100)
#     ])
#     submit = SubmitField('Add Source')

# class ElectricityUsageForm(FlaskForm):
#     """用电记录表单"""
#     date = DateField('Date', validators=[DataRequired()])
#     usage_kwh = FloatField('Usage (kWh)', validators=[
#         DataRequired(),
#         NumberRange(min=0)
#     ])
#     submit = SubmitField('Log Usage')
