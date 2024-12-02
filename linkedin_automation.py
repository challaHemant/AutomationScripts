from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
import pickle
import os

# Set up Chrome driver
chrome_driver_path = "/opt/homebrew/bin/chromedriver"
service = Service(chrome_driver_path)
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Optional: Start browser maximized
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
driver = webdriver.Chrome(service=service, options=chrome_options)

# Login details
linkedin_email = "LINKEDIN_EMAIL"
linkedin_password = "LINKEDIN_PASSWORD"

# Path to resume
resume_path = "RESUME_PATH"

# Predefined responses for specific questions
predefined_answers = {
    "python": "3",  # Experience with Python
    "pandas": "1",  # Experience with Pandas
    "aws": "3",     # Experience with AWS
    "numpy": "2",    # Experience with Numpy
    "data manipulation": "3",  # Experience with Data Manipulation
    "data engineering": "1",   # Experience with Data Engineering
    "location": "Yes",  # Willing to work in Bangalore
    "ctc": "10 LPA",   # Expected CTC
    "joining": "Immediate"  # Joining availability
}

# Function to log in with cookies if available
def login_with_cookies():
    driver.get("https://www.linkedin.com/login")  # Ensure we're on the correct domain
    if os.path.exists("linkedin_cookies.pkl"):
        with open("linkedin_cookies.pkl", "rb") as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                if "domain" not in cookie:
                    cookie["domain"] = ".linkedin.com"  # Set domain to linkedin.com
                driver.add_cookie(cookie)
            return True
    return False

# Save cookies after login
def save_cookies():
    cookies = driver.get_cookies()
    with open("linkedin_cookies.pkl", "wb") as cookiesfile:
        pickle.dump(cookies, cookiesfile)

# Login to LinkedIn
def login():
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(linkedin_email)
    driver.find_element(By.ID, "password").send_keys(linkedin_password)
    
    # Find and click 'Remember Me' checkbox if available
    try:
        remember_me_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox' and @id='remember-me']")
        if not remember_me_checkbox.is_selected():
            remember_me_checkbox.click()
    except Exception as e:
        print("Remember Me checkbox not found or no action required.")
    
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    print("Successfully logged into LinkedIn!")

# Try logging in with cookies, otherwise, perform a fresh login
try:
    if not login_with_cookies():
        login()  # Perform fresh login if no cookies exist
    time.sleep(5)  # Wait for login to complete
    save_cookies()  # Save cookies after login
except Exception as e:
    print(f"Error during LinkedIn login: {e}")
    traceback.print_exc()
    driver.quit()
    exit()

# Navigate to job postings
try:
    driver.get("https://www.linkedin.com/jobs/search/?f_TP=1")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
except Exception as e:
    print(f"Error navigating to job postings: {e}")
    traceback.print_exc()
    driver.quit()
    exit()

# Locate job elements
print("Waiting for job titles to load...")
try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.XPATH, ".//div[contains(@class, 'job-card-container')]//a[contains(@class, 'job-card-list__title')]"))
    )
    jobs = driver.find_elements(By.XPATH, ".//div[contains(@class, 'job-card-container')]//a[contains(@class, 'job-card-list__title')]")
    print(f"Found {len(jobs)} job(s).")
except Exception as e:
    print(f"Error waiting for job titles: {e}")
    traceback.print_exc()
    driver.quit()
    exit()

# Function to handle Easy Apply and additional questions
def easy_apply_for_job_with_resume(driver, job_link, resume_path):
    try:
        driver.get(job_link)
        
        # Scroll to the Easy Apply button to make sure it's in view
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Give some time for the page to settle

        # Wait for and click the Easy Apply button using CSS selector
        try:
            easy_apply_button = WebDriverWait(driver, 90).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jobs-apply-button.artdeco-button--primary"))
            )
            print("Clicking Easy Apply button...")
            easy_apply_button.click()
        except Exception:
            print("Easy Apply button not clickable in time.")
            return  # Skip this job if button is not found
        
        # Handle additional questions
        try:
            questions = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'jobs-easy-apply-form__question')]"))
            )
            print(f"Found {len(questions)} additional questions.")
            for question in questions:
                question_text = question.text.lower()
                print(f"Question: {question_text}")

                # Handle dropdown questions
                try:
                    dropdown = question.find_element(By.XPATH, ".//select")
                    if dropdown.is_displayed():
                        print("Handling dropdown question...")
                        dropdown.click()
                        options = dropdown.find_elements(By.TAG_NAME, "option")
                        for option in options:
                            if option.text.strip().lower() in predefined_answers.values():
                                option.click()
                                break
                except Exception:
                    pass  # No dropdown found, continue to text input questions

                # Handle text input questions
                try:
                    text_input = question.find_element(By.XPATH, ".//input")
                    if text_input.is_displayed():
                        print("Handling text input question...")
                        for key, answer in predefined_answers.items():
                            if key.lower() in question_text:
                                text_input.send_keys(answer)
                                break
                except Exception:
                    pass  # No text input found, continue to next question

        except Exception as e:
            print("No additional questions found or error handling questions:", e)

        # Upload resume
        try:
            file_input = driver.find_element(By.XPATH, "//input[@type='file']")
            if file_input.is_displayed():
                print("Uploading resume...")
                file_input.send_keys(resume_path)
        except Exception as e:
            print(f"No file input found: {e}")

        # Review and submit application
        try:
            review_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Review')]"))
            )
            review_button.click()
            print("Clicked 'Review' button.")

            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit application')]"))
            )
            submit_button.click()
            print("Successfully applied for the job!")
        except Exception as e:
            print(f"Error during review/submit process: {e}")
    except Exception as e:
        print(f"Error applying to job: {e}")
        traceback.print_exc()
        driver.save_screenshot(f"error_screenshot_{int(time.time())}.png")  # Save screenshot for debugging

# Apply for jobs
for i in range(len(jobs)):
    try:
        # Refresh the list of jobs to avoid stale element issues
        jobs = driver.find_elements(By.XPATH, ".//div[contains(@class, 'job-card-container')]//a[contains(@class, 'job-card-list__title')]")
        if i >= len(jobs):
            continue
        job = jobs[i]
        title = job.text
        link = job.get_attribute("href")
        print(f"Applying for {title} ({link})...")
        easy_apply_for_job_with_resume(driver, link, resume_path)
    except Exception as e:
        print(f"Error processing job at index {i}: {e}")
        traceback.print_exc()

# Quit driver
driver.quit()
