from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# قائمة لتجنب التكرار
visited_links = set()
extracted_emails = set()
social_links = set()

# أنماط البحث عن الإيميلات وروابط التواصل
EMAIL_PATTERN = r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
SOCIAL_PATTERN = r'(https?://(www\.)?(facebook|instagram|twitter|linkedin|tiktok)\.com/[^\s"<>]*)'


def scrape_website(url):
    global extracted_emails, social_links
    
    if url in visited_links:
        return  # تجنب التكرار
    
    visited_links.add(url)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # استخراج الإيميلات
    for mailto in re.findall(EMAIL_PATTERN, response.text):
        extracted_emails.add(mailto)
    
    # استخراج روابط التواصل
    for match in re.findall(SOCIAL_PATTERN, response.text):
        social_links.add(match[0])
    
    # البحث عن الروابط الداخلية وزحفها
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/'):
            href = url.rstrip('/') + href
        if href.startswith(url):
            scrape_website(href)


@app.route('/')
def scrape():
    global visited_links, extracted_emails, social_links
    
    url = "https://www.webuyestate.com/contact-us/"
    if not url:
        return jsonify({'error': 'يرجى إدخال رابط الموقع'}), 400
    
    # تصفير القوائم لكل طلب جديد
    visited_links.clear()
    extracted_emails.clear()
    social_links.clear()
    
    scrape_website(url)
    
    return jsonify({
        'emails': list(extracted_emails),
        'social_links': list(social_links)
    })

if __name__ == '__main__':
    app.run(debug=False,use_reloader=False)
