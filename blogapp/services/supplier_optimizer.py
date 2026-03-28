# blogapp/services/supplier_optimizer.py
"""
供应商选择与用电优化服务
根据电网价格和售电公司价格，选择最优供应商并优化用电时间
"""

import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import numpy as np


class SupplierType(Enum):
    """供应商类型"""
    GRID = "grid"  # 电网
    RETAIL = "retail"  # 售电公司


@dataclass
class PriceCurve:
    """价格曲线"""
    hour: int  # 小时 (0-23)
    price: float  # 电价 (元/kWh)
    carbon_intensity: float  # 碳排放强度 (gCO₂/kWh)
    
    def __repr__(self):
        return f"{self.hour:02d}:00-{(self.hour+1):02d}:00: {self.price:.4f}元/kWh, {self.carbon_intensity:.1f}gCO₂/kWh"


@dataclass
class SupplierInfo:
    """供应商信息"""
    supplier_type: SupplierType
    name: str
    price_curve: List[PriceCurve]  # 24小时价格曲线
    constraint: float = 1.6  # 售电价格 ≤ 电网 × 1.6


@dataclass
class DemandProfile:
    """用电需求"""
    total_daily_usage: float  # 日总用电量 (kWh)
    flexible_hours: List[int]  # 可灵活调整的时段
    required_hours: List[int]  # 必须用电的时段
    min_work_hours: int  # 最少工作时长
    max_work_hours: int  # 最多工作时长


@dataclass
class OptimizationResult:
    """优化结果"""
    selected_supplier: SupplierType
    supplier_name: str
    hourly_schedule: Dict[int, float]  # 每小时用电量分配
    total_cost: float  # 总成本 (元)
    total_carbon: float  # 总碳排放 (kg)
    average_price: float  # 平均电价 (元/kWh)
    average_carbon: float  # 平均碳排放强度 (gCO₂/kWh)
    cost_saving: float  # 相比电网节省金额
    carbon_reduction: float  # 相比电网碳减排量
    constraint_satisfied: bool  # 约束是否满足
    recommendation: str  # 建议说明


