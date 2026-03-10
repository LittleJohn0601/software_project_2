# blogapp/models.py
import re
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from blogapp import db
from datetime import datetime, timezone, timedelta

# Add missing import for current_app (to fix undefined reference)
from flask import current_app

class User(UserMixin, db.Model):
    """User model with encrypted email"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    _email_encrypted = db.Column(db.String(500), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20), default='student')
    ban_reason = db.Column(db.String(255), nullable=True)
    ban_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # ========== Email validation methods (static methods) ==========
    @staticmethod
    def validate_email_format(email):
        """Validate email format"""
        print(f"🔍 Validating email: {email}")
        
        if not email or not isinstance(email, str):
            print("❌ Email is empty or not a string")
            return False
        
        email = email.strip().lower()
        
        # Basic format check
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            print(f"❌ Basic pattern mismatch for: {email}")
            return False
        
        # Length check
        if len(email) > 254:
            print(f"❌ Email too long: {len(email)} characters")
            return False
        
        # Check for @ symbol
        if '@' not in email:
            print("❌ No @ symbol")
            return False
        
        try:
            local_part, domain_part = email.split('@')
        except ValueError:
            print("❌ Invalid email structure")
            return False
        
        # Local part checks
        if len(local_part) > 64:
            print(f"❌ Local part too long: {len(local_part)} characters")
            return False
        
        # Prohibit certain special character combinations
        if '..' in local_part:  # Consecutive dots
            print("❌ Consecutive dots in local part")
            return False
        
        if local_part.startswith('.') or local_part.endswith('.'):
            print("❌ Local part starts or ends with dot")
            return False
        
        # Domain part checks
        if domain_part.startswith('-') or domain_part.endswith('-'):
            print("❌ Domain starts or ends with hyphen")
            return False
        
        # Domain part must have at least one dot
        if '.' not in domain_part:
            print("❌ No dot in domain part")
            return False
        
        # TLD check
        tld = domain_part.split('.')[-1]
        if len(tld) < 2:
            print(f"❌ TLD too short: {tld}")
            return False
        
        print(f"✅ Email validation passed for: {email}")
        return True
    
    @classmethod
    def is_email_available(cls, email, exclude_user_id=None):
        """Check if email is available"""
        print(f"🔍 Checking if email is available: {email}")
        
        if not email:
            print("❌ Email is empty")
            return False
        
        # Validate format
        if not cls.validate_email_format(email):
            print("❌ Email format validation failed")
            return False
        
        # Check if already exists
        # Note: Special handling needed because email is stored encrypted
        # We need to query all users and decrypt for comparison one by one
        
        query = cls.query
        if exclude_user_id:
            query = query.filter(cls.id != exclude_user_id)
        
        users = query.all()
        for user in users:
            if user.email == email.strip().lower():
                print(f"❌ Email already used by user: {user.username}")
                return False
        
        print(f"✅ Email is available: {email}")
        return True
    
    @staticmethod
    def _encrypt_email_for_query(email):
        """Encrypt email for query purposes (simplified version)"""
        try:
            # Try to use real encryptor
            from blogapp.email_encryptor import email_encryptor
            return email_encryptor.encrypt_email(email.strip().lower())
        except Exception as e:
            print(f"⚠️ Using fallback email encryption: {e}")
            # Development environment fallback
            return f"[FALLBACK]{email.strip().lower()}"
    
    def __init__(self,** kwargs):
        """Initialize user, encrypt email"""
        # Extract email parameter
        email = kwargs.pop('email', None)
        
        # Call parent class constructor
        super().__init__(** kwargs)
        
        # Set encrypted email
        if email:
            self.email = email
    
    # ========== Helper methods ==========
    def _get_encryptor(self):
        """Lazy import encryptor to avoid circular dependencies"""
        try:
            from blogapp.email_encryptor import email_encryptor
            return email_encryptor
        except ImportError as e:
            # Log error but continue execution
            if current_app:
                current_app.logger.error(f"Failed to import email_encryptor: {e}")
            # Return a simple mock encryptor
            return self._create_fallback_encryptor()
    
    def _create_fallback_encryptor(self):
        """Create fallback simple encryptor"""
        class FallbackEncryptor:
            @staticmethod
            def encrypt_email(email):
                if current_app and current_app.config.get('ENV') == 'development':
                    return f"[FALLBACK]{email}"
                raise RuntimeError("Encryption service not available")
            
            @staticmethod
            def decrypt_email(encrypted):
                if encrypted.startswith("[FALLBACK]"):
                    return encrypted[10:]
                return "[ERROR]"
        
        return FallbackEncryptor()
    
    # ========== Encrypted email property ==========
    @property
    def email(self):
        """Get decrypted email"""
        if not self._email_encrypted:
            return None
        
        try:
            encryptor = self._get_encryptor()
            return encryptor.decrypt_email(self._email_encrypted)
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Failed to decrypt email for user {self.id}: {e}")
            
            # In development environment, might return unencrypted data
            if current_app and current_app.config.get('ENV') == 'development':
                if '@' in self._email_encrypted:
                    return self._email_encrypted
            
            return "[DECRYPTION_ERROR]"
    
    @email.setter
    def email(self, value):
        """Encrypt and set email"""
        print(f"🔐 Setting email for user {self.username if hasattr(self, 'username') else 'new'}: {value}")
        
        if value:
            # Validate email format
            if not User.validate_email_format(value):
                raise ValueError(f"Invalid email format: {value}")
            
            try:
                encryptor = self._get_encryptor()
                clean_email = value.strip().lower()
                self._email_encrypted = encryptor.encrypt_email(clean_email)
                print(f"✅ Email encrypted and set for user")
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Failed to encrypt email: {e}")
                
                # Development environment: store unencrypted version (with marker)
                if current_app and current_app.config.get('ENV') == 'development':
                    self._email_encrypted = f"[UNENCRYPTED]{value.strip().lower()}"
                    print(f"⚠️ Using unencrypted email in development")
                else:
                    raise
        else:
            self._email_encrypted = None
            print("⚠️ Email set to None")
    
    # ========== Other methods ==========
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_temporary_ban(self, duration_hours: int, reason: str | None = None):
        self.ban_reason = reason or "No reason provided"
        self.ban_until = datetime.now() + timedelta(hours=duration_hours)
    
    def clear_ban(self):
        self.ban_reason = None
        self.ban_until = None
    
    @property
    def is_staff(self):
        return self.user_type in ['teacher', 'admin']
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_banned(self):
        if self.ban_until is None:
            return False
        return datetime.now() < self.ban_until
    
    def __repr__(self):
        return f'<User {self.username}>'

class CarbonFootprintLog(db.Model):
    """Model for tracking carbon footprint reduction activities"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # Type of eco-friendly activity
    carbon_saved = db.Column(db.Float, nullable=False)        # Amount of carbon saved
    activity_date = db.Column(db.DateTime, nullable=False, default=datetime.now)    # Date of activity
    notes = db.Column(db.Text)                                # Additional notes

