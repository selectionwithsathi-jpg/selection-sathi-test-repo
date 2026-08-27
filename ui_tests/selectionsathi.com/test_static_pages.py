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


def test_slash_l_route_returns_not_found_page(driver, base_url, helpers):
    """Corrected this session: crawl_site's page title for /l looked identical
    to the homepage (this SPA reuses one static <title> across all client-side
    routes), which wrongly suggested /l silently served homepage content.
    Selenium confirms the real behavior is a proper client-side 404 page.
    Locks that in as the known-good behavior."""
    driver.get(f'{base_url}/l')
    helpers['wait_ready'](driver)
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/l rendered no visible body text'
    lowered = body.lower()
    assert '404' in lowered and ('not found' in lowered or "doesn't exist" in lowered or 'does not exist' in lowered), (
        f'/l no longer renders the expected 404/not-found page -- got: {body[:200]!r}'
    )