class SupplierOptimizer:
    """供应商选择与用电优化器"""
    
    def __init__(self, grid_price_curve: List[PriceCurve], retail_price_curve: List[PriceCurve]):
        """
        初始化优化器
        
        Args:
            grid_price_curve: 电网价格曲线 (24小时)
            retail_price_curve: 售电公司价格曲线 (24小时)
        """
        self.grid_curve = self._validate_price_curve(grid_price_curve)
        self.retail_curve = self._validate_price_curve(retail_price_curve)
        
        # 验证售电价格约束
        self.retail_constraint_satisfied = self._check_retail_constraint()
        
        # 创建供应商对象
        self.suppliers = {
            SupplierType.GRID: SupplierInfo(
                supplier_type=SupplierType.GRID,
                name="电网公司",
                price_curve=self.grid_curve
            ),
            SupplierType.RETAIL: SupplierInfo(
                supplier_type=SupplierType.RETAIL,
                name="售电公司",
                price_curve=self.retail_curve,
                constraint=1.6
            )
        }
    
    def _validate_price_curve(self, curve: List[PriceCurve]) -> List[PriceCurve]:
        """验证价格曲线完整性"""
        if len(curve) != 24:
            raise ValueError(f"价格曲线必须包含24小时数据，当前只有{len(curve)}小时")
        
        # 按小时排序
        sorted_curve = sorted(curve, key=lambda x: x.hour)
        
        # 验证小时连续性
        for i in range(24):
            if sorted_curve[i].hour != i:
                raise ValueError(f"小时数据不连续，缺少小时{i}")
        
        return sorted_curve
    
    def _check_retail_constraint(self) -> bool:
        """检查售电价格是否满足约束: 售电价格 ≤ 电网 × 1.6"""
        for grid, retail in zip(self.grid_curve, self.retail_curve):
            if retail.price > grid.price * 1.6:
                return False
        return True
    
    def optimize_supplier_selection(self, demand: DemandProfile) -> OptimizationResult:
        """
        选择最优供应商并优化用电时间
        
        Args:
            demand: 用电需求
            
        Returns:
            优化结果
        """
        # 计算两个供应商的最优方案
        grid_result = self._optimize_for_supplier(
            self.suppliers[SupplierType.GRID], demand
        )
        retail_result = self._optimize_for_supplier(
            self.suppliers[SupplierType.RETAIL], demand
        )
        
        # 如果售电公司不满足约束，直接返回电网方案
        if not self.retail_constraint_satisfied:
            return self._create_final_result(
                SupplierType.GRID,
                grid_result,
                retail_result,
                "售电公司价格超出约束条件（售价 > 电网价 × 1.6），建议选择电网公司"
            )
        
        # 比较成本，选择更优的供应商
        if retail_result['total_cost'] < grid_result['total_cost']:
            selected_supplier = SupplierType.RETAIL
            result_data = retail_result
            recommendation = f"售电公司方案成本更低，节省 {grid_result['total_cost'] - retail_result['total_cost']:.2f} 元/天"
        else:
            selected_supplier = SupplierType.GRID
            result_data = grid_result
            recommendation = f"电网公司方案成本更低，节省 {retail_result['total_cost'] - grid_result['total_cost']:.2f} 元/天"
        
        return self._create_final_result(
            selected_supplier,
            result_data,
            None,
            recommendation
        )
    
    def _optimize_for_supplier(self, supplier: SupplierInfo, demand: DemandProfile) -> Dict:
        """
        为特定供应商优化用电时间安排
        
        Args:
            supplier: 供应商信息
            demand: 用电需求
            
        Returns:
            优化结果字典
        """
        # 获取各小时电价
        hourly_prices = [(p.hour, p.price, p.carbon_intensity) for p in supplier.price_curve]
        
        # 分离固定时段和灵活时段
        fixed_schedule = {}
        flexible_hours = []
        
        for hour in range(24):
            if hour in demand.required_hours:
                # 必须用电时段：分配最小用电量
                fixed_schedule[hour] = demand.total_daily_usage / len(demand.required_hours) if demand.required_hours else 0
            elif hour in demand.flexible_hours:
                flexible_hours.append(hour)
        
        # 计算已分配的电量
        allocated_usage = sum(fixed_schedule.values())
        remaining_usage = demand.total_daily_usage - allocated_usage
        
        # 如果剩余电量为负，说明固定时段分配过多
        if remaining_usage < 0:
            # 调整固定时段分配
            for hour in fixed_schedule:
                fixed_schedule[hour] = demand.total_daily_usage / len(demand.required_hours)
            remaining_usage = 0
            flexible_hours = []
        
        # 在灵活时段中优化分配剩余电量
        flexible_schedule = self._optimize_hourly_distribution(
            flexible_hours, 
            hourly_prices,
            remaining_usage,
            demand.min_work_hours - len(demand.required_hours),
            demand.max_work_hours - len(demand.required_hours)
        )
        
        # 合并所有时段的用电安排
        final_schedule = {**fixed_schedule, **flexible_schedule}
        
        # 计算总成本和碳排放
        total_cost = 0
        total_carbon = 0
        
        for hour in range(24):
            usage = final_schedule.get(hour, 0)
            price = hourly_prices[hour][1]
            carbon_intensity = hourly_prices[hour][2]
            
            total_cost += usage * price
            total_carbon += usage * carbon_intensity / 1000  # 转换为 kg
        
        # 计算平均指标
        avg_price = total_cost / demand.total_daily_usage if demand.total_daily_usage > 0 else 0
        avg_carbon = total_carbon / demand.total_daily_usage * 1000 if demand.total_daily_usage > 0 else 0
        
        return {
            'schedule': final_schedule,
            'total_cost': total_cost,
            'total_carbon': total_carbon,
            'average_price': avg_price,
            'average_carbon': avg_carbon,
            'fixed_hours': len(demand.required_hours),
            'flexible_hours': len(flexible_hours)
        }
    
    def _optimize_hourly_distribution(self, 
                                      flexible_hours: List[int],
                                      hourly_prices: List[Tuple[int, float, float]],
                                      total_usage: float,
                                      min_hours: int,
                                      max_hours: int) -> Dict[int, float]:
        """
        优化小时用电分配（贪心算法）
        将用电量优先分配到电价最低的时段
        
        Args:
            flexible_hours: 可调整的小时列表
            hourly_prices: 每小时价格列表 [(hour, price, carbon), ...]
            total_usage: 总用电量
            min_hours: 最少工作时长
            max_hours: 最多工作时长
            
        Returns:
            优化后的用电分配
        """
        if total_usage <= 0 or not flexible_hours:
            return {}
        
        # 获取灵活时段的价格排序
        price_list = [(hour, hourly_prices[hour][1]) for hour in flexible_hours]
        price_list.sort(key=lambda x: x[1])  # 按电价升序排序
        
        # 确定实际使用的小时数
        if min_hours > 0 and min_hours <= len(flexible_hours):
            # 最少需要分配 min_hours 个小时
            hours_to_use = min(max_hours, len(flexible_hours))
            hours_to_use = max(min_hours, hours_to_use)
        else:
            hours_to_use = min(max_hours, len(flexible_hours))
        
        # 如果小时数为0，返回空分配
        if hours_to_use <= 0:
            return {}
        
        # 选择电价最低的 hours_to_use 个小时
        selected_hours = [h for h, _ in price_list[:hours_to_use]]
        
        # 平均分配用电量
        usage_per_hour = total_usage / len(selected_hours)
        
        return {hour: usage_per_hour for hour in selected_hours}
    
    def _create_final_result(self, 
                            selected_supplier: SupplierType,
                            result_data: Dict,
                            alternative_data: Optional[Dict],
                            recommendation: str) -> OptimizationResult:
        """创建最终优化结果"""
        
        # 计算相比电网的节省
        if selected_supplier == SupplierType.GRID:
            cost_saving = 0
            carbon_reduction = 0
        else:
            # 计算如果选择电网的成本
            grid_total_cost = self._calculate_grid_cost(result_data['schedule'])
            grid_total_carbon = self._calculate_grid_carbon(result_data['schedule'])
            cost_saving = grid_total_cost - result_data['total_cost']
            carbon_reduction = grid_total_carbon - result_data['total_carbon']
        
        return OptimizationResult(
            selected_supplier=selected_supplier,
            supplier_name=self.suppliers[selected_supplier].name,
            hourly_schedule=result_data['schedule'],
            total_cost=result_data['total_cost'],
            total_carbon=result_data['total_carbon'],
            average_price=result_data['average_price'],
            average_carbon=result_data['average_carbon'],
            cost_saving=cost_saving,
            carbon_reduction=carbon_reduction,
            constraint_satisfied=self.retail_constraint_satisfied,
            recommendation=recommendation
        )
    
    def _calculate_grid_cost(self, schedule: Dict[int, float]) -> float:
        """计算电网方案的成本"""
        total_cost = 0
        for hour, usage in schedule.items():
            total_cost += usage * self.grid_curve[hour].price
        return total_cost
    
    def _calculate_grid_carbon(self, schedule: Dict[int, float]) -> float:
        """计算电网方案的碳排放"""
        total_carbon = 0
        for hour, usage in schedule.items():
            total_carbon += usage * self.grid_curve[hour].carbon_intensity / 1000
        return total_carbon
    
    def get_comparison_table(self, demand: DemandProfile) -> Dict:
        """获取供应商对比表"""
        grid_result = self._optimize_for_supplier(self.suppliers[SupplierType.GRID], demand)
        retail_result = self._optimize_for_supplier(self.suppliers[SupplierType.RETAIL], demand)
        
        return {
            'grid': {
                'total_cost': grid_result['total_cost'],
                'total_carbon': grid_result['total_carbon'],
                'average_price': grid_result['average_price'],
                'average_carbon': grid_result['average_carbon']
            },
            'retail': {
                'total_cost': retail_result['total_cost'],
                'total_carbon': retail_result['total_carbon'],
                'average_price': retail_result['average_price'],
                'average_carbon': retail_result['average_carbon']
            },
            'comparison': {
                'cost_diff': retail_result['total_cost'] - grid_result['total_cost'],
                'carbon_diff': retail_result['total_carbon'] - grid_result['total_carbon'],
                'better_supplier': 'retail' if retail_result['total_cost'] < grid_result['total_cost'] else 'grid'
            }
        }