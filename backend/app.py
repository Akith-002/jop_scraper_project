from flask import Flask, jsonify, request
from flask_cors import CORS
from scrapers import indeed, linkedin, glassdoor
import json
from database.db import initialize_db, get_db

app = Flask(__name__)
CORS(app)  # Enable CORS for Streamlit frontend

# Initialize database
initialize_db()

@app.route('/api/scrape', methods=['POST'])
def scrape_jobs():
    data = request.json
    job_title = data.get('job_title', '')
    location = data.get('location', '')
    sources = data.get('sources', ['indeed', 'linkedin', 'glassdoor'])
    
    results = []
    
    if 'indeed' in sources:
        indeed_jobs = indeed.scrape(job_title, location)
        results.extend(indeed_jobs)
    
    if 'linkedin' in sources:
        linkedin_jobs = linkedin.scrape(job_title, location)
        results.extend(linkedin_jobs)
    
    if 'glassdoor' in sources:
        glassdoor_jobs = glassdoor.scrape(job_title, location)
        results.extend(glassdoor_jobs)
    
    # Save to database
    db = get_db()
    for job in results:
        db.execute(
            'INSERT INTO jobs (title, company, location, description, url, source, date_posted) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (job['title'], job['company'], job['location'], job['description'], job['url'], job['source'], job['date_posted'])
        )
    db.commit()
    
    return jsonify({"jobs": results, "count": len(results)})

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    db = get_db()
    jobs = db.execute('SELECT * FROM jobs ORDER BY date_posted DESC').fetchall()
    
    # Convert to list of dictionaries
    result = []
    for job in jobs:
        result.append({
            'id': job['id'],
            'title': job['title'],
            'company': job['company'],
            'location': job['location'],
            'description': job['description'],
            'url': job['url'],
            'source': job['source'],
            'date_posted': job['date_posted']
        })
    
    return jsonify({"jobs": result, "count": len(result)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)