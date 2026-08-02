def test_admin_terminal_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/terminal')
    helpers['wait_ready'](driver)
    assert '/login' not in driver.current_url, 'Authenticated /admin/terminal request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin/terminal rendered empty body after authentication'


def test_admin_terminal_requires_auth(driver, base_url, helpers):
    """High-value check: /admin/terminal is linked to a previously-confirmed critical
    dev-login-backdoor finding where a zero-credential JWT reached /api/code/execute's
    auth layer. Verifying this UI entry point enforces auth is a direct regression guard
    against that class of bug.
    """
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/terminal')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/terminal did not redirect to a login page; ended at {current}'
    )
