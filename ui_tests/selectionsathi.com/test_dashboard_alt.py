def test_dashboard_alt_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/dashboard')
    helpers['wait_ready'](driver)
    assert '/login' not in driver.current_url, 'Authenticated /dashboard request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/dashboard rendered empty body after authentication'


def test_dashboard_alt_requires_auth(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/dashboard')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /dashboard did not redirect to a login page; ended at {current}'
    )


def test_dashboard_login_redirect_param_preserved(driver, base_url, helpers):
    """New this session: confirms the redirect target is preserved through the
    auth gate, not just that some /login page is reached."""
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/dashboard')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /dashboard did not redirect to a login page; ended at {current}'
    )
    assert 'dashboard' in current.lower(), (
        f'Redirected to login but the redirect target param does not reference /dashboard: {current!r}'
    )
