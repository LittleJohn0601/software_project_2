# blogapp/services/supplier_optimizer.py
"""
Supplier optimizer - select optimal electricity supplier and optimize usage schedule

Input:
- Grid price curve
- Retail supplier price curve  
- User electricity demand

Constraints:
- Can only choose one supplier (short term)
- Supplier price ≤ grid × 1.6

Output:
- Best supplier selection
- Optimal electricity usage schedule
- Cost & carbon emissions
"""

import json
from typing import Dict, List, Any, Tuple, Optional


class SupplierType:
    """Supplier type constants"""
    GRID = "grid"
    SUPPLIER = "supplier"


class SupplierOptimizer:
    """Supplier optimizer"""
    
    def __init__(self, factory, grid_price, supplier_prices, tou_periods):
        """
        Initialize optimizer
        
        Args:
            factory: Factory object
            grid_price: Grid price object (GridElectricityPrice)
            supplier_prices: Retail supplier price table (HourlyElectricityPrice)
            tou_periods: Time-of-use period list (TimeOfUsePeriod)
        """
        self.factory = factory
        self.grid_price = grid_price
        self.supplier_prices_list = supplier_prices
        self.tou_periods_list = tou_periods
        
        # Constraint: Supplier price ≤ Grid price × 1.6
        self.price_constraint_ratio = 1.6
        
        # Parse work periods
        self.work_periods = self._parse_work_periods()
        self.total_work_hours = self._calculate_total_work_hours()
        self.hourly_usage = self._calculate_hourly_usage()
        
        # Cache mapping
        self._grid_hourly_prices = None
        self._supplier_hourly_prices = None
        self._carbon_factors = None
        self._tou_map = None
    
    def _parse_work_periods(self) -> List[Dict]:
        """Parse work periods JSON"""
        try:
            if isinstance(self.factory.work_periods, str):
                return json.loads(self.factory.work_periods)
            return self.factory.work_periods
        except (json.JSONDecodeError, TypeError):
            return [{"start": 8, "end": 18}]
    
    def _calculate_total_work_hours(self) -> int:
        """Calculate total working hours"""
        total = 0
        for period in self.work_periods:
            total += period.get('end', 0) - period.get('start', 0)
        return max(total, 1)
    
    def _calculate_hourly_usage(self) -> float:
        """Calculate electricity usage per hour (kWh/hour)"""
        if self.total_work_hours > 0:
            return self.factory.daily_usage / self.total_work_hours
        return 0
    
    def _get_tou_map(self) -> Dict[int, str]:
        """Get hour to period mapping"""
        if self._tou_map is None:
            self._tou_map = {}
            for tp in self.tou_periods_list:
                self._tou_map[tp.hour] = tp.period_type
        return self._tou_map
    
    def get_grid_hourly_prices(self) -> Dict[int, float]:
        """Get grid supplier time-of-use prices"""
        if self._grid_hourly_prices is None:
            self._grid_hourly_prices = {}
            tou_map = self._get_tou_map()
            
            for hour in range(24):
                period_type = tou_map.get(hour, 'Normal')
                # Support both Chinese and English
                if period_type in ['peak', 'Peak']:
                    price = self.grid_price.peak_price if self.grid_price else 0
                elif period_type in ['valley', 'Valley']:
                    price = self.grid_price.valley_price if self.grid_price else 0
                else:  # normal, Normal
                    price = self.grid_price.normal_price if self.grid_price else 0
                self._grid_hourly_prices[hour] = price
        return self._grid_hourly_prices
    
    def get_supplier_hourly_prices(self) -> Dict[int, float]:
        """Get retail supplier time-of-use prices"""
        if self._supplier_hourly_prices is None:
            self._supplier_hourly_prices = {}
            for hp in self.supplier_prices_list:
                self._supplier_hourly_prices[hp.hour] = hp.price
        return self._supplier_hourly_prices
    
    def get_carbon_factors(self) -> Dict[int, float]:
        """Get carbon emission factors for each hour (kg CO₂/kWh)"""
        if self._carbon_factors is None:
            self._carbon_factors = {}
            tou_map = self._get_tou_map()
            
            for hour in range(24):
                period_type = tou_map.get(hour, 'Normal')
                # Support both Chinese and English
                if period_type in ['peak', 'Peak']:
                    self._carbon_factors[hour] = 0.75
                elif period_type in ['valley', 'Valley']:
                    self._carbon_factors[hour] = 0.55
                else:  # normal, Normal
                    self._carbon_factors[hour] = 0.65
        return self._carbon_factors
    
    def check_supplier_price_constraint(self) -> bool:
        """Check supplier price meets constraint: supplier price ≤ grid price × 1.6"""
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
        """Calculate total cost for a given supplier and usage schedule"""
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
        
        # Add capacity fee
        total_cost += self.factory.capacity_fee
        
        return total_cost
    
    def _calculate_carbon_with_schedule(self, schedule: List[int]) -> float:
        """Calculate carbon emissions for a given usage schedule"""
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
        """Generate optimal electricity usage schedule"""
        needed_hours = self.total_work_hours
        
        if objective == 'cost':
            if supplier == SupplierType.GRID:
                values = self.get_grid_hourly_prices()
            else:
                values = self.get_supplier_hourly_prices()
        else:
            values = self.get_carbon_factors()
        
        # Greedy algorithm: sort by value ascending
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
        """Get current usage schedule"""
        schedule = [0] * 24
        for period in self.work_periods:
            for hour in range(period.get('start', 0), period.get('end', 0)):
                if 0 <= hour < 24:
                    schedule[hour] = 1
        return schedule
    
    def _calculate_current_cost(self) -> float:
        """Calculate current cost (assuming grid usage)"""
        schedule = self._get_current_schedule()
        return self._calculate_cost_with_schedule(SupplierType.GRID, schedule)
    
    def _calculate_current_carbon(self) -> float:
        """Calculate current carbon emissions"""
        schedule = self._get_current_schedule()
        return self._calculate_carbon_with_schedule(schedule)
    
    def optimize(self, objective: str = 'cost') -> Dict[str, Any]:
        """Execute full optimization"""
        # Check if retail supplier is valid
        supplier_valid = self.check_supplier_price_constraint()
        
        # Evaluate both suppliers
        candidates = []
        
        # Grid supplier
        grid_schedule, grid_cost, grid_carbon = self._generate_optimal_schedule(
            SupplierType.GRID, objective
        )
        candidates.append({
            'supplier': SupplierType.GRID,
            'supplier_name': 'Grid supplier',
            'cost': grid_cost,
            'carbon': grid_carbon,
            'schedule': grid_schedule,
            'valid': True
        })
        
        # Retail supplier
        if supplier_valid:
            sup_schedule, sup_cost, sup_carbon = self._generate_optimal_schedule(
                SupplierType.SUPPLIER, objective
            )
            candidates.append({
                'supplier': SupplierType.SUPPLIER,
                'supplier_name': 'Retail supplier',
                'cost': sup_cost,
                'carbon': sup_carbon,
                'schedule': sup_schedule,
                'valid': True
            })
        else:
            candidates.append({
                'supplier': SupplierType.SUPPLIER,
                'supplier_name': 'Retail supplier',
                'cost': float('inf'),
                'carbon': float('inf'),
                'schedule': None,
                'valid': False,
                'invalid_reason': f'Price exceeds grid price by {self.price_constraint_ratio}x'
            })
        
        # Select optimal
        if objective == 'cost':
            best = min(candidates, key=lambda x: x['cost'] if x['valid'] else float('inf'))
        else:
            best = min(candidates, key=lambda x: x['carbon'] if x['valid'] else float('inf'))
        
        # Current values
        current_cost = self._calculate_current_cost()
        current_carbon = self._calculate_current_carbon()
        
        # Savings
        cost_saving = current_cost - best['cost'] if best['cost'] != float('inf') else 0
        carbon_reduction = current_carbon - best['carbon'] if best['carbon'] != float('inf') else 0
        
        # Format electricity usage time
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
                'unit_cost': 'CNY/month',
                'unit_carbon': 'kg CO₂/month'
            },
            'optimized': {
                'cost': round(best['cost'], 2) if best['cost'] != float('inf') else None,
                'carbon': round(best['carbon'], 2) if best['carbon'] != float('inf') else None,
                'unit_cost': 'CNY/month',
                'unit_carbon': 'kg CO₂/month',
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
        """Get saving potential"""
        result = self.optimize(mode)
        
        if mode == 'cost':
            value = result['saving']['cost']
            unit = "CNY/month"
            description = f"By choosing the best supplier and optimizing usage schedule, you can save approximately {value:,.2f} CNY per month"
        else:
            value = result['saving']['carbon']
            unit = "kg CO₂/month"
            description = f"By choosing the best supplier and optimizing usage schedule, you can reduce approximately {value:,.2f} kg CO₂ emissions per month"
        
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
        """Get optimization suggestions"""
        result = self.optimize('cost')
        suggestions = []
        
        # Supplier suggestions
        if result['best_supplier']['type'] == SupplierType.SUPPLIER:
            suggestions.append({
                'title': 'Switch to retail supplier',
                'description': f'Retail supplier prices are more competitive, estimated monthly savings: {result["saving"]["cost"]:,.2f} CNY',
                'impact': 'high',
                'potential_saving': result['saving']['cost'],
                'potential_carbon_reduction': result['saving']['carbon'],
                'action_items': [
                    'Sign a long-term power purchase agreement with the retail supplier',
                    'Monitor retail supplier price fluctuations',
                    'Regularly evaluate supplier cost-effectiveness'
                ]
            })
        else:
            suggestions.append({
                'title': 'Keep using the grid supplier',
                'description': 'Current retail supplier price does not meet constraint (must not exceed grid price by 1.6x), continue using grid supplier',
                'impact': 'medium',
                'potential_saving': 0,
                'potential_carbon_reduction': 0,
                'action_items': [
                    'Monitor retail supplier price changes',
                    'Wait for better retail supplier offers',
                    'Consider participating in power market trading'
                ]
            })
        
        # Electricity usage timing suggestions
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
                'title': 'Adjust electricity usage schedule',
                'description': f'Suggest moving some production tasks to lower price periods: {", ".join(new_hours[:3])}',
                'impact': 'high' if len(new_hours) > 3 else 'medium',
                'potential_saving': result['saving']['cost'] * 0.6,
                'potential_carbon_reduction': result['saving']['carbon'] * 0.5,
                'action_items': [
                    f'Schedule production in lower-price periods such as {"、".join(new_hours[:3])}',
                    'Adjust production shift schedule',
                    'Optimize dispatch of shiftable loads'
                ]
            })
        
        return {
            'success': True,
            'suggestions': suggestions
        }
    
    # Attribute aliases (compatibility)
    @property
    def grid_hourly_prices(self):
        return self.get_grid_hourly_prices()
    
    @property
    def supplier_hourly_prices(self):
        return self.get_supplier_hourly_prices()