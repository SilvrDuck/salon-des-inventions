import threading
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path

PROJ_DIR = Path(__file__).resolve().parent.parent.parent.parent

browser = None

def close_extra_tabs():
    global browser
    try:
        original_tab = browser.window_handles[0]
        for handle in browser.window_handles[1:]:
            browser.switch_to.window(handle)
            browser.close()
        browser.switch_to.window(original_tab)
        print("Extra tabs closed.")
    except Exception as e:
        print("Error while closing extra tabs:", e)

def accept_cookies():
    global browser
    try:
        wait = WebDriverWait(browser, 15)
        accept_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@aria-label='Accept the use of cookies and other data for the purposes described']"
        )))
        accept_button.click()
        print("Cookies accepted.")
    except Exception as e:
        print("No 'Accept All' button found or another issue occurred:", e)

def enable_loop():
    global browser
    from selenium.common.exceptions import (
        StaleElementReferenceException,
        NoSuchElementException,
        TimeoutException,
    )
    try:
        wait = WebDriverWait(browser, 15)
        loop_button_xpath = "//button[@aria-label='Loop playlist']"

        for attempt in range(5):
            try:
                loop_button = wait.until(EC.element_to_be_clickable((
                    By.XPATH, loop_button_xpath
                )))
                loop_button.click()
                print("Loop enabled via loop button.")
                break
            except (StaleElementReferenceException, NoSuchElementException) as e:
                print(f"Attempt {attempt + 1}: Element not found or stale. Retrying...")
                time.sleep(1)
        else:
            print("Failed to enable loop after multiple attempts.")
    except TimeoutException:
        print("Loop button not found within the timeout period.")
    except Exception as e:
        print("Could not enable loop due to an unexpected error:", e)
        import traceback
        traceback.print_exc()

def play(video_ids):
    global browser

    ublock_path = PROJ_DIR / "crx/ublock.crx"
    sponsorblock_path = PROJ_DIR / "crx/sponsorblock.crx"
    print(ublock_path)
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_extension(ublock_path)
    chrome_options.add_extension(sponsorblock_path)

    browser = webdriver.Chrome(options=chrome_options)

    close_extra_tabs()

    playlist_url = "https://www.youtube.com/watch_videos?video_ids=" + ",".join(video_ids)
    browser.get(playlist_url)

    accept_cookies()
    enable_loop()

def stop():
    global browser
    if browser:
        browser.quit()
        browser = None

if __name__ == "__main__":
    video_ids = ["dQw4w9WgXcQ", "kJQP7kiw5Fk"]
    play_thread = threading.Thread(target=play, args=(video_ids,))
    play_thread.start()

    time.sleep(600)
    stop()
    play_thread.join()
