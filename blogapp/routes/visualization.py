from flask import Blueprint, jsonify
from blogapp.impact_calculator import ImpactCalculator

# Create Blueprint for visualization routes
bp = Blueprint('visualization', __name__)

@bp.route('/impact/campus_live')
def campus_live_impact():
    """Return campus-wide impact data as JSON"""
    calculator = ImpactCalculator()
    return jsonify(calculator.calculate_campus_impact())

@bp.route('/impact/user/<int:user_id>')
def user_impact(user_id):
    """Return user-specific impact data as JSON"""
    calculator = ImpactCalculator()
    return jsonify(calculator.calculate_user_impact(user_id))