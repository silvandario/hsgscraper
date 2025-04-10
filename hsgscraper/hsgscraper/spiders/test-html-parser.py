import requests
from bs4 import BeautifulSoup

# Set the target URL
url = 'https://www.triathlete.com/training/10-hour-week-ironman-training-plan/'  # Replace with the site you want to scrape

# Send a GET request to the URL
response = requests.get(url)

# Check if request was successful
if response.status_code == 200:
    # Get the raw HTML
    html_content = response.text

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract plain text by removing all HTML tags
    plain_text = soup.get_text(separator='\n', strip=True)

    # Print the plain text
    print(plain_text)

    # Save to a file
    with open('site_text.txt', 'w', encoding='utf-8') as f:
        f.write(plain_text)

    print("✅ Text content successfully extracted and saved to 'site_text.txt'")
else:
    print(f"❌ Failed to retrieve page. Status code: {response.status_code}")