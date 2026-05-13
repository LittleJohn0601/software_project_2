"""
行业能效基准服务
从数据库读取行业基准数据
"""

from blogapp.models import IndustryBenchmark, Factory


class EfficiencyBenchmarkService:
    """能效基准服务"""
    
    @classmethod
    def get_benchmark(cls, industry_type, monthly_usage):
        """从数据库获取能效基准和排名"""
        
        # 从数据库读取行业基准
        benchmark_data = IndustryBenchmark.query.filter_by(
            industry_type=industry_type
        ).first()
        
        # 如果没有找到，使用默认值
        if not benchmark_data:
            benchmark_data = IndustryBenchmark.query.filter_by(
                industry_type='Other'
            ).first()
            
            if not benchmark_data:
                # 如果连默认都没有，返回 None
                return None
        
        # 估算月产值（万元）
        estimated_output = round(
            (monthly_usage * benchmark_data.output_per_kwh) / 10000, 2
        )
        
        # 计算单位产值能耗（kWh/万元）
        energy_intensity = round(
            monthly_usage / estimated_output, 2
        ) if estimated_output > 0 else 0
        
        # 判断等级
        if energy_intensity <= benchmark_data.excellent_intensity:
            level = 'excellent'
            level_text = '优秀'
            level_color = 'success'
            level_icon = '🏆'
            tip = f'Your energy efficiency level is above {round((1 - energy_intensity/benchmark_data.excellent_intensity)*100)}% of industry peers'
        elif energy_intensity <= benchmark_data.avg_intensity:
            level = 'good'
            level_text = '良好'
            level_color = 'primary'
            level_icon = '👍'
            tip = f'Your energy efficiency level is at the industry average, with {round(benchmark_data.avg_intensity - energy_intensity)} kWh/ten thousand yuan of room for improvement'
        elif energy_intensity <= benchmark_data.poor_intensity:
            level = 'average'
            level_text = '一般'
            level_color = 'warning'
            level_icon = '⚠️'
            tip = f'Your energy efficiency level is below the industry average,建议优化用电模式'
        else:
            level = 'poor'
            level_text = '待改进'
            level_color = 'danger'
            level_icon = '🔴'
            tip = f'Your energy efficiency level is in the bottom 30% of the industry,建议尽快采取优化措施'
        
        # 计算潜在节省
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
    """获取工厂的能效基准"""
    if not factory:
        return None
    
    return EfficiencyBenchmarkService.get_benchmark(
        factory.industry_type,
        factory.monthly_usage
    )