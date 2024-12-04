import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Get the current directory where the script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# Correct the path to your chromedriver (make sure it's in the same folder as the script)
service = Service(os.path.join(script_dir, 'chromedriver.exe'))

brave_options = Options()
brave_options.binary_location = r"C:\Users\Justine\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_options.add_argument("--headless")  # Run in background
brave_options.add_argument("--disable-gpu")
brave_options.add_argument("--no-sandbox")

# Ask user for username and password
username = input("Enter your username: ")
password = input("Enter your password: ")

# Construct the URL using the user input
url = f"http://vnhs.portal/login?&username={username}&password={password}"

# Function to wait for page load
def wait_for_page_load(driver):
    while driver.execute_script("return document.readyState;") != "complete":
        time.sleep(1)

# Function to check login status and refresh if needed
def check_login(driver, url):
    try:
        driver.get(url)
        wait_for_page_load(driver)

        # Check if the "no more sessions allowed" message exists
        no_more_sessions_xpath = "/html/body/section/div/div[2]/div"
        try:
            no_sessions = driver.find_element(By.XPATH, no_more_sessions_xpath)
            print(f"Account at {url}: No more sessions allowed.")
            driver.refresh()  # Refresh page if this message appears
            time.sleep(0.1)
            return False  # Login failed, retry after refresh
        except:
            pass

        # Check if the login success message exists
        login_xpath = "/html/body/div/div/form/div/input"
        login_message = WebDriverWait(driver, 0.1).until(
            EC.presence_of_element_located((By.XPATH, login_xpath))
        )
        print(f"Account at {url}: Login successful.")
        return True  # Login successful
    except Exception as e:
        print(f"Account at {url}: Error during login check: {e}")
        return False

# Function to process each account and stop once one is successful
def process_account(url):
    # Initialize the driver
    driver = webdriver.Chrome(service=service, options=brave_options)
    
    login_success = False
    while not login_success:
        login_success = check_login(driver, url)
    
    # Wait 5 seconds before closing after successful login
    time.sleep(5)
    driver.quit()
    return url  # Return the URL of the successfully logged-in account

# Run the user-provided URL in parallel using ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=1) as executor:  # Single task since only 1 account
    futures = [executor.submit(process_account, url)]
    
    # Wait for the first successful login
    for future in as_completed(futures):
        url = future.result()
        print(f"Login successful for {url}, stopping other checks.")
        # Cancel the remaining tasks after the first successful login
        for future in futures:
            future.cancel()
        break  # Exit the loop after the first successful login
