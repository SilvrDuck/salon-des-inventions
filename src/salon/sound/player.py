import threading
from pathlib import Path
from functools import wraps

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PROJ_DIR = Path(__file__).resolve().parent.parent.parent.parent

def ensure_browser(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (NoSuchWindowException, WebDriverException) as e:
            print(f"Browser exception in {func.__name__}: {e}")
            with self.lock:
                self.stop()
                self._initialize_browser()
            return func(self, *args, **kwargs)
    return wrapper

class Player:
    def __init__(self):
        self.browser = None
        self.lock = threading.RLock()

    def _initialize_browser(self):
        ublock_path = PROJ_DIR / "crx/ublock.crx"
        sponsorblock_path = PROJ_DIR / "crx/sponsorblock.crx"

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_extension(str(ublock_path))
        chrome_options.add_extension(str(sponsorblock_path))

        self.browser = webdriver.Chrome(options=chrome_options)

    def _is_browser_valid(self):
        if self.browser is None:
            return False
        try:
            self.browser.current_window_handle
            return True
        except (NoSuchWindowException, WebDriverException):
            return False

    @ensure_browser
    def _accept_cookies(self):
        try:
            wait = WebDriverWait(self.browser, 15)
            accept_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//button[@aria-label='Accept the use of cookies and other data for the purposes described']"
            )))
            accept_button.click()
            print("Cookies accepted.")
        except Exception as e:
            print("No 'Accept All' button found or another issue occurred:", e)

    @ensure_browser
    def _enable_loop(self):
        try:
            wait = WebDriverWait(self.browser, 15)
            loop_button_xpath = "//button[@aria-label='Loop playlist']"
            loop_button = wait.until(EC.element_to_be_clickable((By.XPATH, loop_button_xpath)))
            loop_button.click()
            print("Loop enabled via loop button.")
        except Exception as e:
            print("Could not enable loop:", e)

    @ensure_browser
    def _navigate_to_playlist(self, playlist_url):
        self.browser.get(playlist_url)
        print("Navigated to new playlist URL.")
        self._accept_cookies()
        self._enable_loop()

    def play(self, video_ids):
        with self.lock:
            playlist_url = "https://www.youtube.com/watch_videos?video_ids=" + ",".join(video_ids)
            if not self._is_browser_valid():
                self.stop()
                self._initialize_browser()
            threading.Thread(target=self._navigate_to_playlist, args=(playlist_url,)).start()

    def stop(self):
        with self.lock:
            if self.browser:
                self.browser.quit()
                self.browser = None
                print("Browser stopped.")
