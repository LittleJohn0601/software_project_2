# blogapp/routes/main.py
"""
Main routes for PeakShift application
工业用电成本与碳排放分析优化系统 - 主路由
"""

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
    return render_template('dashboard.html')


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
            'monthly_usage': f.monthly_usage,
            'monthly_cost': f.monthly_cost,
            'carbon_emission': f.carbon_emission,
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
        
        # 处理数值字段，空字符串转为 0
        monthly_usage = data.get('monthly_usage')
        monthly_cost = data.get('monthly_cost')
        carbon_emission = data.get('carbon_emission')
        
        # 转换为浮点数，如果为空或空字符串则设为 0
        monthly_usage = float(monthly_usage) if monthly_usage and str(monthly_usage).strip() else 0
        monthly_cost = float(monthly_cost) if monthly_cost and str(monthly_cost).strip() else 0
        carbon_emission = float(carbon_emission) if carbon_emission and str(carbon_emission).strip() else 0
        
        factory = Factory(
            name=data.get('name').strip(),
            location=data.get('location', '').strip() if data.get('location') else None,
            industry_type=data.get('industry_type', '').strip() if data.get('industry_type') else None,
            monthly_usage=monthly_usage,
            monthly_cost=monthly_cost,
            carbon_emission=carbon_emission,
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
                'monthly_usage': factory.monthly_usage,
                'monthly_cost': factory.monthly_cost,
                'carbon_emission': factory.carbon_emission,
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
