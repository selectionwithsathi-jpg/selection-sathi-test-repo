from selenium.webdriver.common.by import By

LOGOUT_MARKERS = ['logout', 'log out', 'sign out']


def _find_logout_control(driver):
    for marker in LOGOUT_MARKERS:
        text_els = driver.find_elements(
            By.XPATH,
            f'//*[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{marker}")]'
        )
        href_els = driver.find_elements(
            By.XPATH,
            f'//*[contains(translate(@href, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{marker}")]'
        )
        aria_els = driver.find_elements(
            By.XPATH,
            f'//*[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{marker}")]'
        )
        for kind, els in (('text', text_els), ('href', href_els), ('aria-label', aria_els)):
            visible = [e for e in els if e.is_displayed()]
            if visible:
                return visible, marker, kind
    return [], None, None


def test_admin_settings_page_loads(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/settings')
    helpers['wait_ready'](driver)
    assert '/admin/login' not in driver.current_url, 'Authenticated /admin/settings redirected to login'
    inputs = driver.find_elements(By.CSS_SELECTOR, 'input, select, textarea')
    assert len(inputs) > 0, '/admin/settings rendered with no form fields'


def test_admin_settings_requires_auth(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/settings')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/settings did not redirect to a login page; ended at {current}'
    )


def test_admin_settings_logout_control_search(driver, base_url, admin_credentials, helpers):
    """Gap closure: logout_invalidation has been genuinely UNVERIFIED across many prior
    sessions because no logout control was ever discoverable. This searches both /admin and
    /admin/settings with a broader case-insensitive text/href/aria-label selector. If found,
    logs exactly which marker/attribute-kind matched (prior sessions could not confirm this),
    clicks it, and verifies the session token is actually cleared and /admin becomes
    unauthenticated again. If still not found, skips with an explicit reason rather than
    silently passing -- absence of a failing test is not evidence logout is safe.
    """
    import pytest

    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    assert helpers['has_token'](driver), 'Setup failed: no token present after login'

    control, marker, kind = _find_logout_control(driver)
    matched_page = '/admin'
    if not control:
        driver.get(f'{base_url}/admin/settings')
        helpers['wait_ready'](driver)
        control, marker, kind = _find_logout_control(driver)
        matched_page = '/admin/settings'

    if not control:
        pytest.skip(
            'No logout control discoverable on /admin or /admin/settings via text/href/aria-label '
            'search -- logout invalidation remains UNVERIFIED, not confirmed safe'
        )

    tag_name = control[0].tag_name
    print(
        f'[logout_control_search] matched marker="{marker}" attribute-kind={kind} '
        f'tag=<{tag_name}> on page={matched_page}'
    )

    control[0].click()
    helpers['wait_ready'](driver)

    still_has_token = helpers['has_token'](driver)
    driver.get(f'{base_url}/admin')
    helpers['wait_ready'](driver)
    still_authed = '/admin/login' not in driver.current_url and '/login' not in driver.current_url

    assert not still_has_token, 'Logout control clicked but session token still present in storage'
    assert not still_authed, (
        f'Logout control clicked but /admin is still reachable without re-authentication '
        f'(ended at {driver.current_url})'
    )


def test_admin_settings_anomaly_full_layout_renders(driver, base_url, admin_credentials, helpers):
    """Gap closure: this session's crawl found /admin/settings (and 11 sibling pages)
    rendering an anomalous minimal shell (4 elements, 0 admin-nav links, 1 form/2 inputs)
    instead of the ~48-link admin layout seen in every prior session. This directly checks,
    via a real authenticated Selenium load rather than the crawler's snapshot, whether the
    full admin nav sidebar is present -- confirming whether this is a real regression or a
    crawl-timing artifact.
    """
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/settings')
    helpers['wait_ready'](driver)
    nav_links = [
        l for l in driver.find_elements(By.CSS_SELECTOR, 'a[href*="/admin/"]')
        if l.is_displayed()
    ]
    print(f'[settings_anomaly] admin nav links found: {len(nav_links)}')
    assert len(nav_links) > 10, (
        f'/admin/settings rendered only {len(nav_links)} admin nav link(s) after authenticated load '
        '-- matches the anomalous minimal-shell fingerprint seen in this session\'s crawl, not the '
        'expected ~48-link admin layout. Possible render/routing regression.'
    )
