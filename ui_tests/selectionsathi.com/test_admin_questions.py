def test_admin_questions_page_loads_after_login(driver, base_url, admin_credentials, helpers):
    helpers['login'](driver, base_url, admin_credentials['username'], admin_credentials['password'])
    driver.get(f'{base_url}/admin/questions')
    helpers['wait_ready'](driver)
    assert '/login' not in driver.current_url, 'Authenticated /admin/questions request redirected to login'
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/admin/questions rendered empty body after authentication'


def test_admin_questions_requires_auth(driver, base_url, helpers):
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/admin/questions')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /admin/questions did not redirect to a login page; ended at {current}'
    )
