from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI(title="Solar Leads Scraper")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Solar Leads Scraper</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f9; color: #333; text-align: center; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                h1 { color: #f39c12; }
                input[type="text"] { width: 90%; padding: 12px; margin: 20px 0; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; }
                button { background-color: #f39c12; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
                button:hover { background-color: #e67e22; }
                .footer { margin-top: 20px; font-size: 12px; color: #7f8c8d; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>☀️ Solar Leads Scraper Live!</h1>
                <p>Apna target website URL niche dalein aur 'Scrape Leads' par click karein:</p>
                <form action="/scrape" method="get">
                    <input type="text" name="url" placeholder="https://example-solar-website.com" required>
                    <br>
                    <button type="submit">Scrape Leads</button>
                </form>
                <div class="footer">Powered by Coolify & Oracle Cloud</div>
            </div>
        </body>
    </html>
    """

@app.get("/scrape")
def scrape(url: str = Query(..., description="URL of the website to scrape")):
    try:
        # Website ko block karne se rokne ke liye headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": f"Website ne respond nahi kiya. Status code: {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Emails nikalne ke liye Regex
        emails = list(set(re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+\.[a-zA-Z,0-9.]+', response.text)))
        
        # 2. Phone numbers nikalne ke liye Basic Regex
        phones = list(set(re.findall(r'\+?\d[\d\s\-]{8,14}\d', response.text)))
        
        # 3. Company Name / Title
        title = soup.title.string if soup.title else "No Title Found"
        
        # 4. Solar aur Contact se jude links dhoodhna
        solar_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'solar' in href.lower() or 'contact' in href.lower() or 'about' in href.lower():
                # Agar relative link hai toh full domain jodna
                if href.startswith('/'):
                    solar_links.append(url.rstrip('/') + href)
                else:
                    solar_links.append(href)
        
        return {
            "status": "Success",
            "target_url": url,
            "company_name": title.strip() if title else "",
            "emails_found": emails,
            "phone_numbers_found": phones[:15],  # Top 15 numbers
            "useful_links": list(set(solar_links))[:10]  # Top 10 links
        }
        
    except Exception as e:
        return {"status": "Failed", "error": f"Kuch gadbad hui: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
