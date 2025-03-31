import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import requests
import os

# Chrome Setup
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
# options.add_argument("--headless=new")

# Anti-detection measures
driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Target URL
url = "https://courses.unisg.ch/event/event-hierarchy"
driver.get(url)

# Create WebDriverWait object with longer timeout
wait = WebDriverWait(driver, 20)

# CSV setup
csv_filename = 'course_links.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Course Name', 'Course Number', 'Instructor', 'Link'])

    try:
        print("Loading page...")
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        time.sleep(3)  # Give extra time for Angular to initialize
        
        # Switch to Deutsch
        print("Switching to Deutsch...")
        # (//span[normalize-space()='DE'])[1]
        de_element = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//span[normalize-space()='DE'])[1]")))
        de_element.click()
        time.sleep(7)
        
        # Click on Master dropdown
        print("Clicking on Master dropdown...")
        master_element = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//span[normalize-space()='Master'])[1]")))
        master_element.click()
        time.sleep(2)
        # and scroll down a bit
        driver.execute_script("window.scrollTo(0, 500)")
        time.sleep(2)

        # Click on the specific Master program
        print("Selecting Master program...")
        master_program = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//span[normalize-space()='Master of Arts in Business Innovation (18MBIh)'])[1]")))
        master_program.click()
        time.sleep(2)

        # Click on Fachstudium
        print("Clicking on Fachstudium...")
        fachstudium = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//span[normalize-space()='Fachstudium'])[1]")))
        fachstudium.click()
        time.sleep(2)

        # Click on Pflichtbereich
        print("Clicking on Pflichtbereich...")
        pflichtbereich = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//span[normalize-space()='Pflichtbereich'])[1]")))
        pflichtbereich.click()
        time.sleep(2)

        # Click on Reporting & Auditing
        print("Clicking on Reporting & Auditing...")
        reporting = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//span[normalize-space()='Forschungsmethoden für Geschäftsinnovation'])[1]")))
        reporting.click()
        time.sleep(3)

        # Wait for the course table to load
        print("Waiting for course table to load...")
        # Select Kursmerkblatt (//a[normalize-space()='Merkblatt'])[1]
        kursmerkblatt = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//a[normalize-space()='Forschungsmethoden für Geschäftsinnovation'])[1]")))
        
        # Extract course information directly from the table
        print("Extracting course information...")
        
        # Get the link of the kursmekr^rkblatt
        kursmerkblatt_link = kursmerkblatt.get_attribute("href")
        print(kursmerkblatt_link)
        # Write to CSV in Form of link 1, link
        writer.writerow(["Forschungsmethoden für Geschäftsinnovation", "18MBIh", "Prof. Dr. Stefan Feuerriegel", kursmerkblatt_link])
        
        # Click on the kursmerkblatt
        kursmerkblatt.click()
        time.sleep(3)
        
        # click on (//a[normalize-space()='Merkblatt'])[1]
        merkblatt = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//a[normalize-space()='Merkblatt'])[1]")))
        merkblatt.click()
        time.sleep(3)
        
        # print the pdf link
        pdf_link = driver.current_url
        print(pdf_link)
        time.sleep(3)
        # Speicherpfad und Dateiname
        pdf_output_dir = "pdfs"
        os.makedirs(pdf_output_dir, exist_ok=True)
        pdf_output_path = os.path.join(pdf_output_dir, "forschungsmethoden_merblatt.pdf")

        # PDF herunterladen und speichern
        response = requests.get(pdf_link)
        if response.status_code == 200:
            with open(pdf_output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ PDF gespeichert unter: {pdf_output_path}")
        else:
            print(f"❌ Fehler beim Herunterladen: Status {response.status_code}")
        
        # download the pdf
        print("Downloading the PDF...")
        
        

        
        
        
        
    except TimeoutException:
        print("Timed out waiting for page elements to load.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        driver.quit()
        print("Browser closed.")
# print("\n📊 To run without interruption on macOS:")
# print("caffeinate -i python improved_course_scraper.py")