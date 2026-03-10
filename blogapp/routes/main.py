# blogapp/routes/main.py

import datetime
from datetime import timedelta
from functools import wraps

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, session, current_app, make_response, jsonify
)
from flask_login import (
    login_required, current_user, logout_user
)
from sqlalchemy import func, or_
from blogapp import db, impact_calculator
from blogapp.forms import EventForm, LogActivityForm
from blogapp.models import (
    User, SustainabilityEvent, EventRegistration, CarbonFootprintLog
)

# -------------------------------------------------------------
# Blueprint
# -------------------------------------------------------------
bp = Blueprint('main', __name__)

# -------------------------------------------------------------
# Constants & Cache
# -------------------------------------------------------------
carbon_stats_cache = {}
CACHE_DURATION = 300  # 5 minutes

# Mapping between activity types and event types (for statistics & explanation)
ACTIVITY_EVENT_MAPPING = {
    'cycling': ['challenge', 'cycling_challenge'],
    'recycling': ['cleanup', 'recycling_cleanup'],
    'energy_saving': ['workshop', 'energy_workshop', 'seminar'],
    'public_transport': ['challenge', 'transport_challenge'],
    'vegetarian_meal': ['challenge', 'vegetarian_challenge'],
    'planting': ['tree_planting'],
}

# Display names for activity types (for frontend)
ACTIVITY_DISPLAY_NAMES = {
    'cycling': '🚴 Cycling',
    'recycling': '♻️ Recycling',
    'energy_saving': '💡 Energy Saving',
    'public_transport': '🚆 Public Transport',
    'vegetarian_meal': '🥗 Vegetarian Meal',
    'planting': '🌳 Tree Planting',
}

# Rough CO₂ conversion rules (consistent with impact_calculator comments)
ACTIVITY_CO2_RULES = {
    'cycling': 'Approx. 0.2 kg CO₂ saved per km cycled (compared to driving).',
    'recycling': 'Approx. 1.5 kg CO₂ saved per kg of materials recycled.',
    'energy_saving': 'Approx. 0.5 kg CO₂ saved per kWh of electricity you avoided.',
    'public_transport': 'Approx. 0.1 kg CO₂ saved per km travelled by public transport (vs. car).',
    'vegetarian_meal': 'Approx. 2.0 kg CO₂ saved per vegetarian meal (vs. meat-based meal).',
    'planting': 'Tree planting contributes to long-term CO₂ absorption; log the estimated CO₂ benefit here.',
}

# 21 kg CO₂ ≈ absorption of 1 mature tree per year
TREE_EQUIVALENT_KG = 21.0

# -------------------------------------------------------------
# Basic Pages
# -------------------------------------------------------------
@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home - UCD GreenLife')


@bp.route('/dashboard')
@login_required
def dashboard():
    try:
        user_stats = get_user_stats(current_user.id)
        recent_activities = (
            CarbonFootprintLog.query.filter_by(user_id=current_user.id)
            .order_by(CarbonFootprintLog.activity_date.desc())
            .limit(5).all()
        )
        return render_template(
            'dashboard.html',
            user_stats=user_stats,
            recent_activities=recent_activities
        )
    except Exception as e:
        print(f"Error in dashboard route: {e}")
        return render_template(
            'dashboard.html',
            user_stats={
                'total_carbon_saved': 0, 'activity_count': 0,
                'rank': 'Newcomer', 'progress_percentage': 0,
                'achievements': {
                    'eco_starter': False, 'green_commuter': False, 'energy_saver': False
                },
                'user_trees_equivalent': 0.0
            },
            recent_activities=[]
        )


# -------------------------------------------------------------
# Music Player Persistence
# -------------------------------------------------------------

