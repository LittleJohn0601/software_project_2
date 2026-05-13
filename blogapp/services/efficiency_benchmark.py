"""
Industry Efficiency Benchmark Service
Reads industry benchmark data from database
"""

from blogapp.models import IndustryBenchmark, Factory


class EfficiencyBenchmarkService:
    """Efficiency benchmark service"""
    
    @classmethod
    def get_benchmark(cls, industry_type, monthly_usage):
        """Get efficiency benchmark and ranking from database"""
        
        # Read industry benchmark from database
        benchmark_data = IndustryBenchmark.query.filter_by(
            industry_type=industry_type
        ).first()
        
        # If not found, use defaults
        if not benchmark_data:
            benchmark_data = IndustryBenchmark.query.filter_by(
                industry_type='Other'
            ).first()
            
            if not benchmark_data:
                # If no default either, return None
                return None
        
        # Estimate monthly output (ten thousand yuan)
        estimated_output = round(
            (monthly_usage * benchmark_data.output_per_kwh) / 10000, 2
        )
        
        # Calculate energy intensity (kWh per ten thousand yuan)
        energy_intensity = round(
            monthly_usage / estimated_output, 2
        ) if estimated_output > 0 else 0
        
        # Determine level
        if energy_intensity <= benchmark_data.excellent_intensity:
            level = 'excellent'
            level_text = 'Excellent'
            level_color = 'success'
            level_icon = '🏆'
            tip = f'Outperforms {round((1 - energy_intensity/benchmark_data.excellent_intensity)*100)}% of industry peers'
        elif energy_intensity <= benchmark_data.avg_intensity:
            level = 'good'
            level_text = 'Good'
            level_color = 'primary'
            level_icon = '👍'
            tip = f'At industry average, {round(benchmark_data.avg_intensity - energy_intensity)} kWh/10k yuan room for improvement'
        elif energy_intensity <= benchmark_data.poor_intensity:
            level = 'average'
            level_text = 'Average'
            level_color = 'warning'
            level_icon = '⚠️'
            tip = 'Below industry average, consider optimizing power usage patterns'
        else:
            level = 'poor'
            level_text = 'Poor'
            level_color = 'danger'
            level_icon = '🔴'
            tip = 'In the bottom 30% of industry, optimization measures recommended'
        
        # Calculate potential savings
        target_intensity = benchmark_data.excellent_intensity
        target_usage = target_intensity * estimated_output
        potential_savings_kwh = monthly_usage - target_usage
        potential_savings_rate = round(
            (potential_savings_kwh / monthly_usage) * 100, 2
        ) if monthly_usage > 0 else 0
        
        return {
            'industry': industry_type,
            'monthly_usage': monthly_usage,
            'estimated_output': estimated_output,
            'energy_intensity': energy_intensity,
            'benchmark_avg': benchmark_data.avg_intensity,
            'benchmark_excellent': benchmark_data.excellent_intensity,
            'benchmark_poor': benchmark_data.poor_intensity,
            'output_per_kwh': benchmark_data.output_per_kwh,
            'level': level,
            'level_text': level_text,
            'level_color': level_color,
            'level_icon': level_icon,
            'tip': tip,
            'potential_savings_kwh': round(potential_savings_kwh, 2),
            'potential_savings_rate': potential_savings_rate,
        }


def get_efficiency_benchmark(factory):
    """Get factory efficiency benchmark"""
    if not factory:
        return None
    
    return EfficiencyBenchmarkService.get_benchmark(
        factory.industry_type,
        factory.monthly_usage
    )