# backend/scrapers/glassdoor.py
import requests
from bs4 import BeautifulSoup
import datetime

def scrape(job_title, location):
    jobs = []
    
    # Format search query for Glassdoor URL
    query = f"{job_title.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}"
    url = f"https://www.glassdoor.com/Job/{query}-SRCH_KO0,{len(job_title)}_IL.0,{len(location)}_IN1.htm"
    
    try:
        # Send request with custom headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job listings (note: selectors may need updating as Glassdoor changes its HTML)
            job_cards = soup.find_all('li', class_='react-job-listing')
            
            for card in job_cards:
                try:
                    title_elem = card.find('a', class_='job-link')
                    title = title_elem.get_text().strip() if title_elem else "N/A"
                    
                    company_elem = card.find('div', class_='job-search-results__company-name')
                    company = company_elem.get_text().strip() if company_elem else "N/A"
                    
                    location_elem = card.find('span', class_='location')
                    location = location_elem.get_text().strip() if location_elem else "N/A"
                    
                    # Glassdoor job listings usually don't show full description in search results
                    description = "Click to view full description"
                    
                    # Get job URL
                    job_url = f"https://www.glassdoor.com{title_elem['href']}" if title_elem and 'href' in title_elem.attrs else "N/A"
                    
                    # Get current date as posting date
                    date_posted = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'description': description,
                        'url': job_url,
                        'source': 'Glassdoor',
                        'date_posted': date_posted
                    }
                    
                    jobs.append(job)
                except Exception as e:
                    print(f"Error parsing job card: {e}")
    
    except Exception as e:
        print(f"Error scraping Glassdoor: {e}")
    
    return jobs