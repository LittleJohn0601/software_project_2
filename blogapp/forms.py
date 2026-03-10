import datetime
from typing import Optional
from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import DateTimeField, IntegerField, StringField, PasswordField, SelectField, SubmitField, FloatField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, Length, Regexp,NumberRange
from blogapp.models import User
import re


    
class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField('Username', validators=[
        DataRequired(message='Username cannot be empty'),
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password cannot be empty')
    ])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[
        DataRequired(message='Username cannot be empty'),
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email cannot be empty'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password cannot be empty'),
    ])
    user_type = SelectField('User Type', choices=[
        ('student', 'Student'), 
        ('teacher', 'Teacher'),
        ('admin', 'Admin')
    ], validators=[DataRequired(message='Please select user type')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("email already registered")
        
class LogActivityForm(FlaskForm):
    activity_type = SelectField('Activity Type', choices=[
        ('cycling', '🚴 Cycling'),
        ('recycling', '♻️ Recycling'), 
        ('energy_saving', '💡 Energy Saving'),
        ('public_transport', '🚆 Public Transport'),
        ('vegetarian_meal', '🥗 Vegetarian Meal'),
        ('planting', '🌳 tree planting')
    ], validators=[DataRequired(message='Please select an activity type')])
    
    carbon_saved = FloatField('Carbon Saved (kg CO₂)', validators=[
        DataRequired(message='Carbon savings amount is required'),
        NumberRange(min=0.1, max=1000, message='Carbon savings must be between 0.1 and 1000 kg')
    ])
    
    notes = TextAreaField('Notes', validators=[
        DataRequired(message='Notes cannot be empty'),
        Length(max=500, message='Notes cannot exceed 500 characters')
    ])
    
    submit = SubmitField('Log Activity')
    
    def validate_carbon_saved(self, field):
        """Reasonableness Verification Based on Activity Type"""
        activity_type = self.activity_type.data
        carbon_saved = field.data
        
        # Reasonable Carbon Saving Scope (Based on Activity Type)
        reasonable_ranges = {
            'cycling': (0.5, 5.0),
            'recycling': (0.1, 3.0),
            'energy_saving': (0.5, 10.0),
            'public_transport': (1.0, 8.0),
            'vegetarian_meal': (0.5, 2.5),
            'planting': (0.4,2.8)
        }
        
        if activity_type in reasonable_ranges:
            min_val, max_val = reasonable_ranges[activity_type]
            if carbon_saved < min_val or carbon_saved > max_val:
                raise ValidationError(
                    f'For {activity_type.replace("_", " ")}, typical carbon savings are between {min_val} and {max_val} kg'
                )

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[
        DataRequired(message="Event title is required"),
        Length(min=5, max=100, message="Title must be between 5 and 100 characters")
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message="Event description is required"),
        Length(min=10, max=500, message="Description must be between 10 and 500 characters")
    ])
    
    event_type = SelectField('Event Type', choices=[
        ('cycling_challenge', 'Cycling Challenge'),
        ('recycling_cleanup', 'Recycling & Cleanup'),
        ('energy_workshop', 'Energy Saving Workshop'),
        ('transport_challenge', 'Public Transport Challenge'),
        ('vegetarian_challenge', 'Vegetarian Meal Challenge'),
        ('sustainability_seminar', 'Sustainability Seminar'),
        ('tree_planting', 'Tree Planting'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    location = StringField('Location', validators=[
        DataRequired(message="Event location is required"),
        Length(min=3, max=100, message="Location must be between 3 and 100 characters")
    ])
    
    start_date = StringField('Start Date & Time', validators=[
        DataRequired(message="Start date is required"),
        Regexp(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', message="Please use format: YYYY-MM-DD HH:MM (e.g., 2025-03-15 19:38)")
    ])
    
    end_date = StringField('End Date & Time', validators=[
        DataRequired(message="End date is required"),
        Regexp(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', message="Please use format: YYYY-MM-DD HH:MM (e.g., 2025-03-15 19:38)")
    ])
    
    max_participants = IntegerField('Maximum Participants', validators=[        
        NumberRange(min=1, max=1000, message="Participants must be between 1 and 1000")
    ])
    
    def validate_start_date(self, field):
        """Verify start date"""
        if field.data:
            try:
                start = datetime.datetime.strptime(field.data, '%Y-%m-%d %H:%M')
                if start < datetime.datetime.now():
                    raise ValidationError("Event cannot start in the past")
                self.start_date_parsed = start
            except ValueError:
                raise ValidationError("Invalid date format. Please use: YYYY-MM-DD HH:MM")
    
    def validate_end_date(self, field):
        """Verify end date"""
        if field.data:
            try:
                end = datetime.datetime.strptime(field.data, '%Y-%m-%d %H:%M')
                
                # endure start_date is analyzed
                if not hasattr(self, 'start_date_parsed'):
                    # if not, analyze firstly
                    try:
                        self.start_date_parsed = datetime.datetime.strptime(self.start_date.data, '%Y-%m-%d %H:%M')
                    except ValueError:
                        raise ValidationError("Please fix the start date first")
                
                if end <= self.start_date_parsed:
                    raise ValidationError("End date must be after start date")
                
                # validate the remaining time
                duration = (end - self.start_date_parsed).days
                if duration > 3000:
                    raise ValidationError("Event cannot last longer than 3000 days")
                    
                # save the analyzed date to an entity
                self.end_date_parsed = end
            except ValueError:
                raise ValidationError("Invalid date format. Please use: YYYY-MM-DD HH:MM")
            
    def validate(self, extra_validators=None):
        """override validate to ensure the date is analyzed"""
        # use father's validate firstly
        if not super().validate(extra_validators=extra_validators):
            return False
        
        # ensure it is analyzed correctly
        try:
            if not hasattr(self, 'start_date_parsed'):
                self.start_date_parsed = datetime.datetime.strptime(self.start_date.data, '%Y-%m-%d %H:%M')
            
            if not hasattr(self, 'end_date_parsed'):
                self.end_date_parsed = datetime.datetime.strptime(self.end_date.data, '%Y-%m-%d %H:%M')
                
        except ValueError:
            # if the date's format is wrong, catch it
            return False
        
        return True
        
       