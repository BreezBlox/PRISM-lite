import os
from datetime import datetime
import pandas as pd
import csv
import io
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
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
    output = io.StringIO()
    writer = csv.writer(output)

    # Group delays by department
    delays_by_dept = {}
    dept_totals = {}

    for dept in DEPARTMENTS:
        dept_delays = [d for d in delays if d.origin_department == dept]
        delays_by_dept[dept] = dept_delays
        dept_totals[dept] = sum(d.delay_time for d in dept_delays)

    for dept in DEPARTMENTS:
        # Write department header
        writer.writerow(['', '', '', '', dept, f'{dept_totals[dept]:.1f}'])

        # Write column headers
        writer.writerow(['Date', 'Discovered in', 'Job#', 'Part#', 'Description', f'{dept_totals[dept]:.1f}'])

        # Write department delays
        for delay in delays_by_dept[dept]:
            writer.writerow([
                delay.date.strftime('%d-%m'),  # Day-Month only
                delay.discovery_department,
                delay.job_number,
                delay.part_number or '',
                delay.description,
                f'{delay.delay_time:.1f}'
            ])

        # Add blank row between departments
        writer.writerow([])

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