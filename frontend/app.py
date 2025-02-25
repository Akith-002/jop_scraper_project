# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import time
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
    st.title("🔍 Job Listings Scraper")
    
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
        
        # Search button
        search_button = st.button("Search Jobs")
    
    # Main content area
    tabs = st.tabs(["Search Results", "Analytics", "About"])
    
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
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")
    
    # Analytics Tab
    with tabs[1]:
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
    with tabs[2]:
        st.header("About this application")
        st.write("""
        This Job Listings Scraper allows you to search for job postings across multiple job boards including Indeed, LinkedIn, and Glassdoor.
        
        ### Features:
        - Search for jobs by title and location
        - Filter by multiple job boards
        - View detailed job listings
        - Analyze job data with interactive visualizations
        
        ### Technical Details:
        - **Frontend**: Streamlit
        - **Backend**: Flask
        - **Web Scraping**: Beautiful Soup, Requests
        - **Data Storage**: SQLite
        
        ### Disclaimer:
        This application is for educational purposes only. Always respect the terms of service of the websites you scrape.
        """)

if __name__ == "__main__":
    main()