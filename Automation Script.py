import os
import time
import shutil
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

class LeadTechAutomation:
    def __init__(self):
        self.base_url = "https://dev.leadtech.in/survey/login"
        self.username = "user_name"
        self.password = "passward"
        self.download_dir = r"D:\Priyanshu_Data\UP_400\Merge Excel"
        self.driver = None
        self.wait = None
        
        # List of project S.No to process - always process S.No 1 first
        self.project_serial_numbers = [9,8,7,6,10,5,4,3,2,1]  # Add more as needed
        
    def setup_driver(self):
        """Setup Chrome driver with download preferences"""
        chrome_options = Options()
        
        # Setup download directory
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-notifications")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)
        
    def login(self):
        """Login to the application"""
        print("🔐 Logging in...")
        self.driver.get(self.base_url)
        time.sleep(2)
        
        try:
            # Enter username
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(5)
            print("✅ Login successful!")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def navigate_to_response(self):
        """Navigate to Response page"""
        print("📋 Navigating to Response page...")
        try:
            # Click on Response link
            response_link = self.wait.until(
                EC.element_to_be_clickable((By.ID, "response-link"))
            )
            response_link.click()
            time.sleep(5)
            print("✅ Navigated to Response page")
            return True
        except Exception as e:
            print(f"❌ Failed to navigate to Response: {e}")
            return False
    
    def click_view_projects(self, client_id="CLIENT0011"):
        """Click on View Projects button for a specific client"""
        print(f"👁️ Clicking View Projects for client: {client_id}")
        try:
            # Find the button with onclick containing the client ID
            view_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(@onclick, '{client_id}')]"))
            )
            view_button.click()
            time.sleep(5)
            print(f"✅ Clicked View Projects for {client_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to click View Projects: {e}")
            return False
    
    def click_project_by_serial(self, serial_number):
        """Click on View Surveys button for a project by serial number"""
        print(f"🔢 Processing project S.No: {serial_number}")
        try:
            # Find the row with the given serial number
            row = self.wait.until(
                EC.presence_of_element_located((By.XPATH, f"//td[text()='{serial_number}']/.."))
            )
            
            # Find the View Surveys button in that row
            view_button = row.find_element(By.CSS_SELECTOR, "button.view-project-surveys")
            project_name = view_button.get_attribute("data-project-name")
            project_id = view_button.get_attribute("data-project-id")
            
            print(f"📁 Found project: {project_name} (ID: {project_id})")
            view_button.click()
            time.sleep(5)
            
            return {"project_name": project_name, "project_id": project_id}
            
        except Exception as e:
            print(f"❌ Failed to click project {serial_number}: {e}")
            return None
    
    def click_view_responses(self, survey_name):
        """Click on View Responses for a specific survey - ALWAYS clicks S.No 1"""
        print(f"📊 Clicking View Responses for survey: {survey_name}")
        try:
            # First, find the table body
            table_body = self.wait.until(
                EC.presence_of_element_located((By.ID, "surveyTableBody"))
            )
            
            # Find the first row (S.No 1) in the table
            first_row = table_body.find_element(By.XPATH, "./tr[1]")
            
            # Find the View Responses element in the first row
            # The view-responses is a <p> tag with class "view-responses"
            view_responses_p = first_row.find_element(By.CSS_SELECTOR, "p.view-responses")
            
            # Click on the span inside the p tag
            view_responses_span = view_responses_p.find_element(By.CSS_SELECTOR, "span")
            
            # Scroll to element and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", view_responses_span)
            time.sleep(1)
            
            # Try clicking with JavaScript if normal click fails
            try:
                view_responses_span.click()
            except:
                self.driver.execute_script("arguments[0].click();", view_responses_span)
            
            time.sleep(5)
            print(f"✅ Clicked View Responses for {survey_name} (S.No 1)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to click View Responses: {e}")
            # Try alternative method
            try:
                # Alternative: Find by data-survey attribute
                view_element = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//p[@class='view-responses' and @data-survey='{survey_name}']/span"))
                )
                self.driver.execute_script("arguments[0].click();", view_element)
                time.sleep(5)
                print(f"✅ Clicked View Responses using alternative method")
                return True
            except:
                print(f"❌ Alternative method also failed")
                return False
    
    def click_view_responses_by_serial(self, serial_number=1):
        """Click on View Responses for a survey by serial number in the survey table"""
        print(f"📊 Clicking View Responses for survey S.No: {serial_number}")
        try:
            # Find the table body
            table_body = self.wait.until(
                EC.presence_of_element_located((By.ID, "surveyTableBody"))
            )
            
            # Find the row with the given serial number
            row = table_body.find_element(By.XPATH, f"./tr[{serial_number}]")
            
            # Find the View Responses element in that row
            view_responses_p = row.find_element(By.CSS_SELECTOR, "p.view-responses")
            view_responses_span = view_responses_p.find_element(By.CSS_SELECTOR, "span")
            
            # Scroll to element and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", view_responses_span)
            time.sleep(1)
            
            # Click using JavaScript
            self.driver.execute_script("arguments[0].click();", view_responses_span)
            
            time.sleep(5)
            print(f"✅ Clicked View Responses for S.No {serial_number}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to click View Responses for S.No {serial_number}: {e}")
            return False
    
    def download_excel_with_media(self):
        """Download Excel with Media"""
        print("📥 Downloading Excel with Media...")
        try:
            # Find the export dropdown
            export_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "sort"))
            )
            
            # Click to open dropdown
            export_dropdown.click()
            time.sleep(1)
            
            # Select Excel with Media option
            excel_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//option[@value='excelWithMedia']"))
            )
            excel_option.click()
            time.sleep(2)
            
            # Wait for download to complete
            print("⏳ Waiting for download to complete...")
            time.sleep(10)
            
            print("✅ Excel download initiated")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download Excel: {e}")
            return False
    
    def get_survey_name_and_count(self):
        """Get survey name and total responses from the header"""
        try:
            header_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "anofield"))
            )
            header_text = header_element.text
            
            # Extract survey name and total responses
            survey_name_match = re.search(r"Survey Responses:\s*(.+?)(?:\n|$)", header_text)
            total_match = re.search(r"Total Responses:\s*(\d+)", header_text)
            
            survey_name = survey_name_match.group(1).strip() if survey_name_match else "unknown"
            total_responses = int(total_match.group(1)) if total_match else 0
            
            return survey_name, total_responses
            
        except Exception as e:
            print(f"❌ Failed to get survey info: {e}")
            return "unknown", 0
    
    def create_folder_for_survey(self, survey_name):
        """Create folder structure for survey"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        folder_path = os.path.join(self.download_dir, date_str, survey_name)
        os.makedirs(folder_path, exist_ok=True)
        print(f"📁 Created folder: {folder_path}")
        return folder_path
    
    def rename_and_move_downloaded_file(self, survey_name, folder_path):
        """Rename and move the downloaded Excel file to the survey folder"""
        try:
            # Wait for download to complete
            time.sleep(3)
            
            # Find the most recent downloaded Excel file
            files = [f for f in os.listdir(self.download_dir) if f.endswith('.xlsx')]
            if not files:
                print("⚠️ No Excel file found in download directory")
                return False
            
            # Get the most recent file
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.download_dir, x)), reverse=True)
            latest_file = files[0]
            source_path = os.path.join(self.download_dir, latest_file)
            
            # Create new filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_filename = f"{survey_name}_{date_str}.xlsx"
            dest_path = os.path.join(folder_path, new_filename)
            
            # Move file
            shutil.move(source_path, dest_path)
            print(f"✅ File saved: {dest_path}")
            return dest_path
            
        except Exception as e:
            print(f"❌ Failed to move file: {e}")
            return False
    
    def navigate_back_to_client(self):
        """Navigate back to Client page"""
        print("🔙 Navigating back to Client page...")
        try:
            # Click on CLIENT0011 breadcrumb
            client_link = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(@onclick, 'viewClientProjects(\'CLIENT0011\')')]")
                )
            )
            client_link.click()
            time.sleep(5)
            print("✅ Navigated back to Client page")
            return True
        except Exception as e:
            print(f"❌ Failed to navigate back: {e}")
            # Try direct navigation
            try:
                self.driver.get("https://dev.leadtech.in/survey/responses")
                time.sleep(5)
                self.click_view_projects("CLIENT0011")
                return True
            except:
                return False
    
    def process_single_project(self, serial_number):
        """Process a single project through the entire workflow"""
        print(f"\n{'='*60}")
        print(f"🎯 Processing Project S.No: {serial_number}")
        print(f"{'='*60}")
        
        try:
            # Click on project by serial number
            project_info = self.click_project_by_serial(serial_number)
            if not project_info:
                return False
            
            project_name = project_info["project_name"]
            
            # Wait for page to load
            time.sleep(3)
            
            # Get survey name from the header (if available)
            survey_name, total_responses = self.get_survey_name_and_count()
            
            # If no survey name found, try to get it from the table
            if survey_name == "unknown":
                try:
                    # Get survey name from first row
                    table_body = self.wait.until(
                        EC.presence_of_element_located((By.ID, "surveyTableBody"))
                    )
                    first_row = table_body.find_element(By.XPATH, "./tr[1]")
                    survey_name_element = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(2) span")
                    survey_name = survey_name_element.text.strip()
                    
                    # Get response count from the same row
                    response_element = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(3) .response-count")
                    total_responses = int(response_element.text.strip()) if response_element.text.strip().isdigit() else 0
                    
                    print(f"📊 Found survey: {survey_name} with {total_responses} responses")
                except Exception as e:
                    print(f"⚠️ Could not get survey info from table: {e}")
            
            if total_responses == 0:
                print(f"⚠️ No responses found for {survey_name}, skipping...")
                self.navigate_back_to_client()
                return True
            
            # Click on View Responses - ALWAYS click S.No 1
            if not self.click_view_responses_by_serial(1):
                # Try alternative method
                if not self.click_view_responses(survey_name):
                    self.navigate_back_to_client()
                    return False
            
            # Create folder for this survey
            folder_path = self.create_folder_for_survey(survey_name)
            
            # Download Excel with Media
            if not self.download_excel_with_media():
                self.navigate_back_to_client()
                return False
            
            # Rename and move the downloaded file
            if not self.rename_and_move_downloaded_file(survey_name, folder_path):
                self.navigate_back_to_client()
                return False
            
            # Navigate back to client page
            self.navigate_back_to_client()
            
            print(f"✅ Completed processing for {survey_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing project {serial_number}: {e}")
            self.navigate_back_to_client()
            return False
    
    def merge_all_excel_files(self):
        """Merge all Excel files from the day's folder"""
        print("\n📊 Merging all Excel files...")
        date_str = datetime.now().strftime("%Y-%m-%d")
        base_folder = os.path.join(self.download_dir, date_str)
        
        if not os.path.exists(base_folder):
            print("❌ No folder found for today's date")
            return False
        
        all_dataframes = []
        merged_file_path = os.path.join(base_folder, f"Merged_All_Surveys_{date_str}.xlsx")
        
        try:
            # Walk through all folders and find Excel files
            for root, dirs, files in os.walk(base_folder):
                for file in files:
                    if file.endswith('.xlsx') and not file.startswith('Merged_'):
                        file_path = os.path.join(root, file)
                        print(f"📄 Reading: {file_path}")
                        try:
                            df = pd.read_excel(file_path)
                            # Add survey name as a column
                            survey_folder = os.path.basename(root)
                            df['Survey_Name'] = survey_folder
                            all_dataframes.append(df)
                        except Exception as e:
                            print(f"⚠️ Could not read {file}: {e}")
            
            if not all_dataframes:
                print("❌ No Excel files found to merge")
                return False
            
            # Merge all dataframes
            merged_df = pd.concat(all_dataframes, ignore_index=True)
            
            # Save merged file
            merged_df.to_excel(merged_file_path, index=False)
            print(f"✅ Merged file saved: {merged_file_path}")
            print(f"📊 Total rows: {len(merged_df)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error merging files: {e}")
            return False
    
    def run(self):
        """Main execution method"""
        print("🚀 Starting LeadTech Automation...")
        
        try:
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login():
                return
            
            # Navigate to Response
            if not self.navigate_to_response():
                return
            
            # Click View Projects for CLIENT0011
            if not self.click_view_projects("CLIENT0011"):
                return
            
            # Process each project in the list
            for serial_number in self.project_serial_numbers:
                success = self.process_single_project(serial_number)
                if not success:
                    print(f"⚠️ Failed to process S.No: {serial_number}, continuing...")
                    # Try to navigate back to client page
                    try:
                        self.driver.get("https://dev.leadtech.in/survey/responses")
                        time.sleep(5)
                        self.click_view_projects("CLIENT0011")
                    except:
                        pass
            
            # Merge all Excel files
            self.merge_all_excel_files()
            
            print("\n✅ Automation completed successfully!")
            
        except Exception as e:
            print(f"❌ Automation failed: {e}")
        finally:
            # Keep browser open for inspection
            print("\n⏳ Browser will close in 30 seconds...")
            time.sleep(30)
            self.driver.quit()
    
    def get_project_list_from_table(self):
        """Helper method to get all project serial numbers from the table"""
        print("📋 Getting list of all projects...")
        try:
            rows = self.driver.find_elements(By.CSS_SELECTOR, "#surveyTableBody tr")
            project_list = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells and len(cells) > 0:
                    serial = int(cells[0].text.strip())
                    project_list.append(serial)
            print(f"✅ Found {len(project_list)} projects")
            return project_list
        except Exception as e:
            print(f"❌ Failed to get project list: {e}")
            return []

    def get_survey_serial_numbers(self):
        """Get all survey serial numbers from the current page"""
        print("📋 Getting survey serial numbers...")
        try:
            table_body = self.wait.until(
                EC.presence_of_element_located((By.ID, "surveyTableBody"))
            )
            rows = table_body.find_elements(By.XPATH, "./tr")
            survey_list = []
            for i, row in enumerate(rows, 1):
                try:
                    serial = row.find_element(By.XPATH, "./td[1]").text.strip()
                    if serial.isdigit():
                        survey_list.append(int(serial))
                except:
                    pass
            print(f"✅ Found {len(survey_list)} surveys")
            return survey_list
        except Exception as e:
            print(f"❌ Failed to get survey list: {e}")
            return []

if __name__ == "__main__":
    automation = LeadTechAutomation()
    
    # Option: Use all projects from the table
    # automation.project_serial_numbers = automation.get_project_list_from_table()
    
    # Or manually specify which projects to process
    # automation.project_serial_numbers = [1, 2, 3, 4, 5]  # Uncomment and modify as needed
    
    automation.run()