# fix_empty_notes.py

from blogapp import create_app, db
from blogapp.models import CarbonFootprintLog

def add_default_notes():
    """
    Add default notes to all carbon footprint records with empty notes
    """
    # Create application context
    app = create_app()
    
    with app.app_context():
        try:
            # Find all records with empty notes
            empty_notes = CarbonFootprintLog.query.filter(
                (CarbonFootprintLog.notes == None) | (CarbonFootprintLog.notes == '')
            ).all()
            
            if not empty_notes:
                print("✅ No records with empty notes found")
                return
            
            print(f"🔍 Found {len(empty_notes)} records with empty notes")
            
            # Update each record
            updated_count = 0
            for log in empty_notes:
                log.notes = "No note at all"
                updated_count += 1
                
                # Commit every 100 records to avoid excessive memory usage
                if updated_count % 100 == 0:
                    db.session.commit()
                    print(f"✅ Updated {updated_count} records")
            
            # Commit remaining updates
            db.session.commit()
            print(f"✅ Completed! Updated notes field for a total of {updated_count} records")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error occurred during update: {e}")
            raise

if __name__ == "__main__":
    add_default_notes()