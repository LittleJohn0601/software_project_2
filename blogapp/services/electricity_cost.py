import json
from typing import Dict, List, Optional
from blogapp.models import Factory, GridElectricityPrice, TimeOfUsePeriod
from blogapp import db


class ElectricityCostCalculator:
    """Electricity cost calculator"""
    
    def __init__(self, factory_id: int):
        self.factory = Factory.query.get(factory_id)
        if not self.factory:
            raise ValueError(f"Factory with id {factory_id} not found")
        
        self.grid_price = GridElectricityPrice.query.filter_by(
            voltage_level=self.factory.voltage_level
        ).first()
        
        if not self.grid_price:
            raise ValueError(f"Grid price not found for voltage level {self.factory.voltage_level}")
        
        self.tou_periods = self._load_tou_periods()
    
    def _load_tou_periods(self) -> Dict[int, str]:
        """Load time-of-use pricing period configuration"""
        periods = TimeOfUsePeriod.query.all()
        return {p.hour: p.period_type for p in periods}
    
    def get_price_for_hour(self, hour: int) -> float:
        """Get electricity price for a specific hour"""
        period_type = self.tou_periods.get(hour, 'Normal')
        
        if period_type in ['高峰', 'peak', 'Peak']:
            return self.grid_price.peak_price
        elif period_type in ['低谷', 'valley', 'Valley']:
            return self.grid_price.valley_price
        else:
            return self.grid_price.normal_price
    
    def calculate_monthly_cost(self, month_days: int = None) -> Dict:
        """Calculate monthly cost"""
        if month_days is None:
            month_days = self.factory.working_days_per_month
        
        total_usage = self.factory.monthly_usage
        daily_usage = self.factory.daily_usage
        
        # Parse work periods
        work_periods = json.loads(self.factory.work_periods)

        if not work_periods:
            return {
                'factory_id': self.factory.id,
                'factory_name': self.factory.name,
                'voltage_level': self.factory.voltage_level,
                'month_days': month_days,
                'total_usage': 0,
                'daily_usage': self.factory.daily_usage,
                'daily_energy_cost': 0,
                'monthly_energy_cost': 0,
                'capacity_fee': round(self.factory.transformer_capacity * 22.5, 2),
                'total_monthly_cost': round(self.factory.transformer_capacity * 22.5, 2),
                'average_price': 0,
                'hourly_breakdown': [{
                    'hour': hour,
                    'time_range': f"{hour:02d}:00-{(hour+1):02d}:00",
                    'usage': 0,
                    'price': self.get_price_for_hour(hour),
                    'cost': 0,
                    'period_type': self.tou_periods.get(hour, 'Normal')
                } for hour in range(24)]
            }
        
        
        
        # Calculate total working hours
        total_work_hours = 0
        for period in work_periods:
            start = period.get('start', 0)
            end = period.get('end', 0)
            total_work_hours += (end - start)
        
        # Electricity usage per hour
        usage_per_hour = daily_usage / total_work_hours if total_work_hours > 0 else 0
        
        # Calculate daily cost
        daily_cost = 0
        hourly_breakdown = []
        
        for hour in range(24):
            # Determine if the hour falls within working time
            in_work = False
            for period in work_periods:
                if period.get('start', 0) <= hour < period.get('end', 0):
                    in_work = True
                    break
            
            usage = usage_per_hour if in_work else 0
            price = self.get_price_for_hour(hour)
            cost = usage * price
            
            daily_cost += cost
            hourly_breakdown.append({
                'hour': hour,
                'time_range': f"{hour:02d}:00-{(hour+1):02d}:00",
                'usage': round(usage, 2),
                'price': price,
                'cost': round(cost, 2),
                'period_type': self.tou_periods.get(hour, 'Normal')
            })
        
        # Calculate monthly cost
        monthly_energy_cost = daily_cost * month_days
        capacity_fee = self.factory.capacity_fee
        total_monthly_cost = monthly_energy_cost + capacity_fee
        avg_price = monthly_energy_cost / total_usage if total_usage > 0 else 0
        
        return {
            'factory_id': self.factory.id,
            'factory_name': self.factory.name,
            'voltage_level': self.factory.voltage_level,
            'month_days': month_days,
            'total_usage': round(total_usage, 2),
            'daily_usage': round(daily_usage, 2),
            'daily_energy_cost': round(daily_cost, 2),
            'monthly_energy_cost': round(monthly_energy_cost, 2),
            'capacity_fee': round(capacity_fee, 2),
            'total_monthly_cost': round(total_monthly_cost, 2),
            'average_price': round(avg_price, 4),
            'hourly_breakdown': hourly_breakdown
        }