import json
import random
import re
import time
from datetime import datetime, timedelta
from threading import Timer

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from msedge.selenium_tools import Edge, EdgeOptions

browser: webdriver.Chrome = None
total_members = None
config = None
meetings = []
current_meeting = None
already_joined_ids = []
active_correlation_id = ""
hangup_thread: Timer = None
conversation_link = "https://teams.microsoft.com/_#/conversations/a"
mode = 3
uuid_regex = r"\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b"


def load_config():
    global config
    with open('config.json') as json_data_file:
        config = json.load(json_data_file)


def init_browser():
    global browser

    if "chrome_type" in config and config['chrome_type'] == "msedge":
        chrome_options = EdgeOptions()
        chrome_options.use_chromium = True

    else:
        chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--use-fake-ui-for-media-stream')
    chrome_options.add_experimental_option('prefs', {
        'credentials_enable_service': False,
        'profile.default_content_setting_values.media_stream_mic': 1,
        'profile.default_content_setting_values.media_stream_camera': 1,
        'profile.default_content_setting_values.geolocation': 1,
        'profile.default_content_setting_values.notifications': 1,
        'profile': {
            'password_manager_enabled': False
        }
    })
    chrome_options.add_argument('--no-sandbox')

    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    if 'headless' in config and config['headless']:
        chrome_options.add_argument('--headless')
        print("Enabled headless mode")

    if 'mute_audio' in config and config['mute_audio']:
        chrome_options.add_argument("--mute-audio")

    if 'chrome_type' in config:
        if config['chrome_type'] == "chromium":
            browser = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
                                       options=chrome_options)
        elif config['chrome_type'] == "msedge":
            browser = Edge(EdgeChromiumDriverManager().install(), options=chrome_options)
        else:
            browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    else:
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    # make the window a minimum width to show the meetings menu
    window_size = browser.get_window_size()
    if window_size['width'] < 1200:
        print("Resized window width")
        browser.set_window_size(1200, window_size['height'])

    if window_size['height'] < 850:
        print("Resized window height")
        browser.set_window_size(window_size['width'], 850)


def wait_until_found(sel, timeout, print_error=True):
    try:
        element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, sel))
        WebDriverWait(browser, timeout).until(element_present)

        return browser.find_element_by_css_selector(sel)
    except exceptions.TimeoutException:
        if print_error:
            print(f"Timeout waiting for element: {sel}")
        return None


def main():
    global config, current_meeting, hangup_thread

    if config["type"] == "jitsi":
        jitsi()
    elif config["type"] == "teams":
        teams()
    else:
        print("Wrong Type \n Valid: jitsi, teams")

    while current_meeting:
        time.sleep(2)

    if 'auto_leave_after_min' in config and config[ 'auto_leave_after_min' ] > 0:
        hangup_thread = Timer(config[ 'auto_leave_after_min' ] * 60, hangup)
        hangup_thread.start()


def hangup():
    global current_meeting, hangup_thread

    print("auto leave time reached. exiting...")
    exit(1)


def jitsi():
    global config, meetings, mode, conversation_link, total_members, hangup_thread, current_meeting
    current_meeting = True
    init_browser()
    browser.get(config["link_jitsi"])
    time.sleep(5)

    button = wait_until_found("path[d='M23.063 14.688h2.25c0 4.563-3.625 8.313-8 8.938v4.375h-2.625v-4.375c-4.375-.625-8-4.375-8-8.938h2.25c0 4 3.375 6.75 7.063 6.75s7.063-2.75 7.063-6.75zm-7.063 4c-2.188 0-4-1.813-4-4v-8c0-2.188 1.813-4 4-4s4 1.813 4 4v8c0 2.188-1.813 4-4 4z']", 5)
    if button is not None:
        button.click()
    else:
        print("microphone button not found")

    time.sleep(5)
    camera = wait_until_found("path[d='M22.688 14l5.313-5.313v14.625l-5.313-5.313v4.688c0 .75-.625 1.313-1.375 1.313h-16C4.563 24 4 23.437 4 22.687V9.312c0-.75.563-1.313 1.313-1.313h16c.75 0 1.375.563 1.375 1.313V14z']", 5)
    if camera is not None:
        camera.click()
    else:
        print("Camera Button not found")
    time.sleep(5)

    username = wait_until_found("input[placeholder='Bitte geben Sie hier Ihren Namen ein']", 30)
    if username is not None:
        username.send_keys(config['username'])
    else:
        print("Username input field not found")

    # find the element again to avoid StaleElementReferenceException
    username = wait_until_found("input[placeholder='Bitte geben Sie hier Ihren Namen ein']", 5)
    if username is not None:
        username.send_keys(Keys.ENTER)


def teams():
    global config, meetings, mode, conversation_link, total_members, hangup_thread, current_meeting

    current_meeting = True
    init_browser()

    browser.get(config["link_teams"])
    time.sleep(5)

    button = wait_until_found("button[data-tid='joinOnWeb']", 5)
    if button is not None:
        button.click()
    else:
        print("Join on Web button not found")

    time.sleep(5)
    camera = wait_until_found("span[title='Kamera deaktivieren']", 5)
    if camera is not None:
        camera.click()
    else:
        print("Camera Button not found")
    time.sleep(5)
    microphone = wait_until_found("span[title='Mikrofon stummschalten']", 5)
    if microphone is not None:
        microphone.click()
    else:
        print("microphone button note found")

    username = wait_until_found("input[id='username']", 30)
    if username is not None:
        username.send_keys(config['username'])
    else:
        print("Username input field not found")

    # find the element again to avoid StaleElementReferenceException
    username = wait_until_found("input[id='username']", 5)
    if username is not None:
        username.send_keys(Keys.ENTER)


if __name__ == "__main__":
    load_config()

    if 'run_at_time' in config and config['run_at_time'] != "":
        now = datetime.now()
        run_at = datetime.strptime(config['run_at_time'], "%H:%M").replace(year=now.year, month=now.month, day=now.day)

        if run_at.time() < now.time():
            run_at = datetime.strptime(config['run_at_time'], "%H:%M").replace(year=now.year, month=now.month,
                                                                               day=now.day + 1)

        start_delay = (run_at - now).total_seconds()

        print(f"Waiting until {run_at} ({int(start_delay)}s)")

        end = config["auto_leave_after_min"]
        close = run_at + timedelta(minutes=end, seconds=30)

        if 'auto_leave_after_min' in config and config[ 'auto_leave_after_min' ] != "":
            print(f"Closing at {close} ({end}m)")
        #start_delay
        time.sleep(0)

    try:
        main()
    finally:
        if browser is not None:
            browser.quit()

        if hangup_thread is not None:
            hangup_thread.cancel()
