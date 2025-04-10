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

# --- Step 1: Load course tree page ---
driver.get("https://courses.unisg.ch/event/event-hierarchy")
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
time.sleep(2)

# --- Step 2: Switch to German ---
print("🌐 Switching to Deutsch...")
de_element = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[normalize-space()='DE'])[1]")))
de_element.click()
time.sleep(3)

# --- Step 3: Navigate to 18MBIh ---
print("🎓 Navigating to 18MBIh...")
wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[normalize-space()='Master'])[1]"))).click()
time.sleep(2)
wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'18MBIh')])[1]"))).click()
time.sleep(3)

# --- Step 4: Expand All Nodes ---
print("🌲 Expanding all nodes...")

target_labels = [
    "Fachstudium", "Pflichtbereich", "Forschungsmethoden für Geschäftsinnovation",
    "Pflichtwahl- und Wahlbereich", "Forschungs-, Praxis-, Ventureprojekte / Issue Coverage",
    "ohne Vertiefung", "Business Development", "Digital Channel & Customer Relationship Management",
    "Start-up & Scale-up Entrepreneurship", "Supply Chain & Operations Management",
    "Technology Solution Architect", "Transforming and Managing Digital Business", "Methodenkurs",
    "Pflichtwahlbereich", "Wahlbereich", "Kontextstudium", "Fokusbereiche", "Skills"
]

clicked_paths = set()
max_idle_rounds = 5
idle_rounds = 0

while idle_rounds < max_idle_rounds:
    found_new = False
    nodes = driver.find_elements(By.CSS_SELECTOR, "mat-tree-node")

    for node in nodes:
        try:
            span_el = node.find_element(By.XPATH, ".//span[normalize-space()]")
            label = html.unescape(span_el.text.strip())

            if label not in target_labels:
                continue

            node_key = f"{label}_{node.get_attribute('aria-level')}_{node.get_attribute('aria-posinset')}"
            if node_key in clicked_paths:
                continue

            btn = node.find_element(By.XPATH, ".//button")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            btn.click()
            print(f"✅ Expanded: {label} (Level {node.get_attribute('aria-level')})")
            time.sleep(1)

            clicked_paths.add(node_key)
            found_new = True
        except Exception:
            continue

    if not found_new:
        idle_rounds += 1
        time.sleep(1)
    else:
        idle_rounds = 0

print("✅ Tree expansion completed.")

# --- Step 5: Extract and visit each course ---
print("🔍 Extracting courses and downloading PDFs...")

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Course Name', 'Course Number', 'Instructor', 'Link'])

    course_links = driver.find_elements(By.CLASS_NAME, "unisg-event-event-list-item__title")
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

            # --- Course Info ---
            try:
                course_name = driver.find_element(By.XPATH, "//h1").text.strip()
            except:
                course_name = text

            try:
                instructor = driver.find_element(By.XPATH, "//span[contains(text(),'Dozierende')]/following-sibling::span").text.strip()
            except:
                instructor = "N/A"

            course_number = href.split("/")[-1]
            writer.writerow([course_name, course_number, instructor, href])

            # --- Download Merkblatt ---
            try:
                # 
                merkblatt_link
                merkblatt_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "unisg-event-event-list-item__title")))
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
                    print("❌ Failed to download PDF.")
            except:
                print("ℹ️ No Merkblatt PDF found.")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error: {e}")
            try:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass

driver.quit()
print("✅ Done! CSV and PDFs saved.")