import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

# Load sensitive data from environment variables
COOKIE = os.getenv("OLYMPICS_COOKIE", "YOUR_COOKIE_HERE")

# Paris 2024 Olympics Highlights URL
URL = "https://olympics.com/en/paris-2024/videos/list/highlights"

# Headers for the request
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "cookie": COOKIE,
    "referer": "https://olympics.com/en/",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.8",
}

# Initialize the Flask app
app = Flask(__name__)


def fetch_highlights():
    """Fetch highlights from the Paris 2024 Olympics page."""
    try:
        session = requests.Session()
        response = session.get(URL, headers=HEADERS)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None


def parse_highlights(html_content):
    """Parse the highlights from the page content using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'lxml')
    highlights = []

    # Locate the section that contains the videos
    table = soup.find('section', {
        'class': 'Grid-styles__GridContainer-sc-57f17f60-0 gaYTef grid__column--8-xl min-height-container'
    })

    if table:
        rows = table.findAll('div', {
            'class': 'AllVideosGroup-styles__CardItemWrapper-sc-676df772-2 fwAJO all-videos-card-item'
        })
        for row in rows:
            try:
                title = row.find(
                    'h3', {'data-cy': 'title'}).get_text(strip=True)
                description = row.find(
                    'span', {'data-cy': 'with-read-more-content'}).get_text(strip=True)
                image_url = row.find('img')['src']
                video_link = row.find('a', {'data-cy': 'link'})['href']

                highlights.append({
                    'title': title,
                    'description': description,
                    'image_url': image_url,
                    'video_link': f"https://olympics.com{video_link}"
                })
            except (AttributeError, KeyError, TypeError):
                continue  # Skip if any element is missing or invalid
    return highlights


@app.route('/api/highlights', methods=['GET'])
def get_highlights():
    """API endpoint to fetch and return highlights."""
    html_content = fetch_highlights()
    if not html_content:
        return jsonify({"error": "Failed to fetch highlights"}), 500

    highlights = parse_highlights(html_content)
    if not highlights:
        return jsonify({"message": "No highlights found"}), 404

    return jsonify(highlights)


if __name__ == '__main__':
    app.run(debug=True)
