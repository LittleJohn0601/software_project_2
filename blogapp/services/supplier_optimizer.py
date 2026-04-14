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
            # 直接使用 ElectricityCostCalculator 获取电价
            from blogapp.services.electricity_cost import ElectricityCostCalculator
            calculator = ElectricityCostCalculator(self.factory.id)
            for hour in range(24):
                self._grid_hourly_prices[hour] = calculator.get_price_for_hour(hour)
        return self._grid_hourly_prices
    
    def get_supplier_hourly_prices(self) -> Dict[int, float]:
        """Get retail supplier time-of-use prices"""
        if self._supplier_hourly_prices is None:
            self._supplier_hourly_prices = {}
            for hp in self.supplier_prices_list:
                # Prefer actual_price (from HourlyElectricityPrice.actual_price) when available
                price = None
                if hasattr(hp, 'actual_price') and hp.actual_price is not None:
                    price = hp.actual_price
                elif hasattr(hp, 'price'):
                    price = hp.price
                else:
                    price = 0
                self._supplier_hourly_prices[hp.hour] = price
        return self._supplier_hourly_prices
    
    def get_carbon_factors(self) -> Dict[int, float]:
        """Get carbon emission factors for each hour (kg CO₂/kWh)"""
        if self._carbon_factors is None:
            self._carbon_factors = {}
            
            for hour in range(24):
                # Use unified carbon factor 0.6634 kg CO₂/kWh for all hours
                self._carbon_factors[hour] = 0.6634
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
            # For carbon mode, use photovoltaic carbon reduction potential
            current_schedule = self._get_current_schedule()
            pv_carbon_factor = 0.0520
            grid_carbon_factor = 0.6634
            monthly_days = self.factory.working_days_per_month
            
            # Calculate total carbon reduction from switching to PV
            total_carbon_reduction = 0.0
            for hour, is_working in enumerate(current_schedule):
                if is_working:
                    hourly_energy = self.hourly_usage
                    # Carbon reduction = (grid_factor - pv_factor) * energy
                    daily_reduction = hourly_energy * (grid_carbon_factor - pv_carbon_factor)
                    total_carbon_reduction += daily_reduction * monthly_days
            
            value = round(total_carbon_reduction, 2)
            unit = "kg CO₂/month"
            description = f"By switching to photovoltaic power generation, you can reduce approximately {value:,.2f} kg CO₂ emissions per month"
        
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
        """Get optimization suggestions - supplier only"""
        result = self.optimize('cost')
        carbon_result = self.optimize('carbon')
        suggestions = []
    
        # Get current and optimal schedules (for period calculation)
        current_schedule = self._get_current_schedule()
        grid_prices = self.get_grid_hourly_prices()
        carbon_factors = self.get_carbon_factors()
    
        # Define periods
        periods = {
            'Peak': {'hours': list(range(8, 11)) + list(range(17, 23)), 'current_usage': 0, 'optimal_usage': 0,
                    'current_cost': 0, 'optimal_cost': 0, 'current_carbon': 0, 'optimal_carbon': 0},
            'Normal': {'hours': list(range(7, 8)) + list(range(13, 17)) + list(range(23, 24)), 'current_usage': 0, 'optimal_usage': 0,
                   'current_cost': 0, 'optimal_cost': 0, 'current_carbon': 0, 'optimal_carbon': 0},
            'Valley': {'hours': list(range(0, 7)) + list(range(11, 13)), 'current_usage': 0, 'optimal_usage': 0,
                   'current_cost': 0, 'optimal_cost': 0, 'current_carbon': 0, 'optimal_carbon': 0}
        }
    
        # Get optimal schedule (cost mode)
        optimal_schedule = None
        if result['optimized']['schedule']:
            optimal_schedule = [0] * 24
            for hour_str in result['optimized']['schedule']:
                hour = int(hour_str[:2])
                optimal_schedule[hour] = 1
    
        # Calculate period data per-hour (use supplier actual price when comparing)
        supplier_prices = self.get_supplier_hourly_prices()
        best_supplier_type = result['best_supplier']['type']

        for period_name, period_info in periods.items():
            # Reset accumulators (daily)
            current_cost_daily = 0.0
            optimal_cost_daily = 0.0
            current_carbon_daily = 0.0
            optimal_carbon_daily = 0.0

            for hour in period_info['hours']:
                grid_p = grid_prices.get(hour, 0)
                sup_p = supplier_prices.get(hour, grid_p)

                # current usage at this hour (daily)
                if current_schedule[hour]:
                    usage = self.hourly_usage
                    current_cost_daily += usage * grid_p
                    current_carbon_daily += usage * carbon_factors.get(hour, 0)

                # optimal usage at this hour (daily)
                if optimal_schedule and optimal_schedule[hour]:
                    usage = self.hourly_usage
                    # If best supplier is retail, use supplier price; otherwise grid price
                    price_for_opt = sup_p if best_supplier_type == SupplierType.SUPPLIER else grid_p
                    optimal_cost_daily += usage * price_for_opt
                    optimal_carbon_daily += usage * carbon_factors.get(hour, 0)

            period_info['current_usage'] = sum(1 for h in period_info['hours'] if current_schedule[h]) * self.hourly_usage
            period_info['optimal_usage'] = sum(1 for h in period_info['hours'] if optimal_schedule and optimal_schedule[h]) * self.hourly_usage
            period_info['current_cost'] = current_cost_daily
            period_info['optimal_cost'] = optimal_cost_daily
            period_info['current_carbon'] = current_carbon_daily
            period_info['optimal_carbon'] = optimal_carbon_daily
    
        monthly_days = self.factory.working_days_per_month
    
        # Calculate photovoltaic (PV) carbon emissions using carbon factor 0.0520 kg CO₂/kWh
        pv_carbon_factor = 0.0520
        pv_total_carbon = 0.0
        for hour, is_working in enumerate(current_schedule):
            if is_working:
                hourly_energy = self.hourly_usage
                daily_carbon = hourly_energy * pv_carbon_factor
                pv_total_carbon += daily_carbon * monthly_days
        pv_total_carbon = round(pv_total_carbon, 2)
        
        # Calculate carbon comparison
        current_carbon_total = current_carbon = self._calculate_current_carbon()
        pv_carbon_reduction = current_carbon_total - pv_total_carbon
    
        # Build period savings details (cost only, carbon reduction not meaningful for supplier switch)
        period_savings = []
        period_names = {'Peak': 'Peak', 'Normal': 'Normal', 'Valley': 'Valley'}
        for period_name, p in periods.items():
            cost_saving = p['current_cost'] - p['optimal_cost']
            if cost_saving > 0:  # Only show periods with actual cost savings
                period_savings.append(
                    f"  • {period_names[period_name]} period: Save {cost_saving * monthly_days:,.2f} CNY/month"
                )
    
        # Supplier suggestion only
        if result['best_supplier']['type'] == SupplierType.SUPPLIER:
            suggestions.append({
                'title': 'Switch to Retail Supplier',
                'description': f'Retail supplier offers better prices, estimated monthly savings: {result["saving"]["cost"]:,.2f} CNY',
                'impact': 'high',
                'potential_saving': result['saving']['cost'],
                'potential_carbon_reduction': result['saving']['carbon'],  # Keep this for frontend compatibility
                'period_savings': period_savings if period_savings else None,
                'action_items': [
                    'Sign a long-term power purchase agreement with the retail supplier',
                    'Monitor retail supplier price fluctuations',
                    'Regularly evaluate supplier cost-effectiveness'
                ]
            })
        else:
            suggestions.append({
                'title': 'Continue Using Grid Supplier',
                'description': 'Current retail supplier price does not meet constraint (must not exceed grid price by 1.6x), continue using grid supplier',
                'impact': 'medium',
                'potential_saving': 0,
                'potential_carbon_reduction': 0,  # Keep this for frontend compatibility
                'period_savings': None,
                'action_items': [
                    'Monitor retail supplier price changes',
                    'Wait for better retail supplier offers',
                    'Consider participating in power market trading'
                ]
            })
        
        # Add photovoltaic comparison suggestion
        suggestions.append({
            'title': 'Consider Photovoltaic (PV) Power Generation',
            'description': f'Switching to photovoltaic power can significantly reduce carbon emissions. '
                          f'Current monthly carbon: {current_carbon_total:,.2f} kg CO₂, '
                          f'With PV (0.0520 kg CO₂/kWh): {pv_total_carbon:,.2f} kg CO₂, '
                          f'Carbon reduction: {pv_carbon_reduction:,.2f} kg CO₂/month ({pv_carbon_reduction/current_carbon_total*100:.1f}%)',
            'impact': 'high',
            'potential_saving': 0,  # PV is about carbon reduction, not cost saving in this context
            'potential_carbon_reduction': pv_carbon_reduction,
            'action_items': [
                'Evaluate rooftop or ground-mounted PV system feasibility',
                'Conduct solar irradiance assessment',
                'Request quotations from PV system providers',
                'Analyze investment ROI and payback period'
            ]
        })
    
        return {
            'success': True,
            'suggestions': suggestions,
            'summary': {
                'period_savings': period_savings,
                'total_monthly_saving': result['saving']['cost'],
                'total_monthly_reduction': result['saving']['carbon'],
                'photovoltaic_comparison': {
                    'current_carbon': current_carbon_total,
                    'pv_carbon': pv_total_carbon,
                    'carbon_reduction': pv_carbon_reduction,
                    'reduction_percentage': round(pv_carbon_reduction / current_carbon_total * 100, 1) if current_carbon_total > 0 else 0,
                    'unit': 'kg CO₂/month'
                }
            }
        }
    
    # Attribute aliases (compatibility)
    @property
    def grid_hourly_prices(self):
        return self.get_grid_hourly_prices()
    
    @property
    def supplier_hourly_prices(self):
        return self.get_supplier_hourly_prices()