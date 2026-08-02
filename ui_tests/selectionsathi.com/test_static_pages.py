from selenium.webdriver.common.by import By


def test_terms_page_loads(driver, base_url, helpers):
    driver.get(f'{base_url}/terms')
    helpers['wait_ready'](driver)
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/terms rendered no visible body text'


def test_privacy_page_loads(driver, base_url, helpers):
    driver.get(f'{base_url}/privacy')
    helpers['wait_ready'](driver)
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/privacy rendered no visible body text'


def test_home_page_loads(driver, base_url, helpers):
    driver.get(f'{base_url}/')
    helpers['wait_ready'](driver)
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, 'home page rendered no visible body text'
    nav_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="login"]')
    assert nav_links, 'No login-related link found on home page nav'
