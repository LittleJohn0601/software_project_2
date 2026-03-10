# blogapp/impact_calculator.py
from blogapp import db
from blogapp.models import CarbonFootprintLog, User
from sqlalchemy import func
from datetime import datetime, timedelta

class ImpactCalculator:
    """Calculator for environmental impact metrics based on actual user activities"""
    
    def calculate_campus_impact(self):
        """Calculate campus-wide environmental impact metrics based on actual data"""
        
        # 1. Total carbon saved from all user activities (直接从数据库获取)
        total_carbon_result = db.session.query(
            func.sum(CarbonFootprintLog.carbon_saved)
        ).scalar()
        total_carbon_saved = total_carbon_result if total_carbon_result else 0
        
        # 2. Trees equivalent calculation (21kg CO2 = 1 tree per year)
        trees_equivalent = total_carbon_saved / 21.0
        
        # 3. Campus target progress (suppose the goal is 50,000 kg CO₂)
        campus_target = 50000.0
        campus_target_progress = min(100.0, (total_carbon_saved / campus_target) * 100)
        
        # 4. Active participants (users with activities in last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_participants = db.session.query(
            func.count(func.distinct(CarbonFootprintLog.user_id))
        ).filter(
            CarbonFootprintLog.activity_date >= thirty_days_ago
        ).scalar() or 0
        
        # 5. calculate based on the activity type
        activity_breakdown = self.calculate_activity_breakdown()
        
        return {
            'total_carbon_saved': round(total_carbon_saved, 2),
            'trees_equivalent': round(trees_equivalent, 2),
            'campus_target_progress': round(campus_target_progress, 2),
            'active_participants': active_participants,
            'activity_breakdown': activity_breakdown
        }
    
    def calculate_activity_breakdown(self):
        """Calculate carbon savings breakdown by activity type"""
        breakdown = db.session.query(
            CarbonFootprintLog.activity_type,
            func.count(CarbonFootprintLog.id).label('activity_count'),
            func.sum(CarbonFootprintLog.carbon_saved).label('total_carbon')
        ).group_by(
            CarbonFootprintLog.activity_type
        ).all()
        
        result = {}
        for activity_type, count, carbon in breakdown:
            result[activity_type] = {
                'activity_count': count,
                'total_carbon': round(float(carbon), 2) if carbon else 0
            }
        
        return result
    
    def calculate_user_impact(self, user_id):
        """Calculate impact metrics for a specific user"""
        # all carbon saved
        user_carbon_result = db.session.query(
            func.sum(CarbonFootprintLog.carbon_saved)
        ).filter(
            CarbonFootprintLog.user_id == user_id
        ).scalar()
        user_carbon_saved = user_carbon_result if user_carbon_result else 0
        
        # calculate the activity
        user_activity_count = CarbonFootprintLog.query.filter_by(user_id=user_id).count()
        
        return {
            'user_carbon_saved': round(user_carbon_saved, 2),
            'user_trees_equivalent': round(user_carbon_saved / 21.0, 2),
            'activity_count': user_activity_count
        }
    
# Cycling: Saves 0.2 kg CO₂ per kilometer (compared to driving a car)

# Recycling: Saves 1.5 kg CO₂ per kilogram of recycled materials

# Energy Saving: Saves 0.5 kg CO₂ per kilowatt-hour (assuming energy comes from fossil fuels)

# Public Transport: Saves 0.1 kg CO₂ per kilometer (compared to private cars)

# Vegetarian Meal: Saves 2.0 kg CO₂ per meal (compared to meat-containing meals)  

# 2. Trees equivalent calculation (21kg CO2 = 1 tree per year)
# 3. Campus target progress 