import os
import time
import pytest
import httpx
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get('BASE_URL', 'https://selectionsathi.com')
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


@pytest.fixture(scope='session')
def admin_api_token(base_url, admin_credentials):
    """Bearer token from the JSON admin-login API, independent of the browser session.

    Used only for out-of-band setup/teardown of disposable test data (e.g. deleting
    a test exam created during a UI test) so UI tests never leave orphaned records
    behind on this production site.
    """
    try:
        resp = httpx.post(
            f'{base_url}/api/auth/admin-login',
            json={'username': admin_credentials['username'], 'password': admin_credentials['password']},
            timeout=30.0,
            verify=False,
        )
        if resp.status_code != 200:
            return None
        return resp.json().get('access_token')
    except Exception:
        return None


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


def pytest_runtest_makereport(item, call):
    """On any failure, surface current URL + visible buttons/links so a bare
    AssertionError/Timeout is never the whole story in the TMS logs tab.
    """
    if call.when != 'call' or call.excinfo is None:
        return
    driver = item.funcargs.get('driver') if hasattr(item, 'funcargs') else None
    if driver is None:
        return
    try:
        url = driver.current_url
    except Exception:
        url = '<driver unavailable - session may be dead>'
    visible = []
    try:
        for el in driver.find_elements(By.CSS_SELECTOR, 'button, a')[:30]:
            if el.is_displayed():
                label = (el.text or el.get_attribute('aria-label') or '').strip()
                if label:
                    visible.append(label)
    except Exception:
        pass
    print(f'\n[FAILURE DIAGNOSTICS] test={item.name} url={url}')
    print(f'[FAILURE DIAGNOSTICS] visible buttons/links: {visible}')
