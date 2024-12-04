from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the Brave browser
service = Service('J:/Programming thngs/autologinportal/chromeserver.exe')
brave_options = Options()
brave_options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
brave_options.add_argument("--headless")  # Run in background
brave_options.add_argument("--disable-gpu")
brave_options.add_argument("--no-sandbox")

# Initialize the driver
driver = webdriver.Chrome(service=service, options=brave_options)

# Define the URLs to be opened
urls = [
    "http:192.168.50.1/login?&username=csalva&password=a6ja"
]

# Function to wait for page load
def wait_for_page_load():
    while driver.execute_script("return document.readyState;") != "complete":
        time.sleep(0.5)

# Function to check login status and refresh if needed
def check_login():
    try:
        # Wait up to 10 seconds to locate the element indicating login success
        login_message = WebDriverWait(driver, 0.3).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div/form/div/input"))
        )
        print("Login successful:", login_message.text)
        return True  # Login successful
    except Exception:
        print("Login check failed: Element not found. Refreshing...")
        driver.refresh()  # Refresh the page if login check fails
        time.sleep(0.1)  # Small delay to avoid excessive refreshes
        return False  # Login failed

# Iterate over the list of URLs
for url in urls:
    driver.get(url)
    wait_for_page_load()  # Wait for the page to load
    while not check_login():  # Continue refreshing until login is successful
        pass

# Close the browser once all URLs are processed
driver.quit()
