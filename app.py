import os
from datetime import datetime
import pandas as pd
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import io
import csv
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

        # Determine origin department
        checked_depts = [dept for dept in DEPARTMENTS if data.get(f'dept_{dept}') == 'on']
        if data.get('dept_Other') == 'on' and data.get('dept_Other_value'):
            origin_dept = data.get('dept_Other_value')
            manually_classified = True
        elif checked_depts:
            origin_dept = checked_depts[0]
            manually_classified = True
        else:
            origin_dept = classify_department(data['description'])
            manually_classified = False

        delay = Delay(
            job_number=data['job_number'],
            part_number=data['part_number'],
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            discovery_department=data['discovery_department'],
            description=data['description'],
            delay_time=float(data['delay_time']),
            origin_department=origin_dept,
            manually_classified=manually_classified
        )

        db.session.add(delay)
        db.session.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_delays')
def get_delays():
    delays = Delay.query.all()
    delays_by_dept = {}
    
    for dept in DEPARTMENTS:
        dept_delays = [d.to_dict() for d in delays if d.origin_department == dept]
        total_time = sum(d['delay_time'] for d in dept_delays)
        delays_by_dept[dept] = {
            'delays': dept_delays,
            'total_time': total_time
        }
    
    return jsonify(delays_by_dept)

@app.route('/contest_delay', methods=['POST'])
def contest_delay():
    data = request.json
    delay = Delay.query.get(data['delay_id'])
    if delay:
        delay.previous_department = delay.origin_department
        delay.origin_department = data['new_department']
        delay.contested = True
        delay.contest_reason = data['reason']
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Delay not found'})

@app.route('/export_csv')
def export_csv():
    delays = Delay.query.all()
    delays_by_dept = {}

    # Group delays by department and calculate totals
    for dept in DEPARTMENTS:
        dept_delays = [d for d in delays if d.origin_department == dept]
        total_time = sum(d.delay_time for d in dept_delays)
        delays_by_dept[dept] = {
            'delays': dept_delays,
            'total_time': total_time
        }

    # Create the CSV data
    output = io.StringIO()
    csvwriter = csv.writer(output)

    # Write headers
    headers = ['date', 'discovered in', 'job#', 'part#', 'description', 'hrs', f'total - {delays_by_dept[DEPARTMENTS[0]]["total_time"]:.1f}']
    csvwriter.writerow(headers)

    # Write data for each department
    for dept in DEPARTMENTS:
        dept_data = delays_by_dept[dept]

        # Write department name and total
        if dept != DEPARTMENTS[0]:  # Skip for first department as it's in header
            empty_row = [''] * 6 + [f'total - {dept_data["total_time"]:.1f}']
            csvwriter.writerow(empty_row)

        # Write delays for this department
        for delay in dept_data['delays']:
            row = [
                delay.date.strftime('%d/%m'),  # Date format: day/month
                delay.discovery_department,
                delay.job_number,
                delay.part_number or '',
                delay.description,
                f'{delay.delay_time:.1f}'
            ]
            csvwriter.writerow(row)

        # Add blank row between departments
        if dept != DEPARTMENTS[-1]:
            csvwriter.writerow([''] * 7)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='delays.csv'
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