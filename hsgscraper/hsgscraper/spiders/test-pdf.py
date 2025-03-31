import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download_course_pdf():
    # Create download directory if it doesn't exist
    download_dir = os.path.join(os.getcwd(), "pdfs")
    os.makedirs(download_dir, exist_ok=True)
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True  # Force download PDF instead of opening
    })
    
    # Uncomment for headless mode if needed
    # chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the page
        url = "https://courses.unisg.ch/event/events/by-term/578663a7-e4fc-4b04-8ed9-0d43ef1e9d46/14690301"
        driver.get(url)
        
        # Wait for page to load (adjust timeout as needed)
        time.sleep(5)
        
        # Find all links on the page
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Found {len(all_links)} links on the page")
        
        # Look for PDF links or document links
        pdf_found = False
        for link in all_links:
            href = link.get_attribute("href")
            text = link.text
            
            # Print link details for debugging
            if href:
                print(f"Link: {text} -> {href}")
            
            # Check if it's a PDF link or something that looks like course material
            if href and (href.endswith('.pdf') or "material" in href.lower() or 
                        "document" in href.lower() or "download" in href.lower() or
                        "merkblatt" in href.lower()):
                print(f"Found potential document link: {href}")
                try:
                    # Click the link to download
                    link.click()
                    pdf_found = True
                    print(f"Clicked on link: {text}")
                    # Wait for download to start
                    time.sleep(3)
                except Exception as e:
                    print(f"Failed to click link: {e}")
        
        if not pdf_found:
            print("No PDF links found. Let's try to screenshot the page for analysis.")
            driver.save_screenshot("pdfs/page_screenshot.png")
            print("Screenshot saved to pdfs/page_screenshot.png")
            
            # Dump page source for analysis
            with open("pdfs/page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Page source saved to pdfs/page_source.html")
            
    finally:
        # Close the browser
        time.sleep(5)  # Give time for downloads to complete
        driver.quit()
    
    # Check if any PDFs were downloaded
    pdf_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
    if pdf_files:
        print(f"PDFs downloaded: {pdf_files}")
    else:
        print("No PDFs were downloaded")

if __name__ == "__main__":
    download_course_pdf()