# blogapp/services/supplier_optimizer.py
"""
供应商优化器 - 选择最优电力供应商并优化用电时间

输入：
- 电网价格曲线
- 售电公司价格曲线  
- 用户用电需求

约束：
- 只能选一个供应商（短期内）
- 售电价格 ≤ 电网 × 1.6

输出：
- 最优供应商选择
- 最优用电时间安排
- 成本 & 碳排放
"""

import json
from typing import Dict, List, Any, Tuple, Optional


class SupplierType:
    """供应商类型常量"""
    GRID = "grid"
    SUPPLIER = "supplier"


class SupplierOptimizer:
    """供应商优化器"""
    
    def __init__(self, factory, grid_price, supplier_prices, tou_periods):
        """
        初始化优化器
        
        Args:
            factory: 工厂对象
            grid_price: 电网价格对象 (GridElectricityPrice)
            supplier_prices: 售电公司价格列表 (HourlyElectricityPrice)
            tou_periods: 分时时段列表 (TimeOfUsePeriod)
        """
        self.factory = factory
        self.grid_price = grid_price
        self.supplier_prices_list = supplier_prices
        self.tou_periods_list = tou_periods
        
        # 约束条件：售电价格 ≤ 电网价格 × 1.6
        self.price_constraint_ratio = 1.6
        
        # 解析工作时间段
        self.work_periods = self._parse_work_periods()
        self.total_work_hours = self._calculate_total_work_hours()
        self.hourly_usage = self._calculate_hourly_usage()
        
        # 缓存映射
        self._grid_hourly_prices = None
        self._supplier_hourly_prices = None
        self._carbon_factors = None
        self._tou_map = None
    
    def _parse_work_periods(self) -> List[Dict]:
        """解析工作时间段 JSON"""
        try:
            if isinstance(self.factory.work_periods, str):
                return json.loads(self.factory.work_periods)
            return self.factory.work_periods
        except (json.JSONDecodeError, TypeError):
            return [{"start": 8, "end": 18}]
    
    def _calculate_total_work_hours(self) -> int:
        """计算总工作小时数"""
        total = 0
        for period in self.work_periods:
            total += period.get('end', 0) - period.get('start', 0)
        return max(total, 1)
    
    def _calculate_hourly_usage(self) -> float:
        """计算每小时用电量 (kWh/小时)"""
        if self.total_work_hours > 0:
            return self.factory.daily_usage / self.total_work_hours
        return 0
    
    def _get_tou_map(self) -> Dict[int, str]:
        """获取小时到时段的映射"""
        if self._tou_map is None:
            self._tou_map = {}
            for tp in self.tou_periods_list:
                self._tou_map[tp.hour] = tp.period_type
        return self._tou_map
    
    def get_grid_hourly_prices(self) -> Dict[int, float]:
        """获取电网公司的分时电价"""
        if self._grid_hourly_prices is None:
            self._grid_hourly_prices = {}
            tou_map = self._get_tou_map()
            
            for hour in range(24):
                period_type = tou_map.get(hour, 'normal')
                if period_type == 'peak':
                    price = self.grid_price.peak_price if self.grid_price else 0
                elif period_type == 'valley':
                    price = self.grid_price.valley_price if self.grid_price else 0
                else:
                    price = self.grid_price.normal_price if self.grid_price else 0
                self._grid_hourly_prices[hour] = price
        return self._grid_hourly_prices
    
    def get_supplier_hourly_prices(self) -> Dict[int, float]:
        """获取售电公司的分时电价"""
        if self._supplier_hourly_prices is None:
            self._supplier_hourly_prices = {}
            for hp in self.supplier_prices_list:
                self._supplier_hourly_prices[hp.hour] = hp.price
        return self._supplier_hourly_prices
    
    def get_carbon_factors(self) -> Dict[int, float]:
        """获取各小时的碳排放因子 (kg CO₂/kWh)"""
        if self._carbon_factors is None:
            self._carbon_factors = {}
            tou_map = self._get_tou_map()
            
            for hour in range(24):
                period_type = tou_map.get(hour, 'normal')
                if period_type == 'peak':
                    self._carbon_factors[hour] = 0.75
                elif period_type == 'valley':
                    self._carbon_factors[hour] = 0.55
                else:
                    self._carbon_factors[hour] = 0.65
        return self._carbon_factors
    
    def check_supplier_price_constraint(self) -> bool:
        """检查售电公司价格是否满足约束：售电价格 ≤ 电网价格 × 1.6"""
        grid_prices = self.get_grid_hourly_prices()
        supplier_prices = self.get_supplier_hourly_prices()
        
        for hour in range(24):
            supplier_price = supplier_prices.get(hour, 0)
            grid_price = grid_prices.get(hour, 0)
            max_allowed = grid_price * self.price_constraint_ratio
            
            if supplier_price > max_allowed:
                return False
        return True
    
    def _calculate_cost_with_schedule(self, supplier: str, schedule: List[int]) -> float:
        """计算给定供应商和用电安排的总成本"""
        total_cost = 0
        monthly_work_days = self.factory.working_days_per_month
        
        grid_prices = self.get_grid_hourly_prices()
        supplier_prices = self.get_supplier_hourly_prices()
        
        for hour, is_working in enumerate(schedule):
            if not is_working:
                continue
            
            hourly_energy = self.hourly_usage
            
            if supplier == SupplierType.GRID:
                price = grid_prices.get(hour, 0)
            else:
                price = supplier_prices.get(hour, 0)
            
            daily_cost = hourly_energy * price
            total_cost += daily_cost * monthly_work_days
        
        # 加上容量电费
        total_cost += self.factory.capacity_fee
        
        return total_cost
    
    def _calculate_carbon_with_schedule(self, schedule: List[int]) -> float:
        """计算给定用电安排的碳排放"""
        total_carbon = 0
        monthly_work_days = self.factory.working_days_per_month
        carbon_factors = self.get_carbon_factors()
        
        for hour, is_working in enumerate(schedule):
            if not is_working:
                continue
            
            hourly_energy = self.hourly_usage
            carbon_factor = carbon_factors.get(hour, 0.6634)
            
            daily_carbon = hourly_energy * carbon_factor
            total_carbon += daily_carbon * monthly_work_days
        
        return round(total_carbon, 2)
    
    def _generate_optimal_schedule(self, supplier: str, objective: str = 'cost') -> Tuple[List[int], float, float]:
        """生成最优用电时间安排"""
        needed_hours = self.total_work_hours
        
        if objective == 'cost':
            if supplier == SupplierType.GRID:
                values = self.get_grid_hourly_prices()
            else:
                values = self.get_supplier_hourly_prices()
        else:
            values = self.get_carbon_factors()
        
        # 贪心算法：按值从小到大排序
        hours = list(range(24))
        hours.sort(key=lambda h: values.get(h, float('inf')))
        
        schedule = [0] * 24
        selected_hours = 0
        
        for hour in hours:
            if selected_hours >= needed_hours:
                break
            schedule[hour] = 1
            selected_hours += 1
        
        cost = self._calculate_cost_with_schedule(supplier, schedule)
        carbon = self._calculate_carbon_with_schedule(schedule)
        
        return schedule, cost, carbon
    
    def _get_current_schedule(self) -> List[int]:
        """获取当前的用电安排"""
        schedule = [0] * 24
        for period in self.work_periods:
            for hour in range(period.get('start', 0), period.get('end', 0)):
                if 0 <= hour < 24:
                    schedule[hour] = 1
        return schedule
    
    def _calculate_current_cost(self) -> float:
        """计算当前成本（假设使用电网）"""
        schedule = self._get_current_schedule()
        return self._calculate_cost_with_schedule(SupplierType.GRID, schedule)
    
    def _calculate_current_carbon(self) -> float:
        """计算当前碳排放"""
        schedule = self._get_current_schedule()
        return self._calculate_carbon_with_schedule(schedule)
    
    def optimize(self, objective: str = 'cost') -> Dict[str, Any]:
        """执行完整优化"""
        # 检查售电公司是否有效
        supplier_valid = self.check_supplier_price_constraint()
        
        # 评估两个供应商
        candidates = []
        
        # 电网公司
        grid_schedule, grid_cost, grid_carbon = self._generate_optimal_schedule(
            SupplierType.GRID, objective
        )
        candidates.append({
            'supplier': SupplierType.GRID,
            'supplier_name': '电网公司',
            'cost': grid_cost,
            'carbon': grid_carbon,
            'schedule': grid_schedule,
            'valid': True
        })
        
        # 售电公司
        if supplier_valid:
            sup_schedule, sup_cost, sup_carbon = self._generate_optimal_schedule(
                SupplierType.SUPPLIER, objective
            )
            candidates.append({
                'supplier': SupplierType.SUPPLIER,
                'supplier_name': '售电公司',
                'cost': sup_cost,
                'carbon': sup_carbon,
                'schedule': sup_schedule,
                'valid': True
            })
        else:
            candidates.append({
                'supplier': SupplierType.SUPPLIER,
                'supplier_name': '售电公司',
                'cost': float('inf'),
                'carbon': float('inf'),
                'schedule': None,
                'valid': False,
                'invalid_reason': f'价格超出电网价格 {self.price_constraint_ratio} 倍'
            })
        
        # 选择最优
        if objective == 'cost':
            best = min(candidates, key=lambda x: x['cost'] if x['valid'] else float('inf'))
        else:
            best = min(candidates, key=lambda x: x['carbon'] if x['valid'] else float('inf'))
        
        # 当前值
        current_cost = self._calculate_current_cost()
        current_carbon = self._calculate_current_carbon()
        
        # 节省
        cost_saving = current_cost - best['cost'] if best['cost'] != float('inf') else 0
        carbon_reduction = current_carbon - best['carbon'] if best['carbon'] != float('inf') else 0
        
        # 格式化用电时间
        schedule_hours = []
        if best['schedule']:
            for hour, working in enumerate(best['schedule']):
                if working:
                    schedule_hours.append(f"{hour:02d}:00-{hour+1:02d}:00")
        
        return {
            'success': True,
            'objective': objective,
            'best_supplier': {
                'type': best['supplier'],
                'name': best['supplier_name'],
                'is_valid': best['valid']
            },
            'current': {
                'cost': round(current_cost, 2),
                'carbon': round(current_carbon, 2),
                'unit_cost': '元/月',
                'unit_carbon': 'kg CO₂/月'
            },
            'optimized': {
                'cost': round(best['cost'], 2) if best['cost'] != float('inf') else None,
                'carbon': round(best['carbon'], 2) if best['carbon'] != float('inf') else None,
                'unit_cost': '元/月',
                'unit_carbon': 'kg CO₂/月',
                'schedule': schedule_hours[:10]
            },
            'saving': {
                'cost': round(max(cost_saving, 0), 2),
                'carbon': round(max(carbon_reduction, 0), 2)
            },
            'alternatives': [
                {
                    'supplier': c['supplier_name'],
                    'cost': round(c['cost'], 2) if c['cost'] != float('inf') else None,
                    'carbon': round(c['carbon'], 2) if c['carbon'] != float('inf') else None,
                    'is_valid': c['valid'],
                    'invalid_reason': c.get('invalid_reason')
                }
                for c in candidates
            ]
        }
    
    def get_saving_potential(self, mode: str = 'cost') -> Dict[str, Any]:
        """获取节省潜力"""
        result = self.optimize(mode)
        
        if mode == 'cost':
            value = result['saving']['cost']
            unit = "元/月"
            description = f"通过选择最优供应商和优化用电时段，预计每月可节省 {value:,.2f} 元"
        else:
            value = result['saving']['carbon']
            unit = "kg CO₂/月"
            description = f"通过选择最优供应商和优化用电时段，预计每月可减少 {value:,.2f} kg CO₂ 排放"
        
        return {
            'success': True,
            'mode': mode,
            'saving_potential': {
                'value': value,
                'unit': unit,
                'description': description
            },
            'best_supplier': result['best_supplier']['name'],
            'current_cost': result['current']['cost'],
            'optimized_cost': result['optimized']['cost']
        }
    
    def get_suggestions(self) -> Dict[str, Any]:
        """获取优化建议"""
        result = self.optimize('cost')
        suggestions = []
        
        # 供应商建议
        if result['best_supplier']['type'] == SupplierType.SUPPLIER:
            suggestions.append({
                'title': '切换到售电公司',
                'description': f'售电公司价格更具优势，预计每月可节省 {result["saving"]["cost"]:,.2f} 元',
                'impact': 'high',
                'potential_saving': result['saving']['cost'],
                'potential_carbon_reduction': result['saving']['carbon'],
                'action_items': [
                    '与售电公司签订长期购电协议',
                    '关注售电公司的价格波动',
                    '定期评估供应商性价比'
                ]
            })
        else:
            suggestions.append({
                'title': '保持使用电网公司',
                'description': '当前售电公司价格不符合约束条件（不得超过电网价格1.6倍），建议继续使用电网公司',
                'impact': 'medium',
                'potential_saving': 0,
                'potential_carbon_reduction': 0,
                'action_items': [
                    '关注售电公司价格变化',
                    '等待更优惠的售电公司出现',
                    '考虑参与电力市场交易'
                ]
            })
        
        # 用电时间建议
        optimized_schedule = result['optimized']['schedule']
        current_schedule = self._get_current_schedule()
        current_hours = [h for h, w in enumerate(current_schedule) if w]
        
        new_hours = []
        for hour_str in optimized_schedule:
            hour = int(hour_str[:2])
            if hour not in current_hours:
                new_hours.append(hour_str)
        
        if new_hours:
            suggestions.append({
                'title': '调整用电时间',
                'description': f'建议将部分生产任务调整到电价更低的时段：{", ".join(new_hours[:3])}',
                'impact': 'high' if len(new_hours) > 3 else 'medium',
                'potential_saving': result['saving']['cost'] * 0.6,
                'potential_carbon_reduction': result['saving']['carbon'] * 0.5,
                'action_items': [
                    f'将生产安排在 {"、".join(new_hours[:3])} 等低价时段',
                    '调整生产班次安排',
                    '对可转移负荷进行优化调度'
                ]
            })
        
        return {
            'success': True,
            'suggestions': suggestions
        }
    
    # 属性别名（兼容性）
    @property
    def grid_hourly_prices(self):
        return self.get_grid_hourly_prices()
    
    @property
    def supplier_hourly_prices(self):
        return self.get_supplier_hourly_prices()