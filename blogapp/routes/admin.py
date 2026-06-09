# blogapp/routes/admin.py
"""Admin routes for system management"""

from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from blogapp.decorators import admin_required
from blogapp.models import User, Factory, HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
from blogapp import db, csrf

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
        current_app.logger.error(f"Failed to load admin stats: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to load stats'
        }), 500


@bp.route('/api/admin/users')
@login_required
@admin_required
def get_all_users():
    """Get all users for admin"""
    try:
        users = User.query.filter_by(user_type='user').all()
        
        user_list = []
        for index, user in enumerate(users, start=1):
            factories = Factory.query.filter_by(user_id=user.id, is_deleted=False).all()
            user_list.append({
                'id': user.id,
                'display_id': index,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M'),
                'factory_count': len(factories),
                'total_usage': sum(f.monthly_usage for f in factories),
                'total_carbon': sum(f.carbon_emission for f in factories),
                'is_banned': user.is_banned,
            })
        
        return jsonify({
            'success': True,
            'users': user_list
        })
    except Exception as e:
        current_app.logger.error(f"Failed to load users: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to load users'
        }), 500


@bp.route('/api/admin/factories')
@login_required
@admin_required
def get_all_factories():
    """Get all factories for admin (excluding deleted ones)"""
    try:
        factories = Factory.query.filter_by(is_deleted=False).all()
        
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
        current_app.logger.error(f"Failed to load factories: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to load factories'
        }), 500


@bp.route('/api/admin/users/<int:user_id>/factories')
@login_required
@admin_required
def get_user_factories(user_id):
    """Get all factories for a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        factories = Factory.query.filter_by(user_id=user_id, is_deleted=False).all()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_banned': user.is_banned,
            },
            'factories': [{
                'id': f.id,
                'name': f.name,
                'location': f.location,
                'industry_type': f.industry_type,
                'voltage_level': f.voltage_level,
                'transformer_capacity': f.transformer_capacity,
                'monthly_usage': f.monthly_usage,
                'carbon_emission': f.carbon_emission,
                'created_at': f.created_at.strftime('%Y-%m-%d %H:%M'),
            } for f in factories]
        })
    except Exception as e:
        current_app.logger.error(f"Failed to load user factories: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to load factories'
        }), 500


@bp.route('/api/admin/factory/<int:factory_id>/delete', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def admin_delete_factory(factory_id):
    """Soft-delete a factory (admin action)"""
    try:
        factory = Factory.query.get_or_404(factory_id)
        if factory.is_deleted:
            return jsonify({'success': False, 'message': 'Factory already deleted'}), 400
        
        from datetime import datetime, timezone
        data = request.get_json(silent=True) or {}
        deleted_at = None
        client_deleted_at = data.get('deleted_at_client')
        if client_deleted_at:
            try:
                parsed = datetime.fromisoformat(client_deleted_at.replace('Z', '+00:00'))
                if parsed.tzinfo is not None:
                    deleted_at = parsed.astimezone(timezone.utc).replace(tzinfo=None)
            except ValueError:
                current_app.logger.warning("Invalid client deletion timestamp: %s", client_deleted_at)

        factory.is_deleted = True
        factory.deleted_at = deleted_at or datetime.utcnow()
        factory.deleted_by_admin_id = current_user.id
        db.session.commit()
        
        current_app.logger.info(
            f"Admin '{current_user.username}' deleted factory '{factory.name}' (id={factory.id})"
        )
        
        return jsonify({
            'success': True,
            'message': f'Factory "{factory.name}" deleted',
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete factory {factory_id}: {e}")
        return jsonify({'success': False, 'message': 'Operation failed'}), 500


@bp.route('/api/admin/user/<int:user_id>/ban', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def admin_ban_user(user_id):
    """Ban a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.is_admin:
            return jsonify({'success': False, 'message': 'Cannot ban admin users'}), 400
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'Cannot ban yourself'}), 400
        if user.is_banned:
            return jsonify({'success': False, 'message': 'User already banned'}), 400
        
        from datetime import datetime
        user.is_banned = True
        user.banned_at = datetime.utcnow()
        user.banned_by = current_user.id
        db.session.commit()
        
        current_app.logger.info(
            f"Admin '{current_user.username}' banned user '{user.username}'"
        )
        
        return jsonify({
            'success': True,
            'message': f'User "{user.username}" banned'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to ban user {user_id}: {e}")
        return jsonify({'success': False, 'message': 'Operation failed'}), 500


@bp.route('/api/admin/user/<int:user_id>/unban', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def admin_unban_user(user_id):
    """Unban a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        if not user.is_banned:
            return jsonify({'success': False, 'message': 'User is not banned'}), 400
        
        user.is_banned = False
        user.banned_at = None
        user.banned_by = None
        db.session.commit()
        
        current_app.logger.info(
            f"Admin '{current_user.username}' unbanned user '{user.username}'"
        )
        
        return jsonify({
            'success': True,
            'message': f'User "{user.username}" unbanned'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to unban user {user_id}: {e}")
        return jsonify({'success': False, 'message': 'Operation failed'}), 500
