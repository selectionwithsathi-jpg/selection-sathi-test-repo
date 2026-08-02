import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get('BASE_URL', 'https://selectionsathi.com')
WEBDRIVER_URL = os.environ.get('WEBDRIVER_URL', '')
WEBDRIVER_SESSION_ID = os.environ.get('WEBDRIVER_SESSION_ID', '')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

USER_FIELD_SELECTOR = (
    'input[name="username"], input[name="email"], input[placeholder*="username" i], '
    'input[placeholder*="email" i], input[type="text"]'
)
SUBMIT_SELECTOR = 'button[type="submit"], input[type="submit"]'


@pytest.fixture(scope='session')
def base_url():
    return BASE_URL.rstrip('/')


@pytest.fixture(scope='session')
def admin_credentials():
    return {'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD}


@pytest.fixture(scope='function')
def driver():
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--window-size=1920,1080')
    if WEBDRIVER_URL:
        if WEBDRIVER_SESSION_ID:
            chrome_options.set_capability('se:testSessionId', WEBDRIVER_SESSION_ID)
        drv = webdriver.Remote(command_executor=WEBDRIVER_URL, options=chrome_options)
    else:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        drv = webdriver.Chrome(options=chrome_options)
    drv.implicitly_wait(10)
    yield drv
    drv.quit()


def _wait_ready(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    time.sleep(2)


def _clear_storage(driver):
    try:
        driver.execute_script('window.localStorage.clear(); window.sessionStorage.clear();')
    except Exception:
        pass


def _has_token(driver):
    try:
        token = driver.execute_script(
            "return window.localStorage.getItem('token') || window.localStorage.getItem('access_token') "
            "|| window.sessionStorage.getItem('token') || window.sessionStorage.getItem('access_token');"
        )
        return bool(token)
    except Exception:
        return False


def _body_text(driver):
    try:
        return driver.find_element(By.TAG_NAME, 'body').text
    except Exception:
        return ''


def _login(driver, base_url, username, password, login_path='/admin/login'):
    driver.get(f'{base_url}{login_path}')
    _wait_ready(driver)
    user_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, USER_FIELD_SELECTOR))
    )
    pass_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    user_field.clear()
    user_field.send_keys(username)
    pass_field.clear()
    pass_field.send_keys(password)
    driver.find_element(By.CSS_SELECTOR, SUBMIT_SELECTOR).click()
    _wait_ready(driver)


@pytest.fixture
def helpers():
    return {
        'wait_ready': _wait_ready,
        'clear_storage': _clear_storage,
        'has_token': _has_token,
        'body_text': _body_text,
        'login': _login,
        'user_field_selector': USER_FIELD_SELECTOR,
        'submit_selector': SUBMIT_SELECTOR,
    }
