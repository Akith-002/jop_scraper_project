# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from scrapers import indeed, linkedin, glassdoor
import json
from database.db import initialize_db, get_db
from services.gemini_service import GeminiService

app = Flask(__name__)
CORS(app)  # Enable CORS for Streamlit frontend

# Initialize database
initialize_db()

# Initialize Gemini service
gemini_service = GeminiService()

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
    
    # Fetch jobs with IDs
    jobs_with_ids = db.execute('SELECT * FROM jobs ORDER BY date_posted DESC').fetchall()
    
    # Convert to list of dictionaries
    result = []
    for job in jobs_with_ids:
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

@app.route('/api/analyze', methods=['POST'])
def analyze_job():
    """Analyze a job description using Gemini"""
    data = request.json
    job_id = data.get('job_id')
    
    db = get_db()
    job = db.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    # Get analysis from Gemini
    analysis = gemini_service.analyze_job_description(job['description'])
    
    return jsonify({
        "job_id": job_id,
        "analysis": analysis
    })

@app.route('/api/summarize', methods=['POST'])
def summarize_job():
    """Get a concise summary of a job"""
    data = request.json
    job_id = data.get('job_id')
    
    db = get_db()
    job = db.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    # Get summary from Gemini
    summary = gemini_service.summarize_job(job['description'])
    
    return jsonify({
        "job_id": job_id,
        "summary": summary
    })

@app.route('/api/insights', methods=['GET'])
def get_market_insights():
    """Generate market insights from all jobs"""
    db = get_db()
    jobs = db.execute('SELECT * FROM jobs ORDER BY date_posted DESC').fetchall()
    
    # Convert to list of dictionaries
    job_list = []
    for job in jobs:
        job_list.append({
            'id': job['id'],
            'title': job['title'],
            'company': job['company'],
            'location': job['location'],
            'description': job['description'],
            'url': job['url'],
            'source': job['source'],
            'date_posted': job['date_posted']
        })
    
    # Get insights from Gemini
    insights = gemini_service.generate_job_market_insights(job_list)
    
    return jsonify({
        "insights": insights
    })

@app.route('/api/recommend', methods=['POST'])
def recommend_jobs():
    """Recommend jobs based on user profile"""
    data = request.json
    skills = data.get('skills', '')
    experience = data.get('experience', '')
    
    db = get_db()
    jobs = db.execute('SELECT * FROM jobs ORDER BY date_posted DESC').fetchall()
    
    # Convert to list of dictionaries
    job_list = []
    for job in jobs:
        job_list.append({
            'id': job['id'],
            'title': job['title'],
            'company': job['company'],
            'location': job['location'],
            'description': job['description'],
            'url': job['url'],
            'source': job['source'],
            'date_posted': job['date_posted']
        })
    
    # Get recommendations from Gemini
    recommendations = gemini_service.get_job_recommendations(skills, experience, job_list)
    
    return jsonify({
        "recommendations": recommendations
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)