@bp.route('/api/music/state', methods=['GET', 'POST'])
@login_required
def music_state():
    """Get or update music player state"""
    try:
        if request.method == 'GET':
            # Get current music state from session
            state = {
                'isPlaying': session.get('music_playing', False),
                'volume': session.get('music_volume', 0.3),
                'lastUpdated': session.get('music_last_updated')
            }
            return jsonify({
                'success': True,
                'state': state
            })
        
        elif request.method == 'POST':
            # check structure
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Request must be JSON'
                }), 400
                
            data = request.get_json()
            
            # validate data
            if data is None:
                return jsonify({
                    'success': False,
                    'message': 'No data provided'
                }), 400
            
            # update music status
            if 'isPlaying' in data:
                session['music_playing'] = bool(data['isPlaying'])
            
            if 'volume' in data:
                try:
                    volume = float(data['volume'])
                    if 0 <= volume <= 1:
                        session['music_volume'] = volume
                    else:
                        return jsonify({
                            'success': False,
                            'message': 'Volume must be between 0 and 1'
                        }), 400
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid volume value'
                    }), 400
            
            session['music_last_updated'] = datetime.datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'message': 'Music state updated',
                'state': {
                    'isPlaying': session.get('music_playing', False),
                    'volume': session.get('music_volume', 0.3),
                    'lastUpdated': session.get('music_last_updated')
                }
            })
            
    except Exception as e:
        print(f"Error in music_state endpoint: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@bp.route('/api/music/sync', methods=['POST'])
@login_required
def sync_music_state():
    """Sync music state across tabs/sessions"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Request must be JSON'
            }), 400
            
        data = request.get_json()
        
        if data is None:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Store in database for cross-device sync (optional)
        user = User.query.get(current_user.id)
        if user:
            
            user_preferences = user.preferences or {}
            user_preferences['music'] = {
                'isPlaying': data.get('isPlaying', False),
                'volume': data.get('volume', 0.3),
                'lastSynced': datetime.datetime.now().isoformat()
            }
            user.preferences = user_preferences
            db.session.commit()
        
        # Also store in session
        session['music_playing'] = data.get('isPlaying', False)
        session['music_volume'] = data.get('volume', 0.3)
        session['music_last_synced'] = datetime.datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Music state synced'
        })
        
    except Exception as e:
        print(f"Error syncing music state: {e}")
        return jsonify({
            'success': False,
            'message': 'Error syncing music state'
        }), 500
    

@bp.route('/impact_center')
@login_required
def impact_center():
    return render_template('impact_center.html', title='Impact Center')


# -------------------------------------------------------------
# Activity Logging (Log Activity)
# -------------------------------------------------------------
@bp.route('/log_activity', methods=['GET', 'POST'])
@login_required
def log_activity():
    form = LogActivityForm()
    if form.validate_on_submit():
        activity = CarbonFootprintLog(
            user_id=current_user.id,
            activity_type=form.activity_type.data,
            carbon_saved=form.carbon_saved.data,
            activity_date=datetime.datetime.now(),
            notes=form.notes.data
        )
        db.session.add(activity)
        db.session.commit()

    
        # Clear cache for related events
        clear_related_events_cache(activity.activity_type)

        flash('Activity logged successfully! 🌟', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template(
        'log_activity.html',
        form=form,
        title='Log Activity',
        activity_co2_rules=ACTIVITY_CO2_RULES,
        activity_display_names=ACTIVITY_DISPLAY_NAMES,
        tree_equivalent_kg=TREE_EQUIVALENT_KG,
        activity_event_mapping=ACTIVITY_EVENT_MAPPING,
    )


def get_carbon_stats_with_cache(event_id, event_type):
    """Get event carbon savings statistics with caching"""
    cache_key = f"carbon_stats_{event_id}"
    now = datetime.datetime.now()

    # Cache hit
    if cache_key in carbon_stats_cache:
        cached_data, ts = carbon_stats_cache[cache_key]
        if now - ts < timedelta(seconds=CACHE_DURATION):
            return cached_data

    # Recalculate
    related_activities = [
        a for a, event_types in ACTIVITY_EVENT_MAPPING.items()
        if event_type in event_types
    ]

    if not related_activities:
        result = {'total_carbon_saved': 0.0, 'activity_count': 0}
    else:
        cnt, total = db.session.query(
            func.count(CarbonFootprintLog.id),
            func.sum(CarbonFootprintLog.carbon_saved)
        ).filter(
            CarbonFootprintLog.activity_type.in_(related_activities)
        ).first()
        result = {
            'total_carbon_saved': total or 0.0,
            'activity_count': cnt or 0
        }

    carbon_stats_cache[cache_key] = (result, now)
    return result


def clear_related_events_cache(activity_type):
    """Clear cache for corresponding events when an activity type changes"""
    related_event_types = ACTIVITY_EVENT_MAPPING.get(activity_type, [])
    if not related_event_types:
        return
    for ev in SustainabilityEvent.query.filter(
        SustainabilityEvent.event_type.in_(related_event_types)
    ).all():
        carbon_stats_cache.pop(f"carbon_stats_{ev.id}", None)


# -------------------------------------------------------------
# Personal Progress
# -------------------------------------------------------------
@bp.route('/my_progress')
@login_required
def my_progress():
    user_stats = get_user_stats(current_user.id)
    
    # Get more historical data for charts (e.g., last 30 days)
    recent_activities = (
        CarbonFootprintLog.query.filter_by(user_id=current_user.id)
        .order_by(CarbonFootprintLog.activity_date.desc())
        .limit(30).all()  # Get last 30 activities
    )
    
    return render_template(
        'my_progress.html',
        user_stats=user_stats,
        recent_activities=recent_activities,
        title='My Progress'
    )
    
    # Get activities from the last 30 days for charts
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
    activities = CarbonFootprintLog.query.filter(
        CarbonFootprintLog.user_id == current_user.id,
        CarbonFootprintLog.activity_date >= start_date,
        CarbonFootprintLog.activity_date <= end_date
    ).order_by(CarbonFootprintLog.activity_date.desc()).all()
    
    # Prepare chart data
    chart_data = []
    for activity in activities[:10]:  # Only take last 10 activities for preview
        chart_data.append({
            'date': activity.activity_date.strftime('%Y-%m-%d'),
            'carbon_saved': activity.carbon_saved,
            'activity_type': activity.activity_type
        })
    
    return render_template(
        'my_progress.html', 
        user_stats=user_stats,
        chart_data=chart_data,
        title='My Progress'
    )


@bp.route('/api/user_chart_data')
@login_required
def get_user_chart_data():
    """Get time-series carbon savings data for the user"""
    try:
        # Get query parameters
        time_range = request.args.get('range', '30d')
        chart_type = request.args.get('type', 'daily')
        
        # Calculate start date
        end_date = datetime.date.today()
        if time_range == '7d':
            start_date = end_date - datetime.timedelta(days=7)
        elif time_range == '30d':
            start_date = end_date - datetime.timedelta(days=30)
        elif time_range == '3m':
            start_date = end_date - datetime.timedelta(days=90)
        elif time_range == '1y':
            start_date = end_date - datetime.timedelta(days=365)
        else:
            start_date = end_date - datetime.timedelta(days=30)  # Default 30 days
        
        # Query all user activities
        activities = CarbonFootprintLog.query.filter(
            CarbonFootprintLog.user_id == current_user.id,
            CarbonFootprintLog.activity_date >= start_date,
            CarbonFootprintLog.activity_date <= end_date
        ).order_by(CarbonFootprintLog.activity_date.asc()).all()
        
        # Build time-series data
        if chart_type == 'weekly':
            # Aggregate by week
            data = aggregate_by_week(activities, start_date, end_date)
        elif chart_type == 'monthly':
            # Aggregate by month
            data = aggregate_by_month(activities, start_date, end_date)
        else:
            # Default: aggregate by day
            data = aggregate_by_day(activities, start_date, end_date)
        
        # Calculate statistics
        total_saved = sum(activity.carbon_saved for activity in activities)
        average_daily = total_saved / len(data['data']) if data['data'] else 0
        best_day_value = max(data['data']) if data['data'] else 0
        
        # Get goal progress (from dashboard user stats)
        user_stats = get_user_stats(current_user.id)
        
        return jsonify({
            'success': True,
            'labels': data['labels'],
            'data': data['data'],
            'total_saved': round(total_saved, 1),
            'average_daily': round(average_daily, 2),
            'best_day': round(best_day_value, 2),
            'goal_progress': user_stats['progress_percentage']
        })
        
    except Exception as e:
        print(f"Error getting chart data: {e}")
        return jsonify({
            'success': False,
            'message': 'Error loading chart data'
        }), 500

def aggregate_by_day(activities, start_date, end_date):
    """Aggregate data by day"""
    # Create date range
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date)
        current_date += datetime.timedelta(days=1)
    
    # Group activities by date
    daily_data = {}
    for activity in activities:
        date_str = activity.activity_date.strftime('%Y-%m-%d')
        if date_str in daily_data:
            daily_data[date_str] += activity.carbon_saved
        else:
            daily_data[date_str] = activity.carbon_saved
    
    # Build results
    labels = []
    data = []
    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        labels.append(date.strftime('%b %d'))  # Format like "Jan 01"
        data.append(round(daily_data.get(date_str, 0), 1))
    
    return {'labels': labels, 'data': data}

def aggregate_by_week(activities, start_date, end_date):
    """Aggregate data by week"""
    # Group by week
    weekly_data = {}
    for activity in activities:
        # Get week start
        week_start = activity.activity_date - datetime.timedelta(days=activity.activity_date.weekday())
        week_key = week_start.strftime('%Y-%m-%d')
        
        if week_key in weekly_data:
            weekly_data[week_key] += activity.carbon_saved
        else:
            weekly_data[week_key] = activity.carbon_saved
    
    # Build labels and data
    labels = []
    data = []
    
    # Generate week labels
    current_week = start_date - datetime.timedelta(days=start_date.weekday())
    while current_week <= end_date:
        week_key = current_week.strftime('%Y-%m-%d')
        week_label = f"Week {current_week.isocalendar()[1]}"  # Week number
        
        labels.append(week_label)
        data.append(round(weekly_data.get(week_key, 0), 1))
        
        current_week += datetime.timedelta(days=7)
    
    return {'labels': labels, 'data': data}

def aggregate_by_month(activities, start_date, end_date):
    """Aggregate data by month"""
    # Group by month
    monthly_data = {}
    for activity in activities:
        month_key = activity.activity_date.strftime('%Y-%m')
        
        if month_key in monthly_data:
            monthly_data[month_key] += activity.carbon_saved
        else:
            monthly_data[month_key] = activity.carbon_saved
    
    # Build labels and data
    labels = []
    data = []
    
    # Generate month labels
    current_month = start_date.replace(day=1)
    while current_month <= end_date:
        month_key = current_month.strftime('%Y-%m')
        month_label = current_month.strftime('%b %Y')  # Format like "Jan 2024"
        
        labels.append(month_label)
        data.append(round(monthly_data.get(month_key, 0), 1))
        
        # Next month
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month + 1)
    
    return {'labels': labels, 'data': data}


# -------------------------------------------------------------
# Events
# -------------------------------------------------------------
@bp.route('/events')
@login_required
def events():
    try:
        filter_type = request.args.get('filter', 'all')
        search_query = request.args.get('search', '').strip()

        query = SustainabilityEvent.query

        # Filtering
        if filter_type == 'upcoming':
            query = query.filter(SustainabilityEvent.start_date > datetime.datetime.now())
        elif filter_type == 'past':
            query = query.filter(SustainabilityEvent.end_date < datetime.datetime.now())
        elif filter_type == 'my':
            registered_ids = db.session.query(EventRegistration.event_id).filter(
                EventRegistration.user_id == current_user.id,
                EventRegistration.status == 'registered'
            ).subquery()
            query = query.filter(SustainabilityEvent.id.in_(registered_ids))

        # Search
        if search_query and len(search_query) >= 2:
            if len(search_query) > 50:
                flash('Search query too long', 'warning')
            else:
                query = query.filter(or_(
                    SustainabilityEvent.title.ilike(f'%{search_query}%'),
                    SustainabilityEvent.description.ilike(f'%{search_query}%'),
                    SustainabilityEvent.location.ilike(f'%{search_query}%'),
                ))

        events = query.order_by(SustainabilityEvent.start_date.asc()).all()

        enhanced = []
        for ev in events:
            carbon_stats = get_carbon_stats_with_cache(ev.id, ev.event_type)
            related_acts = [
                a for a, ets in ACTIVITY_EVENT_MAPPING.items() if ev.event_type in ets
            ]
            key = related_acts[0] if related_acts else None

            data = {
                'id': ev.id,
                'title': ev.title,
                'description': ev.description,
                'type': ev.event_type,
                'location': ev.location,
                'start_date': ev.start_date,
                'end_date': ev.end_date,
                'max_participants': ev.max_participants,
                'current_participants': ev.current_participants,
                'status': ev.status,
                'display_date': ev.display_date,
                'time_range': ev.time_range,
                'organizer': ev.organizer.username,
                'is_full': ev.is_full,
                'total_carbon_saved': carbon_stats['total_carbon_saved'],
                'activity_count': carbon_stats['activity_count'],
                'related_activities': related_acts,
                'linked_activity_key': key,
                'linked_activity_label': ACTIVITY_DISPLAY_NAMES.get(key) if key else None,
                'linked_activity_co2_rule': ACTIVITY_CO2_RULES.get(key) if key else None,
            }

            reg = EventRegistration.query.filter_by(
                user_id=current_user.id, event_id=ev.id
            ).first()
            data['is_registered'] = (reg is not None and reg.status == 'registered')
            data['registration_status'] = reg.status if reg else None
            data['can_register'] = ev.can_register(current_user)[0]

            enhanced.append(data)

        form = EventForm() if current_user.is_authenticated and current_user.is_staff else None

        return render_template(
            'events.html',
            events=enhanced,
            form=form,
            current_filter=filter_type,
            search_query=search_query,
            activity_co2_rules=ACTIVITY_CO2_RULES,
            activity_display_names=ACTIVITY_DISPLAY_NAMES,
            tree_equivalent_kg=TREE_EQUIVALENT_KG,
        )
    except Exception as e:
        print(f"Error in events route: {e}")
        flash('Error loading events. Please try again.', 'danger')
        return render_template(
            'events.html',
            events=[],
            form=None,
            current_filter='all',
            search_query='',
            activity_co2_rules=ACTIVITY_CO2_RULES,
            activity_display_names=ACTIVITY_DISPLAY_NAMES,
            tree_equivalent_kg=TREE_EQUIVALENT_KG,
        )


@bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if not getattr(current_user, 'is_staff', False):
        flash('Only staff members can create events.', 'danger')
        return redirect(url_for('main.events'))

    form = EventForm()
    if form.validate_on_submit():
        try:
            if not hasattr(form, 'start_date_parsed') or not hasattr(form, 'end_date_parsed'):
                flash('Please check the date formats and try again.', 'danger')
                return render_template('create_event.html', form=form)

            ev = SustainabilityEvent(
                title=form.title.data,
                description=form.description.data,
                event_type=form.event_type.data,
                location=form.location.data,
                start_date=form.start_date_parsed,
                end_date=form.end_date_parsed,
                max_participants=form.max_participants.data,
                organizer_id=current_user.id
            )
            db.session.add(ev)
            db.session.commit()

            

            flash('Event created successfully! 🎉', 'success')
            return redirect(url_for('main.events'))
        except Exception as e:
            db.session.rollback()

            
            print(f"Error creating event: {e}")
            flash('Error creating event. Please try again.', 'danger')

    return render_template('create_event.html', form=form)


@bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not getattr(current_user, 'is_staff', False):
        flash('Only staff members can edit events.', 'danger')
        return redirect(url_for('main.events'))

    ev = SustainabilityEvent.query.get_or_404(event_id)

    if ev.organizer_id != current_user.id and current_user.user_type != 'admin':
        flash('You can only edit events you created.', 'danger')
        return redirect(url_for('main.events'))

    form = EventForm()
    if request.method == 'GET':
        form.title.data = ev.title
        form.description.data = ev.description
        form.event_type.data = ev.event_type
        form.location.data = ev.location
        form.start_date.data = ev.start_date.strftime('%Y-%m-%d %H:%M')
        form.end_date.data = ev.end_date.strftime('%Y-%m-%d %H:%M')
        form.max_participants.data = ev.max_participants

    if form.validate_on_submit():
        try:
            ev.title = form.title.data
            ev.description = form.description.data
            ev.event_type = form.event_type.data
            ev.location = form.location.data
            ev.start_date = form.start_date_parsed
            ev.end_date = form.end_date_parsed
            ev.max_participants = form.max_participants.data
            db.session.commit()

            
            flash('Event updated successfully! ✅', 'success')
            return redirect(url_for('main.events'))
        except Exception as e:
            db.session.rollback()
            
            print(f"Error updating event: {e}")
            flash('Error updating event. Please try again.', 'danger')

    return render_template('edit_event.html', form=form, event=ev, title='Edit Event')


@bp.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    try:
        ev = SustainabilityEvent.query.get_or_404(event_id)

        reg = EventRegistration.query.filter_by(
            user_id=current_user.id, event_id=event_id
        ).first()

        if reg:
            if reg.status == 'registered':
                flash('You are already registered for this event.', 'warning')
            else:
                reg.status = 'registered'
                reg.registered_at = datetime.datetime.now()
                db.session.commit()
                flash('Registration updated successfully!', 'success')
            return redirect(url_for('main.events'))

        if ev.is_full:
            flash('This event is already full. You can join the waitlist.', 'warning')
            return redirect(url_for('main.events'))

        if ev.status == 'completed':
            flash('Registration is closed for this event.', 'warning')
            return redirect(url_for('main.events'))

        reg = EventRegistration(user_id=current_user.id, event_id=event_id, status='registered')
        db.session.add(reg)
        db.session.commit()
        flash('Successfully registered for the event! 🎉', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error registering for event: {e}")
        flash('Error registering for event. Please try again.', 'danger')

    return redirect(url_for('main.events'))


@bp.route('/events/<int:event_id>/details')
@login_required
def event_details(event_id):
    ev = SustainabilityEvent.query.get_or_404(event_id)

    reg = EventRegistration.query.filter_by(
        user_id=current_user.id, event_id=ev.id, status='registered'
    ).first()
    is_registered = reg is not None

    related_acts = [
        a for a, ets in ACTIVITY_EVENT_MAPPING.items() if ev.event_type in ets
    ]

    now = datetime.datetime.now()
    end_cutoff = ev.end_date if ev.end_date < now else now

    if related_acts:
        total_saved = db.session.query(
            func.coalesce(func.sum(CarbonFootprintLog.carbon_saved), 0.0)
        ).filter(
            CarbonFootprintLog.user_id == current_user.id,
            CarbonFootprintLog.activity_type.in_(related_acts),
            CarbonFootprintLog.activity_date >= ev.start_date,
            CarbonFootprintLog.activity_date <= end_cutoff
        ).scalar() or 0.0

        user_acts = CarbonFootprintLog.query.filter(
            CarbonFootprintLog.user_id == current_user.id,
            CarbonFootprintLog.activity_type.in_(related_acts),
            CarbonFootprintLog.activity_date >= ev.start_date,
            CarbonFootprintLog.activity_date <= end_cutoff
        ).order_by(CarbonFootprintLog.activity_date.desc()).all()
    else:
        total_saved = db.session.query(
            func.coalesce(func.sum(CarbonFootprintLog.carbon_saved), 0.0)
        ).filter(
            CarbonFootprintLog.user_id == current_user.id,
            CarbonFootprintLog.activity_type == ev.event_type,
            CarbonFootprintLog.activity_date >= ev.start_date,
            CarbonFootprintLog.activity_date <= end_cutoff
        ).scalar() or 0.0

        user_acts = CarbonFootprintLog.query.filter(
            CarbonFootprintLog.user_id == current_user.id,
            CarbonFootprintLog.activity_type == ev.event_type,
            CarbonFootprintLog.activity_date >= ev.start_date,
            CarbonFootprintLog.activity_date <= end_cutoff
        ).order_by(CarbonFootprintLog.activity_date.desc()).all()

    target = ev.carbon_target
    if not target or target <= 0:
        progress_pct = 0
        target = 0
    else:
        progress_pct = int(min(total_saved / target, 1.0) * 100)

    return render_template(
        'event_details.html',
        event=ev,
        is_registered=is_registered,
        total_saved=total_saved,
        target=target,
        progress_pct=progress_pct,
        related_activities=related_acts,
        user_activities=user_acts,
        activity_display_names=ACTIVITY_DISPLAY_NAMES,
        activity_co2_rules=ACTIVITY_CO2_RULES,
        tree_equivalent_kg=TREE_EQUIVALENT_KG,
    )


@bp.route('/events/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_registration(event_id):
    try:
        reg = EventRegistration.query.filter_by(
            user_id=current_user.id, event_id=event_id
        ).first()
        if not reg:
            flash('You are not registered for this event.', 'warning')
            return redirect(url_for('main.events'))

        reg.status = 'cancelled'
        db.session.commit()
        flash('Registration cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error cancelling registration: {e}")
        flash('Error cancelling registration. Please try again.', 'danger')

    return redirect(url_for('main.events'))


@bp.route('/events/<int:event_id>/participants')
@login_required
def view_participants(event_id):
    if not getattr(current_user, 'is_staff', False):
        flash('Permission denied. Staff access only.', 'danger')
        return redirect(url_for('main.events'))

    ev = SustainabilityEvent.query.get_or_404(event_id)
    regs = (EventRegistration.query
            .filter_by(event_id=event_id, status='registered')
            .join(User, EventRegistration.user_id == User.id)
            .order_by(EventRegistration.registered_at.asc())
            .all())

    return render_template('view_participants.html', event=ev, registrations=regs)

@bp.route('/events/<int:event_id>/ranking')
@login_required
def event_ranking(event_id):
    """Event participant ranking page - accessible to all users"""
    ev = SustainabilityEvent.query.get_or_404(event_id)
    
    # Check if user is registered (for personalized display)
    reg = EventRegistration.query.filter_by(
        user_id=current_user.id, event_id=ev.id, status='registered'
    ).first()
    is_registered = reg is not None
    
    # Get all participant rankings
    participants_ranking = ev.get_participants_ranking()
    
    # Get current user's ranking info (if registered)
    current_user_rank_info = None
    if is_registered:
        for i, participant in enumerate(participants_ranking):
            if participant['user_id'] == current_user.id:
                current_user_rank_info = {
                    'rank': participant['rank'],
                    'total_saved': participant['total_saved'],
                    'activities_count': participant['activities_count'],
                    'total_participants': len(participants_ranking)
                }
                break
    
    # Calculate statistics
    total_participants = len(participants_ranking)
    total_co2_saved = sum(p['total_saved'] for p in participants_ranking) if participants_ranking else 0
    total_activities = sum(p['activities_count'] for p in participants_ranking) if participants_ranking else 0
    
    # Get top 3 participants
    top_3 = participants_ranking[:3] if len(participants_ranking) >= 3 else participants_ranking
    
    return render_template(
        'event_ranking.html',
        event=ev,
        participants_ranking=participants_ranking,
        current_user_rank_info=current_user_rank_info,
        top_3=top_3,
        total_participants=total_participants,
        total_co2_saved=total_co2_saved,
        total_activities=total_activities,
        is_registered=is_registered,
        is_staff=current_user.is_staff,
        is_admin=current_user.is_admin,
        activity_display_names=ACTIVITY_DISPLAY_NAMES,
        tree_equivalent_kg=TREE_EQUIVALENT_KG,
    )


@bp.route('/events/<int:event_id>/participants/<int:registration_id>/remove', methods=['POST'])
@login_required
def remove_participant(event_id, registration_id):
    if not getattr(current_user, 'is_staff', False):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Permission denied. Staff access only.'}), 403
        flash('Permission denied. Staff access only.', 'danger')
        return redirect(url_for('main.events'))

    ev = SustainabilityEvent.query.get_or_404(event_id)
    reg = EventRegistration.query.filter_by(
        id=registration_id, event_id=event_id, status='registered'
    ).first()

    if not reg:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Participant not found or already removed.'}), 404
        flash('Participant not found or already removed.', 'warning')
        return redirect(url_for('main.view_participants', event_id=ev.id))

    try:
        reg.status = 'cancelled'
        db.session.commit()
        
        # AJAX response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Participant removed successfully.',
                'registration_id': registration_id,
                'event_id': event_id,
                'student_name': reg.user.username
            })
        
        # Regular response
        flash('Participant removed successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f'Error removing participant: {e}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False, 
                'message': 'Error removing participant. Please try again.'
            }), 500
        
        flash('Error removing participant. Please try again.', 'danger')

    return redirect(url_for('main.view_participants', event_id=ev.id))


# -------------------------------------------------------------
# Data Export & Settings Page
# -------------------------------------------------------------
@bp.route('/export_data', methods=['GET'])
@login_required
def export_data():
    """Export current user data (CSV / JSON)"""
    format_type = request.args.get('format', 'csv').lower()
    if format_type not in ['csv', 'json']:
        flash('Invalid export format', 'danger')
        return redirect(url_for('main.settings'))

    try:
        activities = (CarbonFootprintLog.query
                      .filter_by(user_id=current_user.id)
                      .order_by(CarbonFootprintLog.activity_date.desc())
                      .all())

        registrations = EventRegistration.query.filter_by(
            user_id=current_user.id
        ).all()

        if format_type == 'csv':
            import csv, io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Type', 'Date', 'Description', 'Carbon Saved (kg)', 'Status'])

            for a in activities:
                writer.writerow([
                    'Activity',
                    a.activity_date.strftime('%Y-%m-%d'),
                    f"{a.activity_type} - {a.notes or 'No notes'}",
                    a.carbon_saved,
                    'Completed'
                ])

            for r in registrations:
                ev = SustainabilityEvent.query.get(r.event_id)
                if ev:
                    writer.writerow([
                        'Event Registration',
                        ev.start_date.strftime('%Y-%m-%d'),
                        ev.title,
                        'N/A',
                        r.status
                    ])

            resp = make_response(output.getvalue())
            resp.headers["Content-Disposition"] = f"attachment; filename=ucd_greenlife_data_{current_user.username}.csv"
            resp.headers["Content-type"] = "text/csv"
            return resp

        # JSON
        import json
        data = {
            'user_info': {
                'username': current_user.username,
                'email': current_user.email,
                'user_type': current_user.user_type,
                'joined_date': getattr(current_user, 'created_at', None).strftime('%Y-%m-%d')
                                if getattr(current_user, 'created_at', None) else 'N/A'
            },
            'activities': [
                {
                    'date': a.activity_date.strftime('%Y-%m-%d'),
                    'type': a.activity_type,
                    'carbon_saved': float(a.carbon_saved),
                    'notes': a.notes
                } for a in activities
            ],
            'event_registrations': [
                {
                    'event_title': (SustainabilityEvent.query.get(r.event_id).title
                                    if SustainabilityEvent.query.get(r.event_id) else 'Unknown Event'),
                'status': r.status,
                'registered_at': r.registered_at.strftime('%Y-%m-%d %H:%M:%S'),
                'attended': r.attended
                } for r in registrations
            ],
            'stats': get_user_stats(current_user.id)
        }

        resp = make_response(json.dumps(data, indent=2))
        resp.headers["Content-Disposition"] = f"attachment; filename=ucd_greenlife_data_{current_user.username}.json"
        resp.headers["Content-type"] = "application/json"
        return resp

    except Exception as e:
        print(f"Error exporting data: {e}")
        flash('Error exporting data. Please try again.', 'danger')
        return redirect(url_for('main.settings'))


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page (theme, profile, account deletion, etc.)"""
    return render_template('settings.html', title='Settings')


@bp.route('/settings/update_theme', methods=['POST'])
@login_required
def update_theme():
    try:
        theme = request.form.get('theme', 'light')
        font_size = request.form.get('font_size', 'medium')
        color_scheme = request.form.get('color_scheme', 'green')
        session['theme'] = theme
        session['font_size'] = font_size
        session['color_scheme'] = color_scheme
        flash(f'Theme updated', 'success')
    except Exception as e:
        print(f"Error updating theme: {e}")
        flash('Error updating theme settings', 'danger')
    return redirect(url_for('main.settings'))

@bp.route('/api/set-color-scheme', methods=['POST'])
@login_required
def set_color_scheme():
    """API endpoint to save color scheme preference"""
    try:
        data = request.get_json()
        color_scheme = data.get('color_scheme', 'green')
        
        # Save to session
        session['color_scheme'] = color_scheme
        
        # Optional: Save to user database
        user = User.query.get(current_user.id)
        if user:
            # If there is a field to store user preferences
            if hasattr(user, 'preferences'):
                user.preferences = user.preferences or {}
                user.preferences['color_scheme'] = color_scheme
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Color scheme updated',
            'color_scheme': color_scheme
        })
    except Exception as e:
        print(f"Error updating color scheme: {e}")
        return jsonify({
            'success': False,
            'message': 'Error updating color scheme'
        }), 500    


@bp.route('/settings/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        # Check if request is JSON
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip()
            notifications = data.get('notifications', False)
        else:
            # Form submission (non-AJAX)
            email = request.form.get('email', '').strip()
            notifications = request.form.get('notifications', 'off') == 'on'
        
        user = User.query.get(current_user.id)
        
        # Validate email format
        if not User.validate_email_format(email):
            error_msg = "Invalid email format. Please enter a valid email address."
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 400
            flash(error_msg, 'danger')
            return redirect(url_for('main.settings'))
        
        # Check if email is used by another user
        other = User.query.filter_by(_email_encrypted=User._encrypt_email_for_query(email)).first()
        if other and other.id != current_user.id:
            error_msg = 'This email is already registered to another account.'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 400
            flash(error_msg, 'danger')
            return redirect(url_for('main.settings'))
        
        # Skip update if email is the same as current
        if user.email == email:
            print(f"Email unchanged for user {user.username}")
        else:
            # Update email
            user.email = email
            print(f"Email updated for user {user.username}: {email}")
        
        # Update notification settings
        notification_settings = {
            'notifications_enabled': notifications,
            'achievement_alerts': data.get('achievement_alerts', False) if request.is_json else 
                                 (request.form.get('achievement_alerts', 'off') == 'on'),
            'weekly_reports': data.get('weekly_reports', False) if request.is_json else 
                             (request.form.get('weekly_reports', 'off') == 'on')
        }
        
        for key, value in notification_settings.items():
            session[key] = value
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully!',
                'email': email,
                'notification_settings': notification_settings
            })
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.settings'))
        
    except ValueError as e:
        # Email format error
        error_msg = str(e)
        if request.is_json:
            return jsonify({'success': False, 'message': error_msg}), 400
        flash(error_msg, 'danger')
        return redirect(url_for('main.settings'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating profile: {e}")
        
        error_msg = 'An unexpected error occurred. Please try again.'
        if request.is_json:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500
        
        flash(error_msg, 'danger')
        return redirect(url_for('main.settings'))


@bp.route('/settings/delete_account', methods=['POST'])
@login_required
def delete_account():
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Get confirmation text
        if request.is_json:
            data = request.get_json()
            confirm = data.get('confirm_text', '').strip()
        else:
            confirm = request.form.get('confirm_text', '').strip()
        
        # Validate confirmation text
        required_text = f"DELETE {current_user.username}"
        if confirm != required_text:
            if is_ajax or request.is_json:
                return jsonify({
                    'success': False, 
                    'message': 'Please type the confirmation text exactly as shown'
                }), 400
            flash('Please type the confirmation text exactly as shown', 'danger')
            return redirect(url_for('main.settings'))

        # Get user info (for logging)
        user = User.query.get(current_user.id)
        username = user.username
        user_id = user.id
        
        print(f"🗑️ Starting account deletion for user: {username} (ID: {user_id})")

        # Delete related data (in order of foreign key constraints)
        print(f"🗑️ Deleting carbon footprint logs...")
        CarbonFootprintLog.query.filter_by(user_id=current_user.id).delete()
        
        print(f"🗑️ Deleting event registrations...")
        EventRegistration.query.filter_by(user_id=current_user.id).delete()
        
        # If staff, delete created events
        if getattr(user, 'is_staff', False):
            print(f"🗑️ Deleting events created by staff user...")
            SustainabilityEvent.query.filter_by(organizer_id=current_user.id).delete()
        
        # Delete user account
        print(f"🗑️ Deleting user account...")
        db.session.delete(user)
        db.session.commit()
        
        print(f"✅ Account {username} deleted successfully")
        
        # Logout and clear session
        logout_user()
        session.clear()
        
        print(f"✅ User session cleared, logged out successfully")
        
        # Build redirect URL with parameters
        redirect_url = url_for('main.index', account_deleted='true', username=username)
        
        # Return response based on request type
        if is_ajax or request.is_json:
            return jsonify({
                'success': True, 
                'message': f'Account {username} has been permanently deleted. Thank you for being part of UCD GreenLife!',
                'redirect_url': redirect_url,
                'username': username
            })
        
        # Non-AJAX request: redirect directly
        flash(f'Account {username} has been permanently deleted. Thank you for being part of UCD GreenLife!', 'success')
        return redirect(redirect_url)
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting account: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_msg = 'Error deleting account. Please try again.'
        if is_ajax or request.is_json:
            return jsonify({
                'success': False, 
                'message': error_msg,
                'error_details': str(e) if current_app.debug else None
            }), 500
        
        flash(error_msg, 'danger')
        return redirect(url_for('main.settings'))


# -------------------------------------------------------------
# Statistics & Ranking
# -------------------------------------------------------------
def get_user_stats(user_id: int):
    calculator = impact_calculator.ImpactCalculator()
    user_impact = calculator.calculate_user_impact(user_id)

    activity_count = CarbonFootprintLog.query.filter_by(user_id=user_id).count()
    user_rank = calculate_user_rank(user_id)
    progress_percentage = min(100, (activity_count / 10) * 100)

    achievements = {
        'eco_starter': activity_count >= 1,
        'green_commuter': user_impact['user_carbon_saved'] >= 50,
        'energy_saver': activity_count >= 3
    }

    return {
        'total_carbon_saved': user_impact['user_carbon_saved'],
        'activity_count': activity_count,
        'rank': user_rank,
        'progress_percentage': progress_percentage,
        'achievements': achievements,
        'user_trees_equivalent': user_impact['user_trees_equivalent'],
    }


def calculate_user_rank(user_id: int) -> str:
    total = db.session.query(
        func.sum(CarbonFootprintLog.carbon_saved)
    ).filter(
        CarbonFootprintLog.user_id == user_id
    ).scalar() or 0.0

    if total == 0:
        return "Newcomer"
    if total < 5:
        return "Eco Beginner"
    if total < 15:
        return "Green Advocate"
    if total < 30:
        return "Sustainability Champion"
    return "Eco Warrior"


# -------------------------------------------------------------
# Admin helpers & routes
# -------------------------------------------------------------
def admin_required(view_func):
    """Admin access required decorator"""
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            flash("Admin access required.", "danger")
            return redirect(url_for("main.dashboard"))
        return view_func(*args, **kwargs)
    return wrapped


@bp.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.order_by(User.id.asc()).all()
    
    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'is_banned': user.is_banned,
                'ban_until': user.ban_until.isoformat() if user.ban_until else None,
                'ban_reason': user.ban_reason
            })
        return jsonify({
            'success': True,
            'users': users_data
        })
    
    # Regular response
    return render_template("admin_users.html", users=users)



