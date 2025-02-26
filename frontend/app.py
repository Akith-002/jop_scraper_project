# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Job Listings Scraper",
    page_icon="🔍",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:5000/api"

def main():
    st.title("🔍 Job Listings Scraper with AI Insights")
    
    # Sidebar for search options
    with st.sidebar:
        st.header("Search Options")
        
        job_title = st.text_input("Job Title", "Python Developer")
        location = st.text_input("Location", "Remote")
        
        # Source selection
        st.subheader("Sources")
        indeed = st.checkbox("Indeed", value=True)
        linkedin = st.checkbox("LinkedIn", value=True)
        glassdoor = st.checkbox("Glassdoor", value=True)
        
        # Build sources list
        sources = []
        if indeed:
            sources.append("indeed")
        if linkedin:
            sources.append("linkedin")
        if glassdoor:
            sources.append("glassdoor")
        
        # AI Features section
        st.subheader("AI Assistant")
        st.write("Share your profile for personalized recommendations:")
        user_skills = st.text_area("Your Skills", "Python, SQL, Data Analysis")
        user_experience = st.select_slider(
            "Experience Level",
            options=["Entry-level", "Mid-level", "Senior", "Leadership"]
        )
        
        # Search button
        search_button = st.button("Search Jobs")
    
    # Main content area
    tabs = st.tabs(["Search Results", "AI Insights", "Analytics", "About"])
    
    # Search Results Tab
    with tabs[0]:
        if search_button:
            with st.spinner("Scraping job listings..."):
                # Make API request to Flask backend
                payload = {
                    "job_title": job_title,
                    "location": location,
                    "sources": sources
                }
                
                try:
                    response = requests.post(f"{API_URL}/scrape", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        jobs = data.get("jobs", [])
                        
                        # Store jobs in session state for analytics
                        st.session_state.jobs = jobs
                        
                        # Display job count
                        st.success(f"Found {len(jobs)} job listings")
                        
                        # Display jobs in cards
                        for job in jobs:
                            with st.expander(f"{job['title']} at {job['company']}"):
                                cols = st.columns([3, 1])
                                with cols[0]:
                                    st.markdown(f"**Company:** {job['company']}")
                                    st.markdown(f"**Location:** {job['location']}")
                                    st.markdown(f"**Description:** {job['description']}")
                                    st.markdown(f"**Date Posted:** {job['date_posted']}")
                                with cols[1]:
                                    st.markdown(f"**Source:** {job['source']}")
                                    st.link_button("View Job", job['url'])
                                    
                                    # AI analysis buttons
                                    if st.button("✨ AI Analysis", key=f"analyze_{job['id']}"):
                                        with st.spinner("Analyzing job..."):
                                            analysis_response = requests.post(
                                                f"{API_URL}/analyze", 
                                                json={"job_id": job['id']}
                                            )
                                            if analysis_response.status_code == 200:
                                                analysis_data = analysis_response.json()
                                                st.json(analysis_data["analysis"])
                                            else:
                                                st.error("Failed to analyze job")
                                    
                                    if st.button("📝 Quick Summary", key=f"summary_{job['id']}"):
                                        with st.spinner("Generating summary..."):
                                            summary_response = requests.post(
                                                f"{API_URL}/summarize", 
                                                json={"job_id": job['id']}
                                            )
                                            if summary_response.status_code == 200:
                                                summary_data = summary_response.json()
                                                st.write(summary_data["summary"])
                                            else:
                                                st.error("Failed to summarize job")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")
    
    # AI Insights Tab
    with tabs[1]:
        st.header("AI-Powered Insights")
        
        insights_tab1, insights_tab2 = st.tabs(["Job Market Insights", "Personalized Recommendations"])
        
        with insights_tab1:
            if st.button("Generate Market Insights"):
                with st.spinner("Analyzing job market data..."):
                    try:
                        insights_response = requests.get(f"{API_URL}/insights")
                        if insights_response.status_code == 200:
                            insights_data = insights_response.json()
                            st.markdown("### Job Market Trends")
                            st.write(insights_data["insights"])
                        else:
                            st.error("Failed to generate insights")
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")
        
        with insights_tab2:
            if st.button("Get Personalized Job Recommendations"):
                with st.spinner("Finding the best matches for your profile..."):
                    try:
                        payload = {
                            "skills": user_skills,
                            "experience": user_experience
                        }
                        
                        recommendations_response = requests.post(
                            f"{API_URL}/recommend", 
                            json=payload
                        )
                        
                        if recommendations_response.status_code == 200:
                            recommendations_data = recommendations_response.json()
                            st.markdown("### Recommended Jobs for You")
                            
                            # Display each recommendation
                            for recommendation in recommendations_data["top_job_recommendations"]:
                                job_id = recommendation["job_id"]
                                match_explanation = recommendation["match_explanation"]
                                
                                st.markdown(f"**Job ID:** {job_id}")
                                st.markdown(f"**Match Explanation:** {match_explanation}")
                                st.markdown("---")
                        else:
                            st.error("Failed to generate recommendations")
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")
    
    # Analytics Tab
    with tabs[2]:
        if 'jobs' in st.session_state and st.session_state.jobs:
            jobs = st.session_state.jobs
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(jobs)
            
            # Display basic stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Jobs", len(df))
            with col2:
                st.metric("Companies", df['company'].nunique())
            with col3:
                st.metric("Locations", df['location'].nunique())
            
            # Charts row
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Source distribution
                source_counts = df['source'].value_counts().reset_index()
                source_counts.columns = ['Source', 'Count']
                
                fig1 = px.pie(
                    source_counts, 
                    values='Count', 
                    names='Source',
                    title='Job Distribution by Source'
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with chart_col2:
                # Location distribution
                location_counts = df['location'].value_counts().reset_index().head(10)
                location_counts.columns = ['Location', 'Count']
                
                fig2 = px.bar(
                    location_counts,
                    x='Location',
                    y='Count',
                    title='Top 10 Locations'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Company distribution
            company_counts = df['company'].value_counts().reset_index().head(15)
            company_counts.columns = ['Company', 'Count']
            
            fig3 = px.bar(
                company_counts,
                x='Company',
                y='Count',
                title='Top 15 Companies Hiring'
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Raw data table
            st.subheader("Raw Data")
            st.dataframe(df)
        else:
            st.info("No data available yet. Please run a search first.")
    
    
    # About Tab
    with tabs[3]:
        st.header("About this application")
        st.write("""
        This Job Listings Scraper allows you to search for job postings across multiple job boards including Indeed, LinkedIn, and Glassdoor.
        
        ### Features:
        - Search for jobs by title and location
        - Filter by multiple job boards
        - View detailed job listings
        - Analyze job data with interactive visualizations
        - AI-powered insights and recommendations (powered by Google's Gemini API)
        
        ### Technical Details:
        - **Frontend**: Streamlit
        - **Backend**: Flask
        - **Web Scraping**: Beautiful Soup, Requests
        - **Data Storage**: SQLite
        - **AI Integration**: Google Gemini API
        
        ### Disclaimer:
        This application is for educational purposes only. Always respect the terms of service of the websites you scrape.
        """)

if __name__ == "__main__":
    main()