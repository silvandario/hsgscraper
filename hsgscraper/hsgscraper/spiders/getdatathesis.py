# Ausgeführt in separater Umgebung/ Spider
import os
import time
import csv
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

class HSGThesisScraper:
    def __init__(self):
        self.base_url = "https://universitaetstgallen.sharepoint.com/sites/EDOCDB/SitePages/en/Home.aspx"
        self.driver = self.setup_driver()
        self.data = []
        # Load any existing data
        self.load_existing_data()
        
    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def load_existing_data(self):
        """Load existing data from CSV if it exists."""
        try:
            with open("private_equity_theses.csv", 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.data = list(reader)
                print(f"Loaded {len(self.data)} existing thesis entries")
        except FileNotFoundError:
            print("No existing data file found, starting fresh")
            self.data = []

    def wait_and_find_element(self, by, value, timeout=20, clickable=False):
        """Wait for element and handle stale element exceptions."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if clickable:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, value))
                    )
                else:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, value))
                    )
                return element
            except StaleElementReferenceException:
                print(f"Stale element, retrying... ({value})")
                time.sleep(1)
                continue
            except TimeoutException:
                continue
        raise TimeoutException(f"Element {value} not found after {timeout} seconds")
    
    def wait_and_find_elements(self, by, value, timeout=20):
        """Wait for elements and handle stale element exceptions."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                elements = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((by, value))
                )
                if elements:
                    return elements
            except StaleElementReferenceException:
                print(f"Stale elements, retrying... ({value})")
                time.sleep(1)
                continue
            except TimeoutException:
                continue
        print(f"Warning: No elements found for {value} after {timeout} seconds")
        return []
    
    def login(self, username, password):
        """Log in to the HSG SharePoint site."""
        try:
            print("Navigating to login page...")
            self.driver.get(self.base_url)
            time.sleep(3)  # Wait for initial page load
            
            print("Entering username...")
            username_field = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "i0116"))
            )
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            print("Clicking Next...")
            next_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            )
            next_button.click()
            time.sleep(2)
            
            print("Entering password...")
            password_field = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "i0118"))
            )
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            print("Clicking Sign in...")
            sign_in_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            )
            sign_in_button.click()
            time.sleep(3)
            
            print("Handling 'Stay signed in' prompt...")
            try:
                stay_signed_in = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "idSIButton9"))
                )
                stay_signed_in.click()
                time.sleep(3)
            except:
                print("No 'Stay signed in' prompt found or already handled")
            
            print("Waiting for page load...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".mainContent, .ms-List-cell"))
            )
            
            print("Login successful!")
            return True
            
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def search_private_equity(self):
        """Search for Private Equity in the EDOK search bar."""
        try:
            print("Navigating to main EDOK page...")
            self.driver.get(self.base_url)
            time.sleep(5)  # Wait for page to fully load
            
            print("Searching for 'Private Equity'...")
            
            # EDOK-specific search box selectors
            edok_search_selectors = [
                ".mainContent input[type='search']",
                ".mainContent .ms-SearchBox-field",
                "input[placeholder*='Search documents']",
                "input[placeholder*='Search in EDOK']",
                "#edokSearchBox input",
                ".edokSection input[type='search']"
            ]
            
            search_box = None
            for selector in edok_search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            # Verify this is in the main content area
                            parent = self.driver.execute_script("""
                                let element = arguments[0];
                                while (element) {
                                    if (element.className.includes('mainContent')) return true;
                                    element = element.parentElement;
                                }
                                return false;
                            """, element)
                            
                            if parent:
                                search_box = element
                                print(f"Found EDOK search box with selector: {selector}")
                                break
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                print("Could not find EDOK search box")
                return False
            
            # Clear and perform search with explicit waits
            print("Clicking search box...")
            self.driver.execute_script("arguments[0].click();", search_box)
            time.sleep(2)
            
            print("Clearing search box...")
            search_box.clear()
            time.sleep(2)
            
            print("Entering search term...")
            search_box.send_keys("Private Equity")
            time.sleep(2)
            
            print("Submitting search...")
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results with multiple checks
            print("Waiting for search results...")
            max_attempts = 5
            for attempt in range(max_attempts):
                print(f"Attempt {attempt + 1} to verify results...")
                time.sleep(3)
                
                try:
                    # Check for document cards
                    results = self.driver.find_elements(By.CSS_SELECTOR, ".ms-DocumentCard, [role='listitem']")
                    visible_results = [r for r in results if r.is_displayed()]
                    
                    if visible_results:
                        print(f"Found {len(visible_results)} visible results")
                        # Print first result for verification
                        try:
                            print("\nFirst result content:")
                            print(visible_results[0].text[:200])
                        except:
                            print("Could not print result content")
                        return True
                    else:
                        print("No visible results yet")
                except Exception as e:
                    print(f"Error checking results: {e}")
                
            print("Could not verify search results after all attempts")
            return False
                
        except Exception as e:
            print(f"Error during Private Equity search: {e}")
            return False

    def extract_thesis_data_from_current_view(self):
        """Extract thesis data from the current view."""
        thesis_count = 0
        
        try:
            print("Waiting for thesis list to load...")
            time.sleep(5)
            
            # Get all thesis items using the list container XPath
            base_xpath = "/html/body/div[1]/div[2]/div[2]/div/div/div[3]/section/article/div/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div/div[3]/div/div/div/div/div/div[2]/div[3]/div/div/ul/li"
            thesis_items = self.driver.find_elements(By.XPATH, base_xpath)
            
            print(f"Found {len(thesis_items)} thesis items in current view")
            
            # Store theses for this page
            page_theses = []
            
            for i, item in enumerate(thesis_items):
                try:
                    print(f"\nProcessing item {i+1}/{len(thesis_items)}")
                    
                    # Extract data using relative XPaths
                    title = self._extract_title(item)
                    student_name, publishing_year, supervisor = self._extract_metadata(item)
                    
                    if title and title != "No title found":
                        thesis_data = {
                            'Title': title,
                            'Student Name': student_name,
                            'Publishing Year': publishing_year,
                            'Supervisor': supervisor
                        }
                        print("Extracted thesis:", thesis_data)
                        page_theses.append(thesis_data)
                        thesis_count += 1
                    
                except Exception as e:
                    print(f"Error processing individual thesis item: {e}")
                    continue
            
            # Save theses from this page immediately
            if page_theses:
                self.save_page_to_csv(page_theses)
                self.data.extend(page_theses)
            
            return thesis_count
            
        except Exception as e:
            print(f"Error extracting thesis data: {e}")
            return 0

    def save_page_to_csv(self, page_theses, filename=None):
        """Save theses from current page to CSV, creating file if it doesn't exist."""
        try:
            if filename is None:
                # Use absolute path in the EDOK folder
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                filename = os.path.join(base_dir, "private_equity_theses.csv")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Determine if we need to write header (new file)
            write_header = not os.path.exists(filename)
            
            # Open in append mode
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Title', 'Student Name', 'Publishing Year', 'Supervisor']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if write_header:
                    writer.writeheader()
                
                # Write all theses from this page
                for thesis in page_theses:
                    writer.writerow(thesis)
                
            # Create a backup copy every 50 theses
            if len(self.data) % 50 == 0:
                backup_filename = os.path.join(os.path.dirname(filename), f"private_equity_theses_backup_{len(self.data)}.csv")
                with open(backup_filename, 'w', newline='', encoding='utf-8') as backup_file:
                    writer = csv.DictWriter(backup_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.data)
                print(f"Created backup file: {backup_filename}")
                
            print(f"Saved {len(page_theses)} theses to {filename}")
            return True
                
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False

    def _extract_title(self, item):
        """Extract thesis title using relative XPath."""
        try:
            # Use relative XPath for title
            title_xpath = ".//span[1]/a"
            try:
                title_element = item.find_element(By.XPATH, title_xpath)
                if title_element and title_element.is_displayed():
                    title = title_element.text.strip()
                    if title:
                        print(f"Found title: {title}")
                        return title
            except:
                print("Could not find title with relative XPath")
            
            return "No title found"
            
        except Exception as e:
            print(f"Error extracting title: {e}")
            return "No title found"

    def _extract_metadata(self, item):
        """Extract metadata using specific XPaths."""
        try:
            student_name = "No student name"
            publishing_year = "No year"
            supervisor = "No supervisor"
            
            try:
                # Extract student name
                student_element = item.find_element(By.XPATH, ".//div[2]/span[2]")
                if student_element and student_element.is_displayed():
                    student_name = student_element.text.strip()
                    print(f"Found student name: {student_name}")
            except:
                print("Could not find student name")
            
            try:
                # Extract year
                year_element = item.find_element(By.XPATH, ".//div[2]/span[1]")
                if year_element and year_element.is_displayed():
                    publishing_year = year_element.text.strip()
                    print(f"Found year: {publishing_year}")
            except:
                print("Could not find year")
            
            try:
                # Extract supervisor using the correct span[4]
                supervisor_xpath = ".//div[2]/span[4]"
                supervisor_element = item.find_element(By.XPATH, supervisor_xpath)
                if supervisor_element and supervisor_element.is_displayed():
                    supervisor = supervisor_element.text.strip()
                    if supervisor:
                        print(f"Found supervisor: {supervisor}")
                    else:
                        print("Supervisor element found but text is empty")
            except:
                print("Could not find supervisor with primary xpath")
                # Try alternative approaches
                try:
                    # Try getting all spans in div[2] to debug
                    spans = item.find_elements(By.XPATH, ".//div[2]/span")
                    print(f"Found {len(spans)} spans in metadata div")
                    for i, span in enumerate(spans, 1):
                        print(f"Span {i} text: {span.text}")
                        # If this is the supervisor span (4th position)
                        if i == 4:
                            supervisor = span.text.strip()
                            print(f"Found supervisor in span {i}: {supervisor}")
                except Exception as e:
                    print(f"Error during spans analysis: {e}")
            
            return student_name, publishing_year, supervisor
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return "No student name", "No year", "No supervisor"

    def navigate_to_next_page(self):
        """Navigate to next page using specific XPath."""
        try:
            print("\nChecking for next page...")
            
            # Use specific XPath for next page button
            next_page_xpath = "/html/body/div[1]/div[2]/div[2]/div/div/div[3]/section/article/div/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div/div[3]/div/div/div/div/div/div[2]/div[3]/div/div/pnp-pagination/div/div/div/div/ul/li[4]/a"
            
            try:
                next_button = self.driver.find_element(By.XPATH, next_page_xpath)
                if next_button and next_button.is_displayed():
                    # Check if button is not disabled
                    disabled = next_button.get_attribute('disabled') or \
                             'disabled' in next_button.get_attribute('class') or \
                             next_button.get_attribute('aria-disabled') == 'true'
                    
                    if not disabled:
                        print("Found enabled next page button")
                        
                        # Scroll the button into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(1)
                        
                        # Try to click using different methods
                        try:
                            next_button.click()
                        except:
                            try:
                                self.driver.execute_script("arguments[0].click();", next_button)
                            except:
                                print("Could not click next button")
                                return False
                        
                        print("Clicked next page button")
                        
                        # Wait for page to load
                        time.sleep(5)
                        
                        # Verify page changed
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".ms-List-cell, [role='listitem']"))
                            )
                            print("New page loaded successfully")
                            return True
                        except:
                            print("Could not verify new page loaded")
                            return False
                    else:
                        print("Next page button is disabled - likely on last page")
                        return False
                else:
                    print("Next page button not visible")
                    return False
                    
            except Exception as e:
                print(f"Error finding next page button with XPath: {e}")
                
                # Fallback to previous method if XPath fails
                print("Trying fallback pagination method...")
                pagination_selectors = [
                    "div[class*='Pagination']",
                    "[role='navigation']",
                    ".ms-Pagination"
                ]
                
                for selector in pagination_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            next_buttons = element.find_elements(By.CSS_SELECTOR, "[aria-label*='Next']")
                            for button in next_buttons:
                                if button.is_displayed() and not "disabled" in button.get_attribute("class"):
                                    button.click()
                                    time.sleep(5)
                                    print("Used fallback method to navigate to next page")
                                    return True
                
                print("Could not find next page button with any method")
                return False
                
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            return False
    
    def scrape_all_pages(self):
        """Scrape all pages of thesis data."""
        page_num = 1
        total_theses = 0
        
        while True:
            print(f"Processing page {page_num}...")
            count = self.extract_thesis_data_from_current_view()
            total_theses += count
            print(f"Found {count} theses on this page. Total so far: {total_theses}")
            
            time.sleep(random.uniform(2, 4))
            
            if not self.navigate_to_next_page():
                print("No more pages available")
                break
                
            page_num += 1
        
        return total_theses
    
    def save_to_csv(self, filename="private_equity_theses.csv"):
        """Save data to CSV, appending to existing file if it exists."""
        try:
            mode = 'a' if os.path.exists(filename) else 'w'
            with open(filename, mode, newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Title', 'Student Name', 'Publishing Year', 'Supervisor']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if mode == 'w':  # Only write header for new file
                    writer.writeheader()
                
                # Only write new data
                existing_entries = set()
                if mode == 'a':
                    with open(filename, 'r', newline='', encoding='utf-8') as existing_file:
                        reader = csv.DictReader(existing_file)
                        for row in reader:
                            entry_key = f"{row['Title']}-{row['Student Name']}-{row['Publishing Year']}"
                            existing_entries.add(entry_key)
                
                new_entries = 0
                for thesis in self.data:
                    entry_key = f"{thesis['Title']}-{thesis['Student Name']}-{thesis['Publishing Year']}"
                    if entry_key not in existing_entries:
                        writer.writerow(thesis)
                        new_entries += 1
                
                print(f"Saved {new_entries} new entries to {filename}")
                return True
                
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    
    def run(self, username, password):
        """Run complete scraping process."""
        try:
            if not self.login(username, password):
                print("Login failed. Aborting.")
                return False
            
            if not self.search_private_equity():
                print("Failed to search for Private Equity. Aborting.")
                return False
            
            total_theses = self.scrape_all_pages()
            print(f"Scraped a total of {total_theses} theses")
            
            self.save_to_csv()
            
            return True
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return False
        finally:
            if self.driver:
                print("Closing browser...")
                self.driver.quit()


if __name__ == "__main__":
    username = "niklas.millarg@student.unisg.ch"
    password = "6THiAGO22%"
    
    scraper = HSGThesisScraper()
    scraper.run(username, password)