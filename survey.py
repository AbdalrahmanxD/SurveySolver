import threading
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
# Chrome options for incognito mode
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_experimental_option("detach", True)  # Keeps browser open

# Store browser instances
drivers = []
FINALURL = "https://eduservices.edu.gov.qa/WebParts/Survey/#/"

# Get screen size dynamically
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Quarter screen size
WINDOW_WIDTH = SCREEN_WIDTH // 2
WINDOW_HEIGHT = SCREEN_HEIGHT // 2

# **Perfect Window Positions (2x2 Grid)**
POSITIONS = [
    (0, 0),  # Top-left
    (WINDOW_WIDTH, 0),  # Top-right
    (0, WINDOW_HEIGHT),  # Bottom-left
    (WINDOW_WIDTH, WINDOW_HEIGHT)  # Bottom-right
]

# Read numbers from a text file
with open("numbers.txt", "r") as file:
    numbers = [line.strip() for line in file.readlines()]
used_numbers = set()  # Track used numbers


# Function to open a browser, wait for the login button, scroll, and snap it
def open_browser(index):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(FINALURL)

    try:

        # **Scroll down by 1000 pixels smoothly**
        driver.execute_script("window.scrollBy(0, 1000);")
        print(f"🔽 Scrolled down in browser {index}")

        # Step 1: Get a unique number
        number = get_unique_number(index)

        # Step 2: Snap the window to position
        snap_window(index)

        # Step 3: Type the ID in the input field using Selenium
        type_id_in_field(driver, number)
        driver.execute_script("window.scrollBy(0, 150);")

        # Step 4: Select the CAPTCHA field to make it easier for the user
        select_captcha_field(driver)

        # Step 5: Inject JavaScript to detect login button click
        inject_javascript(driver)

        # Step 6: **Wait for button click before proceeding**
        wait_for_button_click(driver)
        while True:


            # Step 7: **Check for alert after button click**
            monitor_alert_and_update_number(driver, index)
     
            # Step 8: **Click `b.ng-binding` and handle new tab**
            handle_ng_binding_click(driver,index)

    except Exception as e:
        print(f"⛛ Error in browser {index}: {str(e)}")
        driver.close()  # Close the window in case of error

    drivers.append(driver)


# Function to get a unique number from the list
def get_unique_number(index):
    global used_numbers
    for i in range(index, len(numbers)):  # Start from the index position
        if numbers[i] not in used_numbers:
            used_numbers.add(numbers[i])
            return numbers[i]
    return None  # If all numbers are used


# Function to type the number from the text file into the field using Selenium
def type_id_in_field(driver, number):
    try:
        # Wait for the input field to type the number
        input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='QID']")))
        input_field.clear()
        input_field.send_keys(number)
        print(f"⌨️ Typed '{number}' in browser")
    except Exception as e:
        print(f"⛛ Failed to type ID: {e}")


# Function to select the CAPTCHA field for the user
def select_captcha_field(driver):
    try:
        captcha_field = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='TbCaptcha']")))
        captcha_field.click()
        print("🖱️ CAPTCHA field selected.")
    except Exception as e:
        print(f"⛛ Failed to select CAPTCHA field: {e}")


# Function to snap the browser window to the specified position
def snap_window(index):
    time.sleep(1)
    window = pyautogui.getWindowsWithTitle("Chrome")[index]  # Get the browser window
    if window:
        window.moveTo(POSITIONS[index][0], POSITIONS[index][1])
        window.resizeTo(WINDOW_WIDTH, WINDOW_HEIGHT)
        print(f"🖥️ Window snapped to position {POSITIONS[index]}")


# Function to inject JavaScript to detect login button click
def inject_javascript(driver):
    script = """
    var loginButton = document.querySelector("button[ng-click='ViewModel.LoadSurveysByQID();']");
    if (loginButton) {
        loginButton.addEventListener('click', function() {
            window.seleniumButtonClicked = true;
        });
    }
    """
    driver.execute_script(script)


# Function to wait for the login button click
def wait_for_button_click(driver):
    print("⏳ Waiting for login button click...")
    while True:
        button_clicked = driver.execute_script("return window.seleniumButtonClicked === true;")
        if button_clicked:
            print("✅ Login button clicked!")
            return
        time.sleep(0.5)


# Function to check for the specific alert and change the ID number if found
def monitor_alert_and_update_number(driver, index):
    while True:
        try:
            alert_element = driver.find_element(By.XPATH, "//div[contains(@ng-if, 'ViewModel.Administrations.length == 0') and contains(@class, 'alert')]")

            if alert_element:
                print(f"⚠️ Alert detected in browser {index}! Changing the ID number...")

                # Get a new number
                number = get_unique_number(index)
                if number:
                    input_field = driver.find_element(By.XPATH, "//*[@id='QID']")
                    input_field.clear()
                    input_field.send_keys(number)
                    print(f"🔢 New number inserted in browser {index}: {number}")

                    # Re-click the login button to restart the process
                    login_button = driver.find_element(By.CSS_SELECTOR, "button[ng-click='ViewModel.LoadSurveysByQID();']")
                    login_button.click()
                    print(f"🔄 Retrying with new ID {number}")
                    return  # Stop further attempts since a new ID was used

        except Exception:
            pass  # Ignore errors and retry

  

