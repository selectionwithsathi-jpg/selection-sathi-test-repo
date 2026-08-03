def test_exams_page_requires_auth_with_redirect_param(driver, base_url, helpers):
    """First-ever test for /exams. Mirrors the /dashboard auth-gate check:
    unauthenticated access must redirect to /login with the redirect target
    preserved, not just to some generic /login page."""
    driver.get(base_url)
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    driver.get(f'{base_url}/exams')
    helpers['wait_ready'](driver)
    current = driver.current_url
    assert '/login' in current, (
        f'Unauthenticated access to /exams did not redirect to a login page; ended at {current}'
    )
    assert 'exams' in current.lower(), (
        f'Redirected to login but the redirect target param does not reference /exams: {current!r}'
    )


def test_exams_page_loads_content(driver, base_url, helpers):
    driver.get(f'{base_url}/exams')
    helpers['wait_ready'](driver)
    body = helpers['body_text'](driver)
    assert len(body.strip()) > 0, '/exams rendered no visible body text (whether login-gate or listing content)'
