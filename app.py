import os
from datetime import datetime
import pandas as pd
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import io
from config import DEPARTMENTS, DATABASE_URL
from utils import classify_department

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db.init_app(app)

from models import Delay

@app.route('/')
def index():
    return render_template('index.html', departments=DEPARTMENTS)

@app.route('/submit_delay', methods=['POST'])
def submit_delay():
    try:
        data = request.form

        # All departments are now classified by AI
        origin_dept = classify_department(data['description'])
        
        issue = Delay(
            job_number=data['job_number'],
            part_number=data['part_number'],
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            discovery_department=data['discovery_department'],
            description=data['description'],
            delay_time=float(data['delay_time']),
            origin_department=origin_dept,
            manually_classified=False
        )

        db.session.add(issue)
        db.session.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_delays')
def get_delays():
    issues = Delay.query.all()
    issues_by_dept = {}
    
    for dept in DEPARTMENTS:
        dept_issues = [d.to_dict() for d in issues if d.origin_department == dept]
        total_time = sum(d['delay_time'] for d in dept_issues)
        issues_by_dept[dept] = {
            'delays': dept_issues,
            'total_time': total_time
        }
    
    return jsonify(issues_by_dept)

@app.route('/contest_delay', methods=['POST'])
def contest_delay():
    data = request.json
    issue = Delay.query.get(data['delay_id'])
    if issue:
        issue.previous_department = issue.origin_department
        issue.origin_department = data['new_department']
        issue.contested = True
        issue.contest_reason = data['reason']
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Issue not found'})

@app.route('/export_csv')
def export_csv():
    issues = Delay.query.all()
    departments_data = {}

    # Group issues by department
    for dept in DEPARTMENTS:
        dept_issues = [d for d in issues if d.origin_department == dept]
        if dept_issues:
            # Create DataFrame for this department
            df_data = {
                'date': [d.date.strftime('%d-%m') for d in dept_issues],
                'discovered in': [d.discovery_department for d in dept_issues],
                'job#': [d.job_number for d in dept_issues],
                'part#': [d.part_number for d in dept_issues],
                dept: [d.description for d in dept_issues],  # Department name as column header
                'hrs': [d.delay_time for d in dept_issues]
            }
            departments_data[dept] = pd.DataFrame(df_data)

    # Combine all department data
    if departments_data:
        # Create output buffer
        output = io.StringIO()
        first_dept = True

        for dept, df in departments_data.items():
            if not first_dept:
                output.write('\n')  # Add blank line between departments
            first_dept = False

            # Write the data for this department
            df.to_csv(output, index=False)

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='production_issues.csv'
        )
    else:
        # Return empty CSV if no data
        return send_file(
            io.BytesIO('No data available'.encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='production_issues.csv'
        )

@app.route('/clear_data', methods=['POST'])
def clear_data():
    try:
        Delay.query.delete()
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

with app.app_context():
    db.create_all()