# **Function to click `b.ng-binding`, switch to the new tab, and proceed**
def handle_ng_binding_click(driver,index):
    try:
        binding_element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//b[@class='ng-binding']")))
        if binding_element:
            binding_element.click()
            print("✅ Clicked `b.ng-binding` element.")

            # **Switch to the new tab if it opens**
            time.sleep(1)  # Small delay for the tab to open
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[1])  # Switch to the new tab
                print("🔄 Switched to the new tab.")

            # **Click `//a[@class='ss-default-language']`**
            lang_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='ss-default-language']")))
            lang_button.click()
            print("✅ Clicked language selection button.")
            paths = ["//*[@id='qs24225721']/div[2]/div/div[2]/div/div/table/tbody",
                     "//*[@id='qs24225722']/div[2]/div/div[2]/div/div/table/tbody",
                     "//*[@id='qs24225724']/div[2]/div/div[2]/div/div/table/tbody",
                     "//*[@id='qs24225732']/div/div/div[2]/div/div/table/tbody",
                     "//*[@id='qs24225729']/div/div/div[2]/div/div/table/tbody",
                     "//*[@id='qs24225733']/div/div/div[2]/div/div/table/tbody",
                     "//*[@id='qs24225726']/div/div/div[2]/div/div/table/tbody"
                     ]
            # **Click `//*[@id='cmdGo']`**
            go_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='cmdGo']")))
            go_button.click()
            for path in paths:
                click_table_random_td(driver,path,index)
                go_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='cmdGo']")))
                go_button.click()
                print("✅ Did the",  paths.index(path),"th page")


            random_xpaths = ["//ul[.//*[@id='o24225727177400070']]","//div[contains(@class, 'ss-question-inner')][.//*[@id='o24225723177400054']]"]
            for path in random_xpaths:
                click_random_radio_button(driver,path,index)

            go_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='cmdGo']")))
            go_button.click()
            print("✅ Done")
            # Close the current tab and go back to the original tab
            WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/div[3]/div/div/div/div/div/div[2]/div/div[1]/span/strong/span")))
            driver.close()
            print("🔴 Closed the current tab.")
            driver.switch_to.window(driver.window_handles[0])  # Switch back to the original tab

            # Get a new unused number from the list
            new_number = get_unique_number(len(drivers))  # Ensure that the number is not used by any other window
            if new_number:
                print(f"🔢 New number for next iteration: {new_number}")

                # Type the new number in the input field
                input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='QID']")))
                input_field.clear()  # Clear the old number
                input_field.send_keys(new_number)  # Type the new number
                print(f"⌨️ Typed new number '{new_number}' in the input field.")
     # Call the process again to continue the workflow
                login_button = driver.find_element(By.CSS_SELECTOR, "button[ng-click='ViewModel.LoadSurveysByQID();']")
                login_button.click()
                return  # Recursive call to continue with the new number
    except Exception as e:
        print(f"⛔ Failed to complete the process: {e}")


def click_random_radio_button(driver, xpath, seed=None):
    # Set a unique seed based on the thread index (or any unique value)
    if seed is not None:
        random.seed(seed)

    # Locate the parent ul element
    ul_element = driver.find_element(By.XPATH, xpath)

    # Find all the <label> elements inside the <ul>
    label_elements = ul_element.find_elements(By.TAG_NAME, "label")

    while True:
        # Select a random <label> element
        random_label = random.choice(label_elements)

        # Find the radio input field inside the selected <label>
        radio_input = random_label.find_element(By.XPATH, ".//input[@type='radio']")

        # Check if the radio input's id is 'o24225727177400057'
        if radio_input.get_attribute('id') != 'o24225727177400057' or radio_input.get_attribute('id') != 'o24225727177400064' or radio_input.get_attribute != 'o24225723177400054':
            # Click the radio input field if it's not the excluded one
            radio_input.click()
            break

    # Optionally, wait to see the effect (if needed)
    #time.sleep(2)
def click_table_random_td(driver,xpath,seed=None):

    try:
        if seed is not None:
            random.seed(seed)

        tbody_xpath = xpath
        rows = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, f"{tbody_xpath}/tr")))

        for row in rows:
            result = random.randrange(1, 3)



            if xpath == "//*[@id='qs24225726']/div/div/div[2]/div/div/table/tbody" or (xpath == "//*[@id='qs24225721']/div[2]/div/div[2]/div/div/table/tbody" and rows.index(row) == 15):
                result = 3


            first_td = row.find_element(By.XPATH, "./td[" + str(result) + "]")  # Get first `<td>` inside `<tr>`

            first_td.click()
            print("✅ Clicked first <td> inside <tr>.")
            time.sleep(0.5)  # Small delay between clicks

    except Exception as e:
        print(f"⛔ Error clicking table cells: {e}")




# Create and start threads for each browser
threads = []
for i in range(min(4, len(numbers))):
    thread = threading.Thread(target=open_browser, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()
