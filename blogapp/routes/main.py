# blogapp/routes/main.py
"""
Main routes for PeakShift application
Industrial power cost and carbon optimization system - main routes
"""

import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from blogapp import db, csrf
from blogapp.models import User, Factory

# Create blueprint
bp = Blueprint('main', __name__)


# ============================================================
# Base page routes
# ============================================================

@bp.route('/')
@bp.route('/index')
def index():
    """Home page - redirect to authentication page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.auth_page'))


@bp.route('/dashboard')
@login_required
def dashboard():
    """Main application page - single-page application"""
    import time
    return render_template('dashboard.html', cache_bust=int(time.time()))


# ============================================================
# Factory management routes (TODO)
# ============================================================

@bp.route('/api/factories', methods=['GET'])
@login_required
@csrf.exempt
def get_factories():
    """API: fetch user factory list"""
    factories = Factory.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'success': True,
        'factories': [{
            'id': f.id,
            'name': f.name,
            'location': f.location,
            'industry_type': f.industry_type,
            'voltage_level': f.voltage_level,
            'transformer_capacity': f.transformer_capacity,
            'capacity_fee': f.capacity_fee,
            'daily_usage': f.daily_usage,
            'working_days_per_month': f.working_days_per_month,
            'monthly_usage': f.monthly_usage,
            'work_periods': f.work_periods,
            'created_at': f.created_at.strftime('%Y-%m-%d')
        } for f in factories]
    })


@bp.route('/api/factory/create', methods=['POST'])
@login_required
@csrf.exempt
def create_factory():
    """API: Create factory"""
    data = request.get_json()
    
    try:
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'Factory name cannot be empty'
            }), 400
        
        if not data.get('voltage_level'):
            return jsonify({
                'success': False,
                'message': 'Voltage level cannot be empty'
            }), 400
        
        if not data.get('transformer_capacity'):
            return jsonify({
                'success': False,
                'message': 'Transformer capacity cannot be empty'
            }), 400
        
        if not data.get('daily_usage'):
            return jsonify({
                'success': False,
                'message': 'Daily usage cannot be empty'
            }), 400
        
        if not data.get('work_periods'):
            return jsonify({
                'success': False,
                'message': 'Work periods cannot be empty'
            }), 400
        
        # Validate if voltage level is valid
        voltage_level = int(data.get('voltage_level'))
        if voltage_level not in [10, 35, 110, 220]:
            return jsonify({
                'success': False,
                'message': 'Voltage level must be one of 10, 35, 110, or 220 kV'
            }), 400
        
        # Process numeric fields
        transformer_capacity = float(data.get('transformer_capacity'))
        daily_usage = float(data.get('daily_usage'))
        working_days_per_month = int(data.get('working_days_per_month', 26))
        
        # Validate work periods format
        work_periods = data.get('work_periods')
        if isinstance(work_periods, str):
            import json
            work_periods = json.loads(work_periods)
        
        if not isinstance(work_periods, list) or len(work_periods) == 0:
            return jsonify({
                'success': False,
                'message': 'Please add at least one work period'
            }), 400
        
        factory = Factory(
            name=data.get('name').strip(),
            location=data.get('location', '').strip() if data.get('location') else None,
            industry_type=data.get('industry_type', '').strip() if data.get('industry_type') else None,
            voltage_level=voltage_level,
            transformer_capacity=transformer_capacity,
            daily_usage=daily_usage,
            working_days_per_month=working_days_per_month,
            work_periods=data.get('work_periods') if isinstance(data.get('work_periods'), str) else json.dumps(work_periods),
            user_id=current_user.id
        )
        
        db.session.add(factory)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Factory created successfully',
            'factory': {
                'id': factory.id,
                'name': factory.name,
                'location': factory.location,
                'industry_type': factory.industry_type,
                'voltage_level': factory.voltage_level,
                'transformer_capacity': factory.transformer_capacity,
                'capacity_fee': factory.capacity_fee,
                'daily_usage': factory.daily_usage,
                'working_days_per_month': factory.working_days_per_month,
                'monthly_usage': factory.monthly_usage,
                'work_periods': factory.work_periods,
                'created_at': factory.created_at.strftime('%Y-%m-%d')
            }
        })
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Data format error: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Creation failed: {str(e)}'
        }), 400


@bp.route('/api/factory/<int:factory_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_factory(factory_id):
    """API: Delete factory"""
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': 'Factory not found or unauthorized'
        }), 404
    
    try:
        db.session.delete(factory)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Factory deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Deletion failed: {str(e)}'
        }), 400


@bp.route('/api/factory/<int:factory_id>', methods=['PUT'])
@login_required
@csrf.exempt
def update_factory(factory_id):
    """API: Update factory"""
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': 'Factory not found or unauthorized'
        }), 404
    
    data = request.get_json()
    
    try:
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'Factory name cannot be empty'
            }), 400
        
        if not data.get('voltage_level'):
            return jsonify({
                'success': False,
                'message': 'Voltage level cannot be empty'
            }), 400
        
        if not data.get('transformer_capacity'):
            return jsonify({
                'success': False,
                'message': 'Transformer capacity cannot be empty'
            }), 400
        
        if not data.get('daily_usage'):
            return jsonify({
                'success': False,
                'message': 'Daily usage cannot be empty'
            }), 400
        
        if not data.get('work_periods'):
            return jsonify({
                'success': False,
                'message': 'Work periods cannot be empty'
            }), 400
        
        # Validate if voltage level is valid
        voltage_level = int(data.get('voltage_level'))
        if voltage_level not in [10, 35, 110, 220]:
            return jsonify({
                'success': False,
                'message': 'Voltage level must be one of 10, 35, 110, or 220 kV'
            }), 400
        
        # Validate work periods format
        work_periods = data.get('work_periods')
        if isinstance(work_periods, str):
            work_periods = json.loads(work_periods)
        
        if not isinstance(work_periods, list) or len(work_periods) == 0:
            return jsonify({
                'success': False,
                'message': 'Please add at least one work period'
            }), 400
        
        # Update factory information
        factory.name = data.get('name').strip()
        factory.location = data.get('location', '').strip() if data.get('location') else None
        factory.industry_type = data.get('industry_type', '').strip() if data.get('industry_type') else None
        factory.voltage_level = voltage_level
        factory.transformer_capacity = float(data.get('transformer_capacity'))
        factory.daily_usage = float(data.get('daily_usage'))
        factory.working_days_per_month = int(data.get('working_days_per_month', 26))
        factory.work_periods = data.get('work_periods') if isinstance(data.get('work_periods'), str) else json.dumps(work_periods)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Factory updated successfully',
            'factory': {
                'id': factory.id,
                'name': factory.name,
                'location': factory.location,
                'industry_type': factory.industry_type,
                'voltage_level': factory.voltage_level,
                'transformer_capacity': factory.transformer_capacity,
                'capacity_fee': factory.capacity_fee,
                'daily_usage': factory.daily_usage,
                'working_days_per_month': factory.working_days_per_month,
                'monthly_usage': factory.monthly_usage,
                'work_periods': factory.work_periods,
                'created_at': factory.created_at.strftime('%Y-%m-%d')
            }
        })
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Data format error: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Update failed: {str(e)}'
        }), 400


# ============================================================
# Factory details and electricity cost routes
# ============================================================

@bp.route('/api/factory/<int:factory_id>/details', methods=['GET'])
@login_required
@csrf.exempt
def get_factory_details(factory_id):
    """API: Fetch factory details and electricity cost results"""
    from blogapp.services.electricity_cost import ElectricityCostCalculator
    from blogapp.models import HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
    
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': 'Factory not found or unauthorized'
        }), 404
    
    try:
        # Use electricity cost calculator
        calculator = ElectricityCostCalculator(factory_id)
        cost_result = calculator.calculate_monthly_cost()
        
        # Fetch supplier hourly prices (including 0.01 agent fee)
        hourly_prices = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
        agent_prices = {p.hour: round(p.price + 0.01, 4) for p in hourly_prices}
        
        # Fetch grid price based on factory voltage level
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=factory.voltage_level).first()
        
        # Fetch time-of-use periods
        tou_periods = TimeOfUsePeriod.query.order_by(TimeOfUsePeriod.hour).all()
        tou_map = {p.hour: p.period_type for p in tou_periods}
        
        # Build 24-hour grid price data
        grid_prices = {}
        if grid_price:
            for hour in range(24):
                period_type = tou_map.get(hour, 'Normal')
                if period_type == 'Peak':
                    grid_prices[hour] = grid_price.peak_price
                elif period_type == 'Valley':
                    grid_prices[hour] = grid_price.valley_price
                else:
                    grid_prices[hour] = grid_price.normal_price
        
        # Add price comparison data to return result
        cost_result['price_comparison'] = {
            'agent_prices': agent_prices,
            'grid_prices': grid_prices
        }
        
        # Add carbon emission data (using teammate's carbon_emission property)
        cost_result['carbon_emission'] = factory.carbon_emission
        
        return jsonify({
            'success': True,
            'factory': {
                'id': factory.id,
                'name': factory.name,
                'location': factory.location,
                'industry_type': factory.industry_type,
                'voltage_level': factory.voltage_level,
                'transformer_capacity': factory.transformer_capacity,
                'daily_usage': factory.daily_usage,
                'working_days_per_month': factory.working_days_per_month,
                'work_periods': factory.work_periods,
                'created_at': factory.created_at.strftime('%Y-%m-%d')
            },
            'cost_analysis': cost_result
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Calculation failed: {str(e)}'
        }), 400


# ============================================================
# Supplier optimization and saving potential API
# ============================================================

@bp.route('/api/factory/<int:factory_id>/optimization', methods=['GET'])
@login_required
@csrf.exempt
def get_optimization(factory_id):
    """API: Fetch saving potential (cost/carbon mode)"""
    from blogapp.services.supplier_optimizer import SupplierOptimizer
    from blogapp.models import HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
    
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': 'Factory not found or unauthorized'
        }), 404
    
    # Get optimization mode parameters
    mode = request.args.get('mode', 'cost')
    if mode not in ['cost', 'carbon']:
        return jsonify({
            'success': False,
            'message': 'Invalid optimization mode; must be cost or carbon'
        }), 400
    
    try:
        # Get necessary data
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=factory.voltage_level).first()
        supplier_prices = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
        tou_periods = TimeOfUsePeriod.query.order_by(TimeOfUsePeriod.hour).all()
        
        if not grid_price:
            return jsonify({
                'success': False,
                'message': f'Grid price data not found for voltage level {factory.voltage_level} kV'
            }), 404
        
        if not supplier_prices:
            return jsonify({
                'success': False,
                'message': 'Supplier price data not found'
            }), 404
        
        # Create optimizer
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        # Get saving potential
        result = optimizer.get_saving_potential(mode=mode)
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Optimization calculation failed: {str(e)}'
        }), 400


@bp.route('/api/factory/<int:factory_id>/suggestions', methods=['GET'])
@login_required
@csrf.exempt
def get_suggestions(factory_id):
    """API: Fetch optimization suggestions"""
    from blogapp.services.supplier_optimizer import SupplierOptimizer
    from blogapp.models import HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
    
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': 'Factory not found or unauthorized'
        }), 404
    
    try:
        # Get necessary data
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=factory.voltage_level).first()
        supplier_prices = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
        tou_periods = TimeOfUsePeriod.query.order_by(TimeOfUsePeriod.hour).all()
        
        if not grid_price:
            return jsonify({
                'success': False,
                'message': f'Grid price data not found for voltage level {factory.voltage_level} kV'
            }), 404
        
        if not supplier_prices:
            return jsonify({
                'success': False,
                'message': 'Supplier price data not found'
            }), 404
        
        # Create optimizer
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        # Get optimization suggestions
        result = optimizer.get_suggestions()
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Suggestion generation failed: {str(e)}'
        }), 400


# ============================================================
# Electricity usage data management routes (TODO)
# ============================================================

@bp.route('/electricity/log', methods=['GET', 'POST'])
@login_required
def log_electricity():
    """Record electricity usage data - TODO"""
    # TODO: Implement electricity usage data recording function
    return jsonify({'message': 'Log electricity usage - Under development'})


@bp.route('/electricity/history')
@login_required
def electricity_history():
    """Electricity usage history - TODO"""
    # TODO: Display electricity usage history data
    return jsonify({'message': 'Electricity history - Under development'})


# ============================================================
# Carbon emissions analysis routes (TODO)
# ============================================================

@bp.route('/carbon/analysis')
@login_required
def carbon_analysis():
    """Carbon emissions analysis page - TODO"""
    # TODO: Implement carbon emissions analysis function
    return jsonify({'message': 'Carbon analysis - Under development'})


@bp.route('/carbon/report')
@login_required
def carbon_report():
    """Carbon emissions report - TODO"""
    # TODO: Generate carbon emissions report
    return jsonify({'message': 'Carbon report - Under development'})


# ============================================================
# Electricity cost optimization suggestions routes (TODO)
# ============================================================

@bp.route('/optimization/suggestions')
@login_required
def optimization_suggestions():
    """Electricity cost optimization suggestions - TODO"""
    # TODO: Provide optimization suggestions based on time-of-use pricing
    return jsonify({'message': 'Optimization suggestions - Under development'})


@bp.route('/optimization/schedule')
@login_required
def production_schedule():
    """Production time adjustment suggestions - TODO"""
    # TODO: Provide production time adjustment suggestions
    return jsonify({'message': 'Production schedule - Under development'})


# ============================================================
# API routes (TODO)
# ============================================================

@bp.route('/api/electricity/data')
@login_required
def api_electricity_data():
    """API: Fetch electricity usage data - TODO"""
    # TODO: Return electricity usage data JSON
    return jsonify({'data': [], 'message': 'Under development'})


@bp.route('/api/carbon/data')
@login_required
def api_carbon_data():
    """API: Fetch carbon emissions data - TODO"""
    # TODO: Return carbon emissions data JSON
    return jsonify({'data': [], 'message': 'Under development'})


# ============================================================
# Error handling
# ============================================================

@bp.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return jsonify({'error': 'Page not found'}), 404


@bp.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500
