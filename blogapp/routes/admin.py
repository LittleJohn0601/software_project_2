# blogapp/routes/admin.py
"""Admin routes for system management"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from blogapp.decorators import admin_required
from blogapp.models import User, Factory, HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
from blogapp import db

bp = Blueprint('admin', __name__)


@bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard page - separate single page for admin"""
    return render_template('admin_dashboard.html')


@bp.route('/api/admin/stats')
@login_required
@admin_required
def get_admin_stats():
    """Get system statistics for admin"""
    try:
        # Count statistics
        total_users = User.query.filter_by(user_type='user').count()
        total_admins = User.query.filter_by(user_type='admin').count()
        total_factories = Factory.query.count()
        
        # Calculate total energy usage
        factories = Factory.query.all()
        total_monthly_usage = sum(f.monthly_usage for f in factories)
        total_carbon_emission = sum(f.carbon_emission for f in factories)
        
        # Get recent users
        recent_users = User.query.filter_by(user_type='user').order_by(User.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_admins': total_admins,
                'total_factories': total_factories,
                'total_monthly_usage': round(total_monthly_usage, 2),
                'total_carbon_emission': round(total_carbon_emission, 2)
            },
            'recent_users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'created_at': u.created_at.strftime('%Y-%m-%d %H:%M')
            } for u in recent_users]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/admin/users')
@login_required
@admin_required
def get_all_users():
    """Get all users for admin"""
    try:
        users = User.query.filter_by(user_type='user').all()
        
        user_list = []
        for user in users:
            factories = Factory.query.filter_by(user_id=user.id).all()
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M'),
                'factory_count': len(factories),
                'total_usage': sum(f.monthly_usage for f in factories),
                'total_carbon': sum(f.carbon_emission for f in factories)
            })
        
        return jsonify({
            'success': True,
            'users': user_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/admin/factories')
@login_required
@admin_required
def get_all_factories():
    """Get all factories for admin"""
    try:
        factories = Factory.query.all()
        
        factory_list = []
        for factory in factories:
            user = User.query.get(factory.user_id)
            factory_list.append({
                'id': factory.id,
                'name': factory.name,
                'location': factory.location,
                'industry_type': factory.industry_type,
                'voltage_level': factory.voltage_level,
                'monthly_usage': factory.monthly_usage,
                'carbon_emission': factory.carbon_emission,
                'user': {
                    'id': user.id,
                    'username': user.username
                } if user else None
            })
        
        return jsonify({
            'success': True,
            'factories': factory_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
