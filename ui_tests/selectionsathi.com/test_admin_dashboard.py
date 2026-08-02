def test_admin_dashboard_loads_after_login(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin')
    helpers['wait_ready'](driver)
    assert '/admin/login' not in driver.current_url, 'Authenticated /admin request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin page rendered empty body after authentication'


def test_dashboard_page_loads(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/dashboard')
    helpers['wait_ready'](driver)
    assert '/admin/login' not in driver.current_url, 'Authenticated /dashboard request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/dashboard page rendered empty body after authentication'


def test_admin_requires_auth_redirects_unauthenticated(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin did not redirect to a login page; ended at {current}'
    )