@bp.route("/admin/users/<int:user_id>/role", methods=["POST"])
@admin_required
def admin_update_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get("user_type")

    if new_role not in ["student", "teacher", "admin"]:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Invalid role selected.'}), 400
        flash("Invalid role selected.", "danger")
        return redirect(url_for("main.admin_users"))

    if user.user_type == "admin" and new_role != "admin":
        admin_count = User.query.filter_by(user_type="admin").count()
        if admin_count <= 1:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'You cannot remove the last admin account.'}), 400
            flash("You cannot remove the last admin account.", "warning")
            return redirect(url_for("main.admin_users"))

    old = user.user_type
    user.user_type = new_role
    db.session.commit()

    current_app.logger.info(
        "Admin '%s' changed role of user '%s' from %s to %s",
        current_user.username, user.username, old, new_role
    )
    
    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f'Updated role for {user.username} to {new_role}.',
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type
            }
        })
    
    # Regular response
    flash(f"Updated role for {user.username} to {new_role}.", "success")
    return redirect(url_for("main.admin_users"))


@bp.route("/admin/users/<int:user_id>/ban", methods=["POST"])
@admin_required
def admin_ban_user(user_id):
    current_app.logger.info(f"\n{'='*80}")
    current_app.logger.info("=== BAN Request Detailed Log ===")
    current_app.logger.info(f"Time: {datetime.datetime.now()}")
    current_app.logger.info(f"Request Path: {request.path}")
    current_app.logger.info(f"Request Method: {request.method}")
    current_app.logger.info(f"Content Type: {request.content_type}")
    

    # Print all request headers
    print("\n=== Request Headers ===")

    for key, value in request.headers:
        if key.lower() not in ['cookie', 'authorization']:  # Exclude sensitive information
            print(f"  {key}: {value}")
    

    # Print form data
    print("\n=== Form Data ===")
    if request.form:
        for key in request.form:
            value = request.form[key]
            print(f"  {key}: '{value}' (Length: {len(value)})")
    else:
        print("  No form data")
    
    # Print raw data
    print("\n=== Raw Request Data (First 500 Characters) ===")

    try:
        raw_data = request.get_data(as_text=True)
        print(raw_data[:500])
    except:

        print("  Unable to get raw data")

    
    # Special CSRF check
    csrf_token = request.form.get('csrf_token')


    print(f"\n=== CSRF Check ===")
    print(f"CSRF Token Exists: {'Yes' if csrf_token else 'No'}")
    if csrf_token:
        print(f"CSRF Token Length: {len(csrf_token)}")
        print(f"CSRF Token First 30 Characters: {csrf_token[:30]}...")

        
        # Validate CSRF token
        from flask_wtf.csrf import validate_csrf
        try:
            validate_csrf(csrf_token)

            print("CSRF Validation: Passed")
        except Exception as e:
            print(f"CSRF Validation Failed: {str(e)}")
    else:
        print("Error: No CSRF token found")

    
    print(f"\n{'='*80}")
    
    # Return detailed error if CSRF validation fails
    if not csrf_token:
        return jsonify({
            'success': False,
            'message': 'CSRF token missing',
            'debug': {
                'headers': {k: v for k, v in request.headers if k.lower() not in ['cookie']},
                'form_data': dict(request.form),
                'raw_data_preview': request.get_data(as_text=True)[:200] if request.get_data() else None
            }
        }), 400
    
    # Normal ban logic processing...
    user = User.query.get_or_404(user_id)
    
    # Check if banning self
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot ban yourself'}), 400
    
    # Get parameters
    try:
        hours = int(request.form.get('duration_hours', '24'))
    except ValueError:
        hours = 24
    
    reason = request.form.get('ban_reason', '').strip() or None
    
    # Execute ban
    try:
        user.set_temporary_ban(hours, reason)
        db.session.commit()

        current_app.logger.warning(
            "Admin '%s' banned user '%s' (id=%s) for %s hours. Reason: %s",
            current_user.username, user.username, user_id, hours, reason
        )
        
        print(f"Successfully banned: {user.username} for {hours} hours")
        
        return jsonify({
            'success': True,
            'message': f'Account {user.username} is banned for {hours} hours',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_banned': True,
                'ban_until': user.ban_until.isoformat() if user.ban_until else None,
                'ban_reason': user.ban_reason
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Ban Error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route("/admin/users/<int:user_id>/unban", methods=["POST"])
@admin_required
def admin_unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.clear_ban()
    db.session.commit()
    
    current_app.logger.info("Admin '%s' unbanned user '%s'.", current_user.username, user.username)
    
    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f'User {user.username} has been unbanned.',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_banned': False,
                'ban_until': None,
                'ban_reason': None
            }
        })
    
    # Regular response
    flash(f"User {user.username} has been unbanned.", "success")
    return redirect(url_for("main.admin_users"))


@bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'You cannot delete your own admin account.'}), 400
        flash("You cannot delete your own admin account.", "warning")
        return redirect(url_for("main.admin_users"))

    if user.user_type == "admin":
        admin_count = User.query.filter_by(user_type="admin").count()
        if admin_count <= 1:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'You cannot delete the last admin account.'}), 400
            flash("You cannot delete the last admin account.", "warning")
            return redirect(url_for("main.admin_users"))

    username = user.username
    
    # Delete related records first
    CarbonFootprintLog.query.filter_by(user_id=user_id).delete()
    EventRegistration.query.filter_by(user_id=user_id).delete()
    
    if getattr(user, 'is_staff', False):
        SustainabilityEvent.query.filter_by(organizer_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()

    current_app.logger.warning(
        "Admin '%s' deleted user '%s' (id=%s).",
        current_user.username, username, user_id
    )
    
    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f'User {username} has been deleted.',
            'user_id': user_id
        })
    
    # Regular response
    flash(f"User {username} has been deleted.", "success")
    return redirect(url_for("main.admin_users"))


@bp.route("/admin/logs")
@admin_required
def admin_view_logs():
    log_file = current_app.config.get("LOG_FILE", "logs/greenlife.log")

    info_logs, warning_logs, error_logs = [], [], []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if not t:
                    continue
                if " ERROR:" in t or " ERROR " in t:    
                    error_logs.append(t)
                elif " WARNING:" in t or " WARNING " in t:
                    warning_logs.append(t)
                elif " INFO:" in t or " INFO " in t:
                    info_logs.append(t)
                else:
                    # Ignore other log levels
                    pass
    except FileNotFoundError:
        flash("Log file not found yet. It will be created as the app runs.", "warning")

    info_logs = list(reversed(info_logs))
    warning_logs = list(reversed(warning_logs))
    error_logs = list(reversed(error_logs))

    return render_template(
        "admin_logs.html",
        log_file=log_file,
        info_logs=info_logs,
        warning_logs=warning_logs,
        error_logs=error_logs,
    )