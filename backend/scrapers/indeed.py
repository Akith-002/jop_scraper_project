# backend/scrapers/indeed.py
import requests
from bs4 import BeautifulSoup
import datetime

def scrape(job_title, location):
    jobs = []
    
    # Format search query for Indeed URL
    query = f"{job_title.replace(' ', '+')}+in+{location.replace(' ', '+')}"
    url = f"https://www.indeed.com/jobs?q={query}"
    
    try:
        # Send request with custom headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job listings (note: selectors may need updating as Indeed changes its HTML)
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for card in job_cards:
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    title = title_elem.get_text().strip() if title_elem else "N/A"
                    
                    company_elem = card.find('span', class_='companyName')
                    company = company_elem.get_text().strip() if company_elem else "N/A"
                    
                    location_elem = card.find('div', class_='companyLocation')
                    location = location_elem.get_text().strip() if location_elem else "N/A"
                    
                    description_elem = card.find('div', class_='job-snippet')
                    description = description_elem.get_text().strip() if description_elem else "N/A"
                    
                    url_elem = card.find('a', class_='jcs-JobTitle')
                    relative_url = url_elem['href'] if url_elem else ""
                    job_url = f"https://www.indeed.com{relative_url}" if relative_url else "N/A"
                    
                    # Get current date as posting date
                    date_posted = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'description': description,
                        'url': job_url,
                        'source': 'Indeed',
                        'date_posted': date_posted
                    }
                    
                    jobs.append(job)
                except Exception as e:
                    print(f"Error parsing job card: {e}")
    
    except Exception as e:
        print(f"Error scraping Indeed: {e}")
    
    return jobs