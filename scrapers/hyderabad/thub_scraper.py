import requests
from bs4 import BeautifulSoup
import re

def scrape_thub_portfolio():
    """
    Scrape T-Hub's portfolio page for Hyderabad startups.
    URL: https://t-hub.co/our-portfolio/
    """
    url = "https://t-hub.co/our-portfolio/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"[!] Error fetching T-Hub portfolio: {e}")
        return []
        
    soup = BeautifulSoup(response.text, 'lxml')
    startups = []
    
    # T-Hub often uses a grid of startup cards.
    # We need to find the specific selectors. 
    # Based on a typical WordPress/Elementor site like T-Hub:
    cards = soup.select('.elementor-post') or soup.select('.startup-card') or soup.select('.jet-listing-grid__item')
    
    for card in cards:
        try:
            name_el = card.select_one('h3') or card.select_one('.title')
            name = name_el.text.strip() if name_el else None
            
            link_el = card.select_one('a')
            website = link_el['href'] if link_el and link_el.has_attr('href') else None
            
            desc_el = card.select_one('p') or card.select_one('.description')
            description = desc_el.text.strip() if desc_el else ""
            
            if name and website:
                # Basic normalization
                if not website.startswith('http'):
                    continue # Skip invalid links
                    
                startups.append({
                    "company_name": name,
                    "source": "thub",
                    "company_url": website,
                    "description": description,
                    "activity_signal": "Listed on T-Hub Portfolio"
                })
        except Exception as e:
            continue
            
    return startups
