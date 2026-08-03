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


def test_slash_l_route_serves_homepage_without_error(driver, base_url, helpers):
    """Regression guard for a quirk found this session: /l is not a real route
    but silently serves homepage content instead of a 404. Locks in current
    behavior so any future change (e.g. a real 404 page) shows as a visible diff."""
    driver.get(f'{base_url}/l')
    helpers['wait_ready'](driver)
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/l rendered no visible body text'
    lowered = body.lower()
    error_markers = ['404', 'not found', 'internal server error', '500 ']
    assert not any(marker in lowered for marker in error_markers), (
        f'/l rendered an error-page marker: {body[:200]!r}'
    )
