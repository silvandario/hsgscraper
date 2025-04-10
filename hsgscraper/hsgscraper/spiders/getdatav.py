import os
import time
import csv
import html
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Setup paths ---
csv_filename = '18MBI_courses.csv'
pdf_output_dir = os.path.join("pdfs", "18MBI")
os.makedirs(pdf_output_dir, exist_ok=True)

# --- Setup Chrome ---
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# --- Open site ---
driver.get("https://courses.unisg.ch/event/event-hierarchy")
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
time.sleep(3)

# --- Switch to German ---
print("🌐 Switching to Deutsch...")
wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[normalize-space()='DE'])[1]"))).click()
time.sleep(5)

# --- Navigate to 18MBIh ---
print("🎓 Opening 18MBIh program...")
wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[normalize-space()='Master'])[1]"))).click()
time.sleep(1)
wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'18MBIh')])[1]"))).click()
time.sleep(3)

# --- Assume tree is already unfolded (from previous expansion script) ---

# --- Start CSV ---
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
   writer = csv.writer(csvfile)
   writer.writerow(['Course Name', 'Course Number', 'Instructor', 'Link'])

   print("🔍 Searching for course links...")
   course_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/event/show/')]")
   visited = set()

   for link in course_links:
       try:
           href = link.get_attribute("href")
           text = link.text.strip()

           if not href or href in visited or not text:
               continue
           visited.add(href)

           print(f"➡️ Visiting: {text}")
           driver.execute_script("window.open(arguments[0]);", href)
           driver.switch_to.window(driver.window_handles[1])
           wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
           time.sleep(2)

           # Extract course info
           try:
               course_name = driver.find_element(By.XPATH, "//h1").text.strip()
           except:
               course_name = text

           try:
               instructor = driver.find_element(By.XPATH, "//span[contains(text(),'Dozierende')]/following-sibling::span").text.strip()
           except:
               instructor = "N/A"

           course_number = href.split("/")[-1]

           # Save to CSV
           writer.writerow([course_name, course_number, instructor, href])

           # Try downloading Merkblatt
           try:
               merkblatt_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Merkblatt']")))
               merkblatt_link.click()
               time.sleep(2)

               pdf_url = driver.current_url
               response = requests.get(pdf_url)
               if response.status_code == 200:
                   safe_title = course_name.replace(" ", "_").replace("/", "_").strip()[:80]
                   pdf_path = os.path.join(pdf_output_dir, f"{safe_title}.pdf")
                   with open(pdf_path, 'wb') as f:
                       f.write(response.content)
                   print(f"📥 PDF saved: {pdf_path}")
               else:
                   print("❌ Failed to download Merkblatt PDF.")
           except:
               print("ℹ️ No Merkblatt PDF found.")

           driver.close()
           driver.switch_to.window(driver.window_handles[0])
           time.sleep(1)

       except Exception as e:
           print(f"❌ Error visiting course page: {e}")
           try:
               driver.close()
               driver.switch_to.window(driver.window_handles[0])
           except:
               pass

driver.quit()
print("✅ All done! Data saved to CSV and PDFs downloaded.")