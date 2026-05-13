"""
Equipment Recommendation Service
Recommend energy-saving equipment based on factory usage patterns
"""

class EquipmentRecommendationService:
    """Energy-saving equipment recommendation service"""
    
    # Energy storage options
    STORAGE_OPTIONS = [
        {
            'name': 'Commercial Storage System',
            'capacity_kwh': 500,
            'power_kw': 100,
            'investment': 500000,
            'lifespan_years': 10,
            'suitable_for': ['medium', 'large'],
            'description': 'Charge during valley hours, discharge during peak hours',
            'annual_saving_per_kwh': 0.8
        },
        {
            'name': 'Compact Storage Unit',
            'capacity_kwh': 100,
            'power_kw': 30,
            'investment': 150000,
            'lifespan_years': 8,
            'suitable_for': ['small', 'medium'],
            'description': 'All-in-one design, easy installation',
            'annual_saving_per_kwh': 0.75
        },
        {
            'name': 'Container Storage System',
            'capacity_kwh': 2000,
            'power_kw': 500,
            'investment': 1800000,
            'lifespan_years': 12,
            'suitable_for': ['large'],
            'description': 'Modular container design for high usage factories',
            'annual_saving_per_kwh': 0.85
        }
    ]
    
    # VFD options (Variable Frequency Drive)
    VFD_OPTIONS = [
        {
            'name': 'Standard VFD',
            'power_range': '30-200 kW',
            'investment_per_kw': 300,
            'saving_rate': 0.25,
            'description': 'For fans, pumps, and variable torque loads'
        },
        {
            'name': 'High-Performance VFD',
            'power_range': '200-1000 kW',
            'investment_per_kw': 250,
            'saving_rate': 0.20,
            'description': 'For compressors, extruders, constant torque loads'
        }
    ]
    
    # LED lighting
    LED_OPTIONS = {
        'saving_rate': 0.60,
        'investment_per_kw': 5000,
        'description': 'Replace traditional lighting with LED',
        'payback_years': 1.5
    }
    
    @classmethod
    def get_size_tier(cls, monthly_usage):
        """Determine factory size tier based on monthly usage (kWh)"""
        if monthly_usage < 50000:
            return 'small'
        elif monthly_usage < 200000:
            return 'medium'
        else:
            return 'large'
    
    @classmethod
    def get_peak_valley_diff(cls, factory):
        """Calculate peak-valley price difference"""
        try:
            from blogapp.models import GridElectricityPrice
            grid_price = GridElectricityPrice.query.filter_by(
                voltage_level=factory.voltage_level
            ).first()
            if grid_price:
                return round(grid_price.peak_price - grid_price.valley_price, 2)
        except:
            pass
        return 0.8  # Default peak-valley difference
    
    @classmethod
    def recommend_storage(cls, monthly_usage, peak_valley_diff):
        """Recommend energy storage system"""
        tier = cls.get_size_tier(monthly_usage)
        
        # Find suitable devices
        suitable = [d for d in cls.STORAGE_OPTIONS if tier in d['suitable_for']]
        
        if not suitable:
            return None
        
        # Primary recommendation (first suitable device)
        device = suitable[0]
        
        # Calculate annual savings
        # Assume 1 cycle per day, 25 working days per month
        daily_saving = device['capacity_kwh'] * peak_valley_diff
        monthly_saving = daily_saving * 25
        annual_saving = monthly_saving * 12
        
        # Calculate payback period
        if annual_saving > 0:
            payback_years = round(device['investment'] / annual_saving, 1)
        else:
            payback_years = 999
        
        return {
            'category': 'Energy Storage',
            'icon': '🔋',
            'recommended_device': device['name'],
            'capacity_kwh': device['capacity_kwh'],
            'power_kw': device['power_kw'],
            'investment': device['investment'],
            'investment_formatted': f"¥{device['investment']:,.0f}",
            'annual_saving': round(annual_saving, 2),
            'annual_saving_formatted': f"¥{annual_saving:,.0f}",
            'payback_years': payback_years,
            'description': device['description'],
            'lifespan_years': device['lifespan_years']
        }
    
    @classmethod
    def recommend_vfd(cls, transformer_capacity):
        """Recommend Variable Frequency Drive"""
        # Assume motor power is 60% of transformer capacity
        motor_power = transformer_capacity * 0.6
        
        if motor_power < 200:
            device = cls.VFD_OPTIONS[0]
        else:
            device = cls.VFD_OPTIONS[1]
        
        investment = motor_power * device['investment_per_kw']
        annual_saving = investment * device['saving_rate']
        
        if annual_saving > 0:
            payback_years = round(investment / annual_saving, 1)
        else:
            payback_years = 999
        
        return {
            'category': 'Variable Frequency Drive',
            'icon': '⚙️',
            'recommended_device': device['name'],
            'motor_power_kw': round(motor_power, 1),
            'investment': round(investment, 2),
            'investment_formatted': f"¥{investment:,.0f}",
            'annual_saving': round(annual_saving, 2),
            'annual_saving_formatted': f"¥{annual_saving:,.0f}",
            'payback_years': payback_years,
            'description': device['description']
        }
    
    @classmethod
    def recommend_led(cls, transformer_capacity):
        """Recommend LED lighting replacement"""
        # Assume lighting load is 30% of transformer capacity
        lighting_power = transformer_capacity * 0.3
        
        investment = lighting_power * cls.LED_OPTIONS['investment_per_kw']
        annual_saving = investment * cls.LED_OPTIONS['saving_rate']
        
        if annual_saving > 0:
            payback_years = round(investment / annual_saving, 1)
        else:
            payback_years = 999
        
        return {
            'category': 'LED Lighting',
            'icon': '💡',
            'investment': round(investment, 2),
            'investment_formatted': f"¥{investment:,.0f}",
            'annual_saving': round(annual_saving, 2),
            'annual_saving_formatted': f"¥{annual_saving:,.0f}",
            'payback_years': payback_years,
            'saving_rate': f"{cls.LED_OPTIONS['saving_rate'] * 100}%",
            'description': cls.LED_OPTIONS['description']
        }
    
    @classmethod
    def get_all_recommendations(cls, factory):
        """Get all equipment recommendations for a factory"""
        if not factory:
            return []
        
        monthly_usage = factory.monthly_usage
        transformer_capacity = factory.transformer_capacity
        peak_valley_diff = cls.get_peak_valley_diff(factory)
        
        recommendations = []
        
        # Storage recommendation
        storage = cls.recommend_storage(monthly_usage, peak_valley_diff)
        if storage:
            recommendations.append(storage)
        
        # VFD recommendation
        vfd = cls.recommend_vfd(transformer_capacity)
        recommendations.append(vfd)
        
        # LED recommendation
        led = cls.recommend_led(transformer_capacity)
        recommendations.append(led)
        
        return recommendations


def get_equipment_recommendations(factory):
    """Get equipment recommendations for a factory"""
    if not factory:
        return None
    
    return EquipmentRecommendationService.get_all_recommendations(factory)