from flask import Flask, render_template, abort, request, redirect, url_for, Response
import os
import glob
import markdown
import json
import csv
import threading
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), 'outputs')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
import runner

import sqlite3

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'history.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

@app.route('/')
def index():
    config = get_config()
    current_categories = ", ".join(config.get("high_value_categories", []))
    current_locations = ", ".join(config.get("high_value_areas", []))
    message = request.args.get('message')
    
    top_leads = []
    try:
        conn = get_db()
        top_leads = conn.execute("SELECT * FROM leads WHERE suggested_pitch != '' ORDER BY score DESC LIMIT 15").fetchall()
        conn.close()
    except Exception as e:
        print("DB Error:", e)
    
    return render_template('index.html', top_leads=top_leads, 
                           current_categories=current_categories, current_locations=current_locations, 
                           message=message, active_tab='dashboard')

@app.route('/leads')
def view_leads():
    config = get_config()
    current_categories = ", ".join(config.get("high_value_categories", []))
    current_locations = ", ".join(config.get("high_value_areas", []))
    
    all_leads = []
    try:
        conn = get_db()
        all_leads = conn.execute("SELECT * FROM leads ORDER BY score DESC, date_added DESC").fetchall()
        conn.close()
    except:
        pass
        
    return render_template('index.html', all_leads=all_leads, 
                           current_categories=current_categories, current_locations=current_locations, 
                           active_tab='leads')

@app.route('/update-status', methods=['POST'])
def update_status():
    lead_id = request.form.get('lead_id')
    new_status = request.form.get('status')
    if lead_id and new_status:
        try:
            conn = get_db()
            conn.execute("UPDATE leads SET status = ? WHERE id = ?", (new_status, lead_id))
            conn.commit()
            conn.close()
        except:
            pass
    return redirect(request.referrer or url_for('view_leads'))

@app.route('/export')
def export_leads():
    try:
        conn = get_db()
        leads = conn.execute("SELECT * FROM leads ORDER BY score DESC").fetchall()
        conn.close()
        
        def generate():
            yield 'ID,Business Name,Category,Area,Rating,Reviews,Website,Phone,Score,Status,Date Added,Why Good Lead,Suggested Pitch\n'
            for lead in leads:
                row = [
                    str(lead['id']),
                    f'"{lead["business_name"]}"' if lead['business_name'] else '',
                    f'"{lead["category"]}"' if lead['category'] else '',
                    f'"{lead["area"]}"' if lead['area'] else '',
                    str(lead['rating']),
                    str(lead['reviews']),
                    f'"{lead["website"]}"' if lead['website'] else '',
                    f'"{lead["phone"]}"' if lead['phone'] else '',
                    str(lead['score']),
                    f'"{lead["status"]}"' if lead['status'] else '',
                    f'"{lead["date_added"]}"' if lead['date_added'] else '',
                    f'"{lead["why_good_lead"]}"' if lead['why_good_lead'] else '',
                    f'"{lead["suggested_pitch"]}"' if lead['suggested_pitch'] else ''
                ]
                yield ','.join(row) + '\n'
                
        return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=leads_export.csv'})
    except Exception as e:
        return str(e)

@app.route('/run', methods=['POST'])
def run_engine():
    categories_raw = request.form.get('categories', '')
    locations_raw = request.form.get('locations', '')
    
    categories = [c.strip() for c in categories_raw.split(',') if c.strip()]
    locations = [l.strip() for l in locations_raw.split(',') if l.strip()]
    
    queries = []
    for loc in locations:
        for cat in categories:
            queries.append(f"{cat} in {loc}")
            
    config = get_config()
    config['search_queries'] = queries
    config['high_value_categories'] = categories
    config['high_value_areas'] = locations
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
        
    # Start engine in background
    thread = threading.Thread(target=runner.main)
    thread.start()
    
    return redirect(url_for('index', message="Engine started! The scraper and AI are running in the background. Please check back in a few minutes."))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
