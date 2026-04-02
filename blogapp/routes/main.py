# blogapp/routes/main.py
"""
Main routes for PeakShift application
工业用电成本与碳排放分析优化系统 - 主路由
"""

import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from blogapp import db, csrf
from blogapp.models import User, Factory

# 创建蓝图
bp = Blueprint('main', __name__)


# ============================================================
# 基础页面路由
# ============================================================

@bp.route('/')
@bp.route('/index')
def index():
    """首页 - 重定向到统一认证页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.auth_page'))


@bp.route('/dashboard')
@login_required
def dashboard():
    """主应用页面 - 单页应用"""
    import time
    return render_template('dashboard.html', cache_bust=int(time.time()))


# ============================================================
# 工厂管理路由 (待实现)
# ============================================================

@bp.route('/api/factories', methods=['GET'])
@login_required
@csrf.exempt
def get_factories():
    """API: 获取用户的工厂列表"""
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
    """API: 创建工厂"""
    data = request.get_json()
    
    try:
        # 验证必填字段
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': '工厂名称不能为空'
            }), 400
        
        if not data.get('voltage_level'):
            return jsonify({
                'success': False,
                'message': '电压等级不能为空'
            }), 400
        
        if not data.get('transformer_capacity'):
            return jsonify({
                'success': False,
                'message': '变压器容量不能为空'
            }), 400
        
        if not data.get('daily_usage'):
            return jsonify({
                'success': False,
                'message': '日用电量不能为空'
            }), 400
        
        if not data.get('work_periods'):
            return jsonify({
                'success': False,
                'message': '工作时间段不能为空'
            }), 400
        
        # 验证电压等级是否有效
        voltage_level = int(data.get('voltage_level'))
        if voltage_level not in [10, 35, 110, 220]:
            return jsonify({
                'success': False,
                'message': '电压等级必须是 10、35、110 或 220 kV'
            }), 400
        
        # 处理数值字段
        transformer_capacity = float(data.get('transformer_capacity'))
        daily_usage = float(data.get('daily_usage'))
        working_days_per_month = int(data.get('working_days_per_month', 26))
        
        # 验证工作时间段格式
        work_periods = data.get('work_periods')
        if isinstance(work_periods, str):
            import json
            work_periods = json.loads(work_periods)
        
        if not isinstance(work_periods, list) or len(work_periods) == 0:
            return jsonify({
                'success': False,
                'message': '请至少添加一个工作时间段'
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
            'message': '工厂创建成功',
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
            'message': f'数据格式错误: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'创建失败: {str(e)}'
        }), 400


@bp.route('/api/factory/<int:factory_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_factory(factory_id):
    """API: 删除工厂"""
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': '工厂不存在或无权限'
        }), 404
    
    try:
        db.session.delete(factory)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '工厂删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 400


@bp.route('/api/factory/<int:factory_id>', methods=['PUT'])
@login_required
@csrf.exempt
def update_factory(factory_id):
    """API: 更新工厂"""
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': '工厂不存在或无权限'
        }), 404
    
    data = request.get_json()
    
    try:
        # 验证必填字段
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': '工厂名称不能为空'
            }), 400
        
        if not data.get('voltage_level'):
            return jsonify({
                'success': False,
                'message': '电压等级不能为空'
            }), 400
        
        if not data.get('transformer_capacity'):
            return jsonify({
                'success': False,
                'message': '变压器容量不能为空'
            }), 400
        
        if not data.get('daily_usage'):
            return jsonify({
                'success': False,
                'message': '日用电量不能为空'
            }), 400
        
        if not data.get('work_periods'):
            return jsonify({
                'success': False,
                'message': '工作时间段不能为空'
            }), 400
        
        # 验证电压等级是否有效
        voltage_level = int(data.get('voltage_level'))
        if voltage_level not in [10, 35, 110, 220]:
            return jsonify({
                'success': False,
                'message': '电压等级必须是 10、35、110 或 220 kV'
            }), 400
        
        # 验证工作时间段格式
        work_periods = data.get('work_periods')
        if isinstance(work_periods, str):
            work_periods = json.loads(work_periods)
        
        if not isinstance(work_periods, list) or len(work_periods) == 0:
            return jsonify({
                'success': False,
                'message': '请至少添加一个工作时间段'
            }), 400
        
        # 更新工厂信息
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
            'message': '工厂更新成功',
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
            'message': f'数据格式错误: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 400


# ============================================================
# 工厂详情和电费计算路由
# ============================================================

@bp.route('/api/factory/<int:factory_id>/details', methods=['GET'])
@login_required
@csrf.exempt
def get_factory_details(factory_id):
    """API: 获取工厂详情和电费计算结果"""
    from blogapp.services.electricity_cost import ElectricityCostCalculator
    from blogapp.models import HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
    
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': '工厂不存在或无权限'
        }), 404
    
    try:
        # 使用电费计算器
        calculator = ElectricityCostCalculator(factory_id)
        cost_result = calculator.calculate_monthly_cost()
        
        # 获取代理公司24小时电价（加上0.01代理费）
        hourly_prices = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
        agent_prices = {p.hour: round(p.price + 0.01, 4) for p in hourly_prices}
        
        # 获取电网价格（根据工厂电压等级）
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=factory.voltage_level).first()
        
        # 获取分时时段
        tou_periods = TimeOfUsePeriod.query.order_by(TimeOfUsePeriod.hour).all()
        tou_map = {p.hour: p.period_type for p in tou_periods}
        
        # 构建24小时电网价格数据
        grid_prices = {}
        if grid_price:
            for hour in range(24):
                period_type = tou_map.get(hour, '平时')
                if period_type == '高峰':
                    grid_prices[hour] = grid_price.peak_price
                elif period_type == '低谷':
                    grid_prices[hour] = grid_price.valley_price
                else:
                    grid_prices[hour] = grid_price.normal_price
        
        # 添加价格对比数据到返回结果
        cost_result['price_comparison'] = {
            'agent_prices': agent_prices,
            'grid_prices': grid_prices
        }
        
        # 添加碳排放数据（使用队友写的 carbon_emission 属性）
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
            'message': f'计算失败: {str(e)}'
        }), 400


# ============================================================
# 供应商优化和节省潜力 API
# ============================================================

@bp.route('/api/factory/<int:factory_id>/optimization', methods=['GET'])
@login_required
@csrf.exempt
def get_optimization(factory_id):
    """API: 获取节省潜力（省钱/减排模式）"""
    from blogapp.services.supplier_optimizer import SupplierOptimizer
    from blogapp.models import HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
    
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': '工厂不存在或无权限'
        }), 404
    
    # 获取优化模式参数
    mode = request.args.get('mode', 'cost')
    if mode not in ['cost', 'carbon']:
        return jsonify({
            'success': False,
            'message': '无效的优化模式，必须是 cost 或 carbon'
        }), 400
    
    try:
        # 获取必要的数据
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=factory.voltage_level).first()
        supplier_prices = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
        tou_periods = TimeOfUsePeriod.query.order_by(TimeOfUsePeriod.hour).all()
        
        if not grid_price:
            return jsonify({
                'success': False,
                'message': f'未找到电压等级 {factory.voltage_level} kV 的电网价格数据'
            }), 404
        
        if not supplier_prices:
            return jsonify({
                'success': False,
                'message': '未找到售电公司价格数据'
            }), 404
        
        # 创建优化器
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        # 获取节省潜力
        result = optimizer.get_saving_potential(mode=mode)
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'优化计算失败: {str(e)}'
        }), 400


@bp.route('/api/factory/<int:factory_id>/suggestions', methods=['GET'])
@login_required
@csrf.exempt
def get_suggestions(factory_id):
    """API: 获取优化建议"""
    from blogapp.services.supplier_optimizer import SupplierOptimizer
    from blogapp.models import HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
    
    factory = Factory.query.filter_by(id=factory_id, user_id=current_user.id).first()
    
    if not factory:
        return jsonify({
            'success': False,
            'message': '工厂不存在或无权限'
        }), 404
    
    try:
        # 获取必要的数据
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=factory.voltage_level).first()
        supplier_prices = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
        tou_periods = TimeOfUsePeriod.query.order_by(TimeOfUsePeriod.hour).all()
        
        if not grid_price:
            return jsonify({
                'success': False,
                'message': f'未找到电压等级 {factory.voltage_level} kV 的电网价格数据'
            }), 404
        
        if not supplier_prices:
            return jsonify({
                'success': False,
                'message': '未找到售电公司价格数据'
            }), 404
        
        # 创建优化器
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        # 获取优化建议
        result = optimizer.get_suggestions()
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'生成建议失败: {str(e)}'
        }), 400


# ============================================================
# 用电数据管理路由 (待实现)
# ============================================================

@bp.route('/electricity/log', methods=['GET', 'POST'])
@login_required
def log_electricity():
    """记录用电数据 - 待实现"""
    # TODO: 实现用电数据记录功能
    return jsonify({'message': 'Log electricity usage - Under development'})


@bp.route('/electricity/history')
@login_required
def electricity_history():
    """用电历史记录 - 待实现"""
    # TODO: 显示用电历史数据
    return jsonify({'message': 'Electricity history - Under development'})


# ============================================================
# 碳排放分析路由 (待实现)
# ============================================================

@bp.route('/carbon/analysis')
@login_required
def carbon_analysis():
    """碳排放分析页面 - 待实现"""
    # TODO: 实现碳排放分析功能
    return jsonify({'message': 'Carbon analysis - Under development'})


@bp.route('/carbon/report')
@login_required
def carbon_report():
    """碳排放报告 - 待实现"""
    # TODO: 生成碳排放报告
    return jsonify({'message': 'Carbon report - Under development'})


# ============================================================
# 电费优化建议路由 (待实现)
# ============================================================

@bp.route('/optimization/suggestions')
@login_required
def optimization_suggestions():
    """电费优化建议 - 待实现"""
    # TODO: 根据分时电价提供优化建议
    return jsonify({'message': 'Optimization suggestions - Under development'})


@bp.route('/optimization/schedule')
@login_required
def production_schedule():
    """生产时间调整建议 - 待实现"""
    # TODO: 提供生产时间调整建议
    return jsonify({'message': 'Production schedule - Under development'})


# ============================================================
# API 路由 (待实现)
# ============================================================

@bp.route('/api/electricity/data')
@login_required
def api_electricity_data():
    """API: 获取用电数据 - 待实现"""
    # TODO: 返回用电数据 JSON
    return jsonify({'data': [], 'message': 'Under development'})


@bp.route('/api/carbon/data')
@login_required
def api_carbon_data():
    """API: 获取碳排放数据 - 待实现"""
    # TODO: 返回碳排放数据 JSON
    return jsonify({'data': [], 'message': 'Under development'})


# ============================================================
# 错误处理
# ============================================================

@bp.errorhandler(404)
def not_found_error(error):
    """404 错误处理"""
    return jsonify({'error': 'Page not found'}), 404


@bp.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500
