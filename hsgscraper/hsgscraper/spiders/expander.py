import time
import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Setup Chrome ---
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# --- Load course tree page ---
driver.get("https://courses.unisg.ch/event/event-hierarchy")
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
time.sleep(3)

# --- Switch to German ---
print("🌐 Switching to Deutsch...")
de_element = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[normalize-space()='DE'])[1]")))
de_element.click()
time.sleep(5)

# --- Open 18MBIh ---
print("🎓 Navigating to 18MBIh...")
master_element = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[normalize-space()='Master'])[1]")))
master_element.click()
time.sleep(2)

mbi_program = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'18MBIh')])[1]")))
mbi_program.click()
time.sleep(3)

# --- Tree Expansion ---
print("🌲 Expanding all nodes...")

target_labels = [
   "Fachstudium", "Pflichtbereich", "Forschungsmethoden für Geschäftsinnovation",
   "Pflichtwahl- und Wahlbereich", "Forschungs-, Praxis-, Ventureprojekte / Issue Coverage",
   "ohne Vertiefung", "Business Development", "Digital Channel & Customer Relationship Management",
   "Start-up & Scale-up Entrepreneurship", "Supply Chain & Operations Management",
   "Technology Solution Architect", "Transforming and Managing Digital Business", "Methodenkurs",
   "Business Development", "Digital Channel & Customer Relationship Management",
   "Start-up & Scale-up Entrepreneurship", "Transforming and Managing Digital Business",
   "Pflichtwahlbereich", "ohne Vertiefung", "Business Development",
   "Digital Channel & Customer Relationship Management", "Start-up & Scale-up Entrepreneurship",
   "Supply Chain & Operations Management", "Technology Solution Architect",
   "Transforming and Managing Digital Business", "Wahlbereich", "Kontextstudium",
   "Fokusbereiche", "Skills"
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
           print(f"✅ Expanded: {label} (level {node.get_attribute('aria-level')})")
           time.sleep(1.2)

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

# --- Log visible child nodes of Pflichtwahlbereich ---
print("\n🔍 Checking child nodes under 'Pflichtwahlbereich':")
child_nodes = driver.find_elements(By.XPATH, "//mat-tree-node[.//span[normalize-space()='Pflichtwahlbereich']/parent::mat-tree-node]/following-sibling::mat-tree-node")

for node in child_nodes:
   try:
       level = node.get_attribute("aria-level")
       label = html.unescape(node.find_element(By.XPATH, ".//span[normalize-space()]").text.strip())
       if level == "6":
           print(f"  - {label}")
   except:
       continue

# --- Pause for inspection ---
print("\n🔎 Browser is now open for manual inspection (5 minutes)...")
time.sleep(300)

# Optional: Quit browser when ready
# driver.quit()