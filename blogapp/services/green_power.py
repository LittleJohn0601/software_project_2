"""
Green Power Procurement Guide Service
Customized based on Shanxi Province renewable energy pricing reform
"""

class GreenPowerService:
    """Green power procurement guide service"""
    
    # Shanxi official trading platforms
    SHANXI_PLATFORMS = [
        {
            'name': 'Electric Power Trading Centre',
            'url': 'https://pmos.sx.sgcc.com.cn',
            'description': 'Official Shanxi electricity trading platform supporting green power trading',
            'price_info': 'Bidding price: 0.199-0.332 CNY/kWh',
            'type': 'official'
        },
        {
            'name': 'Electric Power Medium and Long-term Trading Platform',
            'url': 'https://pmos.sx.sgcc.com.cn',
            'description': 'Multi-year, annual, monthly green power contracts',
            'price_info': 'Market-based pricing',
            'type': 'exchange'
        },
        {
            'name': 'National Green Power Certificate Subscription Trading Platform',
            'url': 'https://www.greenenergy.org.cn',
            'description': 'National GEC platform for Shanxi renewable project registration',
            'price_info': '30-50 CNY per certificate (1000 kWh)',
            'type': 'national'
        }
    ]
    
    # Shanxi coal-fired benchmark price (CNY/kWh)
    SHANXI_BENCHMARK_PRICE = 0.332
    
    @classmethod
    def get_recommendation(cls, monthly_usage, project_type='existing'):
        """
        Args:
            monthly_usage: Monthly electricity consumption (kWh)
            project_type: 'existing' or 'incremental'
        """
        
        # 1. Tier based on usage
        if monthly_usage < 100000:
            tier = 'small'
            tier_name = 'Small and Medium-sized Enterprises'
            strategy = 'green_certificate'
            description = f'Monthly electricity consumption: {monthly_usage:,.0f} kWh, less than 100,000 kWh. It is recommended to directly purchase green certificates.'
            steps = [
                '1. Calculate monthly electricity consumption and determine the number of green certificates to purchase',
                '2. Register enterprise account on the national green certificate platform',
                '3. Purchase green certificates as needed and obtain green electricity certificates',
                '4. Disclose green certificate usage in ESG reports'
            ]
            certificates_needed = round(monthly_usage / 1000, 1)
            
        elif monthly_usage < 1000000:
            tier = 'medium'
            tier_name = 'Medium-sized Enterprises'
            strategy = 'green_ppa'
            description = f'Monthly electricity consumption: {monthly_usage:,.0f} kWh, between 100,000 and 1,000,000 kWh. It is recommended to sign a green power purchase agreement (PPA).'
            steps = [
                '1. Contact Electric Power Trading Centre to inquire about green power packages',
                '2. Sign a green power purchase agreement (PPA)',
                '3. Obtain green power consumption certificates',
                '4. Enjoy the carbon reduction benefits from the green power premium'
            ]
            certificates_needed = None
            
        else:
            tier = 'large'
            tier_name = 'Large-scale Electricity Consumers'
            strategy = 'pv_certificate'
            description = f'Monthly electricity consumption: {monthly_usage:,.0f} kWh, greater than 1,000,000 kWh. It is recommended to build a distributed photovoltaic system combined with green certificates.'
            steps = [
                '1. Evaluate the feasibility of installing rooftop solar panels at the factory',
                '2. Choose between the EMC (Energy Management Contract) model or self-investment',
                '3. Remaining electricity consumption can be offset by green certificates',
                '4. Surplus green electricity can participate in market-based transactions'
            ]
            certificates_needed = None
        
        # 2. Set pricing scheme
        if project_type == 'existing':
            mechanism_price = cls.SHANXI_BENCHMARK_PRICE
            price_info = f'Mechanism electricity price for existing projects：{mechanism_price}CNY/kWh'
            policy_note = 'According to the policy of June 2025, existing projects put into operation before 1 June 2025 will be settled based on the coal-fired benchmark price'
        else:
            price_info = 'Incremental project bidding mechanism price：0.199-0.332CNY/kWh'
            policy_note = 'According to the policy of June 2025, incremental projects put into operation after 1 June 2025 will have their mechanism prices determined through bidding'
        
        # 3. Calculate carbon reduction (national grid average emission factor 0.6634 kg CO₂/kWh)
        carbon_reduction = round(monthly_usage * 0.0006634, 2)  # tons CO₂/month
        
        # 4. Estimate costs
        if strategy == 'green_certificate':
            estimated_cost = round(monthly_usage * 0.04, 2)  # Green cert ~0.04 CNY/kWh
        elif strategy == 'green_ppa':
            estimated_cost = round(monthly_usage * 0.05, 2)  # PPA ~0.05 CNY/kWh
        else:
            estimated_cost = round(monthly_usage * 0.045, 2)  # Combined ~0.045 CNY/kWh
        
        return {
            'success': True,
            'tier': tier,
            'tier_name': tier_name,
            'description': description,
            'strategy': strategy,
            'steps': steps,
            'monthly_usage': monthly_usage,
            'estimated_cost_per_month': estimated_cost,
            'certificates_needed': certificates_needed,
            'carbon_reduction_per_month': carbon_reduction,
            'price_info': price_info,
            'policy_note': policy_note,
            'platforms': cls.SHANXI_PLATFORMS,
            'benchmark_price': cls.SHANXI_BENCHMARK_PRICE
        }


def get_green_power_recommendation(factory, project_type='existing'):
    """Get green power procurement recommendations for a factory"""
    if not factory:
        return None
    
    return GreenPowerService.get_recommendation(
        factory.monthly_usage,
        project_type
    )