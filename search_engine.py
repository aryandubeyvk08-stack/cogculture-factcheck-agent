import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def search_ddg_html(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    """
    Direct DuckDuckGo HTML scraping - no API key required, zero external dependencies beyond bs4.
    """
    results = []
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, "html.parser")
            
            for item in soup.find_all("div", class_="result"):
                title_elem = item.find("a", class_="result__a")
                snippet_elem = item.find("a", class_="result__snippet")
                url_elem = item.find("a", class_="result__url")
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    link = title_elem.get("href", "")
                    # Clean DDG redirect URL if needed
                    if "/l/?" in link and "uddg=" in link:
                        parsed_link = urllib.parse.parse_qs(urllib.parse.urlparse(link).query).get("uddg", [link])[0]
                    else:
                        parsed_link = link
                        
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": parsed_link
                    })
                    if len(results) >= max_results:
                        break
    except Exception:
        pass
    return results

def search_wikipedia_api(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Wikipedia OpenSearch & Summary API - fast, reliable, rate-limit friendly, zero auth required.
    """
    results = []
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit={max_results}&namespace=0&format=json"
        req = urllib.request.Request(search_url, headers={"User-Agent": "FactCheckBot/1.0 (assessment@cogculture.agency)"})
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode('utf-8'))
            titles = data[1]
            descriptions = data[2]
            urls = data[3]
            for title, desc, url in zip(titles, descriptions, urls):
                results.append({
                    "title": f"Wikipedia: {title}",
                    "snippet": desc if desc else title,
                    "url": url
                })
    except Exception:
        pass
    return results

def search_tavily(query: str, api_key: str, max_results: int = 4) -> List[Dict[str, str]]:
    """
    Tavily Search API integration (if user provides a Tavily key).
    """
    results = []
    try:
        url = "https://api.tavily.com/search"
        payload = json.dumps({
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            for res in data.get("results", []):
                results.append({
                    "title": res.get("title", ""),
                    "snippet": res.get("content", ""),
                    "url": res.get("url", "")
                })
    except Exception:
        pass
    return results

def live_web_search(query: str, tavily_api_key: str = None) -> List[Dict[str, str]]:
    """
    Unified multi-source live web search aggregator.
    Tries Tavily (if key provided), then DDG HTML, then Wikipedia API.
    """
    results = []
    if tavily_api_key:
        results = search_tavily(query, tavily_api_key)
        if results:
            return results

    # Try DDG
    results = search_ddg_html(query)
    if results:
        return results

    # Try Wikipedia
    results = search_wikipedia_api(query)
    return results