class SustainabilityEvent(db.Model):
    """Model for sustainability events"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer, nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy=True, cascade='all, delete-orphan')
    organizer = db.relationship('User', backref='created_events')
    
    @property
    def carbon_stats(self):
        """Dynamically calculate carbon savings statistics related to this event"""
        from sqlalchemy import func
        
        # Update mapping relationship
        activity_event_mapping = {
            'cycling': ['cycling_challenge'],
            'recycling': ['recycling_cleanup'],
            'energy_saving': ['energy_workshop'],
            'public_transport': ['transport_challenge'],
            'vegetarian_meal': ['vegetarian_challenge']
        }
        
        # Find activity types related to this event type
        related_activities = []
        for activity_type, event_types in activity_event_mapping.items():
            if self.event_type in event_types:
                related_activities.append(activity_type)
        
        if not related_activities:
            return {'total_carbon_saved': 0.0, 'activity_count': 0}
        
        # Calculate total carbon savings and count of related activities
        result = db.session.query(
            func.count(CarbonFootprintLog.id),
            func.sum(CarbonFootprintLog.carbon_saved)
        ).filter(
            CarbonFootprintLog.activity_type.in_(related_activities)
        ).first()
        
        activity_count, total_carbon = result
        return {
            'total_carbon_saved': total_carbon or 0.0,
            'activity_count': activity_count or 0
        }
    
    @property
    def current_participants(self):
        """Get current number of registered participants"""
        from blogapp.models import EventRegistration
        return EventRegistration.query.filter_by(event_id=self.id, status='registered').count()
    
    @property
    def is_full(self):
        """Check if event is full"""
        if self.max_participants is None:
            return False
        return self.current_participants >= self.max_participants
    
    @property
    def status(self):
        """Get event status based on dates"""
        now = datetime.now()
        if now < self.start_date:
            return 'upcoming'
        elif self.start_date <= now <= self.end_date:
            return 'ongoing'
        else:
            return 'completed'
    
    @property
    def display_date(self):
        """Formatted date for display"""
        if self.start_date.date() == self.end_date.date():
            return self.start_date.strftime('%b %d, %Y')
        else:
            return f"{self.start_date.strftime('%b %d')} - {self.end_date.strftime('%b %d, %Y')}"
    
    @property
    def time_range(self):
        """Formatted time range"""
        if self.start_date.date() == self.end_date.date():
            return f"{self.start_date.strftime('%I:%M %p')} - {self.end_date.strftime('%I:%M %p')}"
        else:
            return "Multiple days"

    @property
    def time_range(self):
        """Formatted time range"""
        if self.start_date.date() == self.end_date.date():
            return f"{self.start_date.strftime('%I:%M %p')} - {self.end_date.strftime('%I:%M %p')}"
        else:
            return "Multiple days"

    # 👍 New property added
    @property
    def carbon_target(self) -> float:
        """
        The expected total CO2e reduction (kg) from participants in this event.
        This is a simple mapping based on event_type and is not stored in the database.
        You can modify the values according to your event_type names.
        """
        mapping = {
            '996 day': 10.0,          # Example: 996 day target is 10kg
            'clean_up': 5.0,          # Campus cleanup
            'bike_week': 3.0,         # Bike to school week
            'veggie_week': 4.0,       # Vegetarian challenge week
            # ……You can add more mappings here……
        }
        return mapping.get(self.event_type, 10.0)  # Default target is 10kg

    def can_register(self, user):
        """Check if user can register for this event"""
        if not user or not user.is_authenticated:
            return False, "Please log in to register"
        
        if self.status != 'upcoming':
            return False, "Registration is closed for this event"
        
        if self.is_full:
            return False, "Event is full"
        
        # Check if user is already registered
        from blogapp.models import EventRegistration
        existing_registration = EventRegistration.query.filter_by(
            user_id=user.id, 
            event_id=self.id
        ).first()
        
        if existing_registration:
            if existing_registration.status == 'registered':
                return False, "Already registered"
            elif existing_registration.status == 'waitlisted':
                return False, "You are on the waitlist"
        
        return True, "Can register"

    # Add the following methods to the SustainabilityEvent class in models.py
    def get_participants_ranking(self, include_visitors=False):
        """
        Get ranking of all participants in this event (sorted by carbon savings)
        Returns: [{'rank': 1, 'user_id': 1, 'username': 'name', 'total_saved': 10.5, ...}, ...]
        """
        from sqlalchemy import func, desc
        from flask_login import current_user
    
        # Get all registered users for the event
        registrations = EventRegistration.query.filter_by(
            event_id=self.id, 
            status='registered'
        ).all()
    
        if not registrations and not include_visitors:
            return []
    
        # Get event-related activity types
        from blogapp.routes.main import ACTIVITY_EVENT_MAPPING
        related_activities = []
        for activity_type, event_types in ACTIVITY_EVENT_MAPPING.items():
            if self.event_type in event_types:
                related_activities.append(activity_type)
    
        # If no related activities, use the event type itself
        if not related_activities:
            related_activities = [self.event_type]

        # Calculate carbon savings for each participant
        participants_data = []
        now = datetime.now()
        end_cutoff = self.end_date if self.end_date < now else now
    
        # Process registered users
        registered_user_ids = []
        for registration in registrations:
            total_saved = db.session.query(
                func.coalesce(func.sum(CarbonFootprintLog.carbon_saved), 0.0)
            ).filter(
                CarbonFootprintLog.user_id == registration.user_id,
                CarbonFootprintLog.activity_type.in_(related_activities),
                CarbonFootprintLog.activity_date >= self.start_date,
                CarbonFootprintLog.activity_date <= end_cutoff
            ).scalar() or 0.0
        
            participants_data.append({
                'user_id': registration.user_id,
                'username': registration.user.username,
                'avatar': None,  # Add avatar functionality if needed
                'total_saved': total_saved,
                'activities_count': self._get_user_activity_count(
                    registration.user_id, 
                    related_activities, 
                    self.start_date, 
                    end_cutoff
                ),
                'registered_at': registration.registered_at,
                'is_current_user': registration.user_id == current_user.id if hasattr(current_user, 'id') else False,
                'is_unofficial': False
            })
            registered_user_ids.append(registration.user_id)
    
        if include_visitors:
            # Find all users who submitted related activities (even if not registered)
            activity_users = db.session.query(
                CarbonFootprintLog.user_id
            ).filter(
                CarbonFootprintLog.activity_type.in_(related_activities),
                CarbonFootprintLog.activity_date >= self.start_date,
                CarbonFootprintLog.activity_date <= end_cutoff
            ).distinct().all()
        
            for result in activity_users:
                user_id = result[0]
                if user_id not in registered_user_ids:
                    # Calculate data for this unregistered user
                    total_saved = db.session.query(
                        func.coalesce(func.sum(CarbonFootprintLog.carbon_saved), 0.0)
                    ).filter(
                        CarbonFootprintLog.user_id == user_id,
                        CarbonFootprintLog.activity_type.in_(related_activities),
                        CarbonFootprintLog.activity_date >= self.start_date,
                        CarbonFootprintLog.activity_date <= end_cutoff
                    ).scalar() or 0.0
                
                    user = User.query.get(user_id)
                    if user:
                        participants_data.append({
                            'user_id': user_id,
                            'username': f"{user.username} (Unofficial)",
                            'avatar': None,
                            'total_saved': total_saved,
                            'activities_count': self._get_user_activity_count(
                                user_id, related_activities, self.start_date, end_cutoff
                            ),
                            'registered_at': None,
                            'is_current_user': user_id == current_user.id if hasattr(current_user, 'id') else False,
                            'is_unofficial': True
                        })
    
        # Sort by carbon savings in descending order
        participants_data.sort(key=lambda x: x['total_saved'], reverse=True)
    
        # Add ranking (handle ties)
        result = []
        rank = 1
        prev_score = None
        for i, participant in enumerate(participants_data):
            if prev_score is not None and participant['total_saved'] < prev_score:
                rank = i + 1
        
            participant['rank'] = rank
            result.append(participant)
            prev_score = participant['total_saved']
    
        return result

    def _get_user_activity_count(self, user_id, activity_types, start_date, end_date):
        """Helper method: Get count of user's activities"""
        from sqlalchemy import func
        return db.session.query(func.count(CarbonFootprintLog.id)).filter(
            CarbonFootprintLog.user_id == user_id,
            CarbonFootprintLog.activity_type.in_(activity_types),
            CarbonFootprintLog.activity_date >= start_date,
            CarbonFootprintLog.activity_date <= end_date
        ).scalar() or 0

    def get_current_user_rank_info(self):
        """Get ranking information for the current user"""
        from flask_login import current_user
    
        if not hasattr(current_user, 'id'):
            return None
    
        rankings = self.get_participants_ranking()
        for participant in rankings:
            if participant['user_id'] == current_user.id:
                return {
                    'rank': participant['rank'],
                    'total_saved': participant['total_saved'],
                    'activities_count': participant['activities_count'],
                    'total_participants': len(rankings)
                }
    
        # Current user not in rankings
        return None
    
    def __repr__(self):
        return f'<SustainabilityEvent {self.title}>'

class EventRegistration(db.Model):
    """Model for event registrations"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('sustainability_event.id'), nullable=False)
    status = db.Column(db.String(20), default='registered')
    registered_at = db.Column(db.DateTime, default=datetime.now)
    attended = db.Column(db.Boolean, default=False)

    attended = db.Column(db.Boolean, default=False)

    # relationship to user
    user = db.relationship('User', backref='event_registrations')

    # Ensure one registration per user per event
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_registration'),)
    
    def __repr__(self):
        return f'<EventRegistration user:{self.user_id} event:{self.event_id}>'