# backend/services/gemini_service.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiService:
    def __init__(self):
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_job_description(self, description):
        """Extract key information from job descriptions"""
        prompt = f"""
        Analyze this job description and extract the following information:
        - Required skills (technical and soft skills)
        - Experience level (entry, mid, senior)
        - Education requirements
        - Key responsibilities
        - Benefits (if mentioned)
        
        Job description:
        {description}
        
        Return the information in JSON format.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def summarize_job(self, description, max_bullets=5):
        """Create a concise summary of a job description"""
        prompt = f"""
        Summarize this job description in {max_bullets} bullet points highlighting the most important aspects:
        
        {description}
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def get_job_recommendations(self, user_skills, user_experience, job_listings, max_results=5):
        """Find the best job matches based on user profile"""
        # Format job listings for the prompt
        job_listings_text = "\n\n".join([
            f"Job {i+1}:\nTitle: {job['title']}\nCompany: {job['company']}\nDescription: {job['description']}"
            for i, job in enumerate(job_listings[:20])  # Limit to first 20 for API constraints
        ])
        
        prompt = f"""
        Given the following user profile and job listings, identify the top {max_results} most suitable jobs for this candidate.
        For each recommended job, provide a unique and detailed explanation of why it's a good match, considering the specific skills and experience of the candidate.
        
        User Profile:
        - Skills: {user_skills}
        - Experience: {user_experience}
        
        Job Listings:
        {job_listings_text}
        
        Return your answer in JSON format with job IDs and match explanations.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_job_market_insights(self, job_listings):
        """Generate insights about the current job market based on scraped listings"""
        # Prepare data for analysis
        titles = [job['title'] for job in job_listings]
        companies = [job['company'] for job in job_listings]
        locations = [job['location'] for job in job_listings]
        
        data_summary = f"""
        Job Titles: {titles[:30]}
        Companies: {list(set(companies))[:30]}
        Locations: {list(set(locations))[:30]}
        Total Jobs: {len(job_listings)}
        """
        
        prompt = f"""
        Based on this job market data, provide 3-5 key insights about trends, in-demand skills, and market conditions.
        
        Data:
        {data_summary}
        
        Format your insights as bullet points with brief explanations.
        """
        
        response = self.model.generate_content(prompt)
        return response.text