from datetime import datetime
from app import db

class Delay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_number = db.Column(db.String(100))
    part_number = db.Column(db.String(100))
    date = db.Column(db.Date, default=datetime.utcnow)
    discovery_department = db.Column(db.String(100))
    description = db.Column(db.Text)
    delay_time = db.Column(db.Float)  # Keeping field name for database compatibility
    origin_department = db.Column(db.String(100))
    manually_classified = db.Column(db.Boolean, default=False)
    
    # Contest related fields
    contested = db.Column(db.Boolean, default=False)
    contest_reason = db.Column(db.Text)
    previous_department = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'job_number': self.job_number,
            'part_number': self.part_number,
            'date': self.date.strftime('%Y-%m-%d'),
            'discovery_department': self.discovery_department,
            'description': self.description,
            'issue_time': self.delay_time,
            'origin_department': self.origin_department,
            'contested': self.contested,
            'contest_reason': self.contest_reason
        }
