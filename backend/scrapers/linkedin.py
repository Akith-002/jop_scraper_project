# backend/scrapers/linkedin.py
import requests
from bs4 import BeautifulSoup
import datetime

def scrape(job_title, location):
    jobs = []
    
    # Format search query for LinkedIn URL
    query = f"{job_title.replace(' ', '%20')}%20{location.replace(' ', '%20')}"
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}"
    
    try:
        # Send request with custom headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job listings (note: selectors may need updating as LinkedIn changes its HTML)
            job_cards = soup.find_all('div', class_='base-card')
            
            for card in job_cards:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    title = title_elem.get_text().strip() if title_elem else "N/A"
                    
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    company = company_elem.get_text().strip() if company_elem else "N/A"
                    
                    location_elem = card.find('span', class_='job-search-card__location')
                    location = location_elem.get_text().strip() if location_elem else "N/A"
                    
                    # LinkedIn job listings usually don't show description in search results
                    description = "Click to view full description"
                    
                    url_elem = card.find('a', class_='base-card__full-link')
                    job_url = url_elem['href'] if url_elem else "N/A"
                    
                    # Get current date as posting date
                    date_posted = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'description': description,
                        'url': job_url,
                        'source': 'LinkedIn',
                        'date_posted': date_posted
                    }
                    
                    jobs.append(job)
                except Exception as e:
                    print(f"Error parsing job card: {e}")
    
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")
    
    return jobs
