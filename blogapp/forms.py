# blogapp/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, FloatField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, ValidationError, NumberRange, Regexp
from blogapp.models import User
from blogapp.utils.encryption import DecryptionError
from blogapp.utils.sensitive_word_filter import validate_text


class SensitiveWordValidator:
    
    def __init__(self, field_name=None):
        self.field_name = field_name
    
    def __call__(self, form, field):
        if not field.data:
            return
        
        field_name = self.field_name or field.label.text or 'content'
        is_valid, error_msg = validate_text(field.data, field_name)
        
        if not is_valid:
            raise ValidationError(error_msg)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=32, message='Username must be between 3 and 32 characters'),
        Regexp(r'^[A-Za-z0-9_-]+$', message='Username can only contain letters, numbers, underscores, and hyphens'),
        SensitiveWordValidator(field_name='Username')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email cannot exceed 120 characters'),
        SensitiveWordValidator(field_name='Email')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, max=128, message='Password must be between 6 and 128 characters'),
        SensitiveWordValidator(field_name='Password')
    ])
    company_name = StringField('Company Name', validators=[
        Length(max=100, message='Company name cannot exceed 100 characters'),
        SensitiveWordValidator(field_name='Company name')
    ])
    user_type = SelectField('User Type', choices=[
        ('user', 'User'), 
        ('admin', 'Admin')
    ], validators=[DataRequired(message='Please select user type')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Check if username already exists (username is encrypted, need to check all users)"""
        for user in User.query.all():
            try:
                if user.username == username.data:
                    raise ValidationError('Username already exists')
            except DecryptionError:
                # 该用户数据解密失败（密钥不匹配/脏数据），跳过比对
                continue
    
    def validate_email(self, email):
        """Check if email already exists (email is encrypted, need to check all users)"""
        for user in User.query.all():
            try:
                if user.email == email.data:
                    raise ValidationError('Email already registered')
            except DecryptionError:
                continue


# TODO: Add your PeakShift forms here
# Example forms for your industrial energy system:

# class FactoryForm(FlaskForm):
#     """Factory information form"""
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
#     """Power source configuration form"""
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
#     """Electricity usage record form"""
#     date = DateField('Date', validators=[DataRequired()])
#     usage_kwh = FloatField('Usage (kWh)', validators=[
#         DataRequired(),
#         NumberRange(min=0)
#     ])
#     submit = SubmitField('Log Usage')
