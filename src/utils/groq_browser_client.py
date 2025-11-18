"""Groq client with multi-page web crawling."""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from groq import Groq


class GroqBrowserClient:
    """Client with crawling capabilities."""

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "moonshotai/kimi-k2-instruct-0905"

    def scrape_page(self, url: str) -> str:
        """Fetch and extract text from a webpage."""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            return text[:50000]
        except:
            return ""

    def crawl_site(self, start_url: str, max_pages: int = 5) -> list:
        """Crawl multiple pages from a website.
        
        Returns list of (url, content) tuples.
        """
        domain = urlparse(start_url).netloc
        visited = set()
        to_visit = [start_url]
        pages = []
        
        while to_visit and len(pages) < max_pages:
            url = to_visit.pop(0)
            
            if url in visited:
                continue
            
            visited.add(url)
            
            # Scrape this page
            content = self.scrape_page(url)
            if content:
                pages.append((url, content))
            
            # Find more links on this page (only from same domain)
            try:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0'
                })
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    link_domain = urlparse(full_url).netloc
                    
                    # Only follow links within same domain
                    if link_domain == domain and full_url not in visited:
                        to_visit.append(full_url)
            except:
                pass
        
        return pages

    def find_license_links(self, url: str) -> list:
        """Find license-related links on a page."""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            keywords = ['license', 'licence', 'copyright', 'terms', 'legal', 'open-licence']
            links = []
            
            for a in soup.find_all('a', href=True):
                href = a.get('href', '').lower()
                text = a.get_text().lower()

                if any(k in href or k in text for k in keywords):
                    full_url = urljoin(url, a['href'])

                    score = 0
                    # Check both href and text for scoring
                    combined = href + ' ' + text
                    if 'open-licence' in combined or 'open-license' in combined:
                        score = 10
                    elif 'licence' in combined or 'license' in combined:
                        score = 8
                    elif 'copyright' in combined:
                        score = 5
                    elif 'terms' in combined:
                        score = 3

                    if full_url not in [l[0] for l in links]:
                        links.append((full_url, score))
            
            links.sort(key=lambda x: x[1], reverse=True)
            return [url for url, score in links[:5]]
        except:
            return []

    def analyze(self, text: str, prompt: str) -> str:
        """Analyze text using Groq."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": f"{prompt}\n\nContent:\n{text}"
                }],
                temperature=0.1,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
