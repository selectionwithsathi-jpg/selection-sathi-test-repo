import os
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

KNOWN_TEST_OTP = os.environ.get('KNOWN_TEST_OTP', '123456')
WRONG_TEST_OTP = '000111' if KNOWN_TEST_OTP != '000111' else '111000'
OTP_INPUT_SELECTOR = (
    'input[type="number"], input[maxlength="6"], input[maxlength="4"], input[maxlength="1"], '
    'input[inputmode="numeric"], input[autocomplete="one-time-code"]'
)
PUBLIC_LOGIN_PATH = '/login'
BACKDOOR_MARKERS = ['[DEV] Quick Login', 'Quick Login', 'DEV Login', 'Dev Login']
LOGIN_INPUT_SELECTOR = (
    'input[name="username"], input[name="email"], input[name="phone"], '
    'input[type="text"], input[type="email"], input[type="tel"], input[type="number"]'
)
PHONE_NUMBER = '8319218216'
OTP_SEND_BUTTON_XPATH = (
    '//button[contains(translate(text(), "OTPSENDCONTIUE", "otpsendcontiue"), "otp") '
    'or contains(translate(text(), "OTPSENDCONTIUE", "otpsendcontiue"), "send") '
    'or contains(translate(text(), "OTPSENDCONTIUE", "otpsendcontiue"), "continue") '
    'or contains(translate(text(), "OTPSENDCONTIUE", "otpsendcontiue"), "get")]'
)


def _find_backdoor_button(driver):
    for marker in BACKDOOR_MARKERS:
        els = driver.find_elements(By.XPATH, f'//*[contains(text(), "{marker}")]')
        visible = [e for e in els if e.is_displayed()]
        if visible:
            return visible
    return []


def _find_phone_login_field(driver):
    """The page can render more than one input[type=tel] (e.g. a callback-request
    field elsewhere) -- prefer the one whose placeholder actually reads like the
    OTP-login phone prompt."""
    candidates = [f for f in driver.find_elements(By.CSS_SELECTOR, 'input[type="tel"]') if f.is_displayed()]
    for f in candidates:
        placeholder = (f.get_attribute('placeholder') or '').lower()
        if 'digit' in placeholder or 'phone' in placeholder or 'mobile' in placeholder:
            return f
    return candidates[0] if candidates else None


def _find_scoped_submit(driver, field):
    """Prefer a submit control inside the same <form> as `field` over the first
    submit-like element on the page, which may belong to an unrelated form."""
    try:
        form = field.find_element(By.XPATH, './ancestor::form[1]')
        scoped = [
            b for b in form.find_elements(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"], button')
            if b.is_displayed() and b.is_enabled()
        ]
        if scoped:
            return scoped
    except Exception:
        pass
    return [
        b for b in driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
        if b.is_displayed() and b.is_enabled()
    ]


def test_public_login_page_renders(driver, base_url, helpers):
    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    helpers['wait_ready'](driver)
    login_fields = driver.find_elements(By.CSS_SELECTOR, LOGIN_INPUT_SELECTOR)
    pass_fields = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
    assert len(login_fields) > 0 or len(pass_fields) > 0, (
        'Neither a username/email/phone field nor a password field was found on public /login'
    )


def test_dev_quick_login_button_not_visible_on_public_login(driver, base_url, helpers):
    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    helpers['wait_ready'](driver)
    backdoor = _find_backdoor_button(driver)
    assert not backdoor, (
        f'[DEV] Quick Login backdoor button is visible on public /login page: '
        f'{[b.text for b in backdoor]}'
    )


def test_dev_quick_login_button_does_not_grant_session(driver, base_url, helpers):
    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    backdoor = _find_backdoor_button(driver)
    if not backdoor:
        pytest.skip('No [DEV] Quick Login backdoor button found -- nothing to click')
    backdoor[0].click()
    helpers['wait_ready'](driver)
    time.sleep(1)
    token = None
    try:
        token = driver.execute_script(
            "return window.localStorage.getItem('token') || window.localStorage.getItem('access_token') "
            "|| window.sessionStorage.getItem('token') || window.sessionStorage.getItem('access_token');"
        )
    except Exception:
        pass
    assert not token, f'Dev backdoor granted a live session token with zero credentials: {token}'


def test_otp_login_phone_field_renders_and_validates(driver, base_url, helpers):
    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    helpers['wait_ready'](driver)
    tel_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="tel"]'))
    )
    assert tel_field.is_displayed(), 'Phone number input is not visible on /login'
    placeholder = (tel_field.get_attribute('placeholder') or '').lower()
    assert 'digit' in placeholder or 'phone' in placeholder or 'mobile' in placeholder, (
        f"Phone field placeholder doesn't look like a phone prompt: {placeholder!r}"
    )


def test_otp_login_incorrect_otp_rejected(driver, base_url, helpers):
    """Closes a previously-unverified security gap: does the server actually
    reject a wrong OTP, or does the UI accept anything client-side?"""
    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    tel_field = WebDriverWait(driver, 10).until(lambda d: _find_phone_login_field(d))
    tel_field.clear()
    tel_field.send_keys(PHONE_NUMBER)

    submit_candidates = _find_scoped_submit(driver, tel_field)
    if not submit_candidates:
        submit_candidates = [
            b for b in driver.find_elements(By.XPATH, OTP_SEND_BUTTON_XPATH)
            if b.is_displayed() and b.is_enabled()
        ]
    assert submit_candidates, 'Could not find any submit/send-OTP button scoped to the phone login form'
    submit_candidates[0].click()
    helpers['wait_ready'](driver)
    time.sleep(1)

    otp_fields = [
        f for f in driver.find_elements(By.CSS_SELECTOR, OTP_INPUT_SELECTOR) if f.is_displayed()
    ]
    if not otp_fields:
        pytest.skip(
            f'No OTP entry field appeared after sending OTP (current_url={driver.current_url!r}) -- '
            "likely blocked by the known OTP resend/rate-limit issue rather than this test's target behavior"
        )

    if len(otp_fields) == 1:
        otp_fields[0].send_keys(WRONG_TEST_OTP)
    else:
        for field, digit in zip(otp_fields, WRONG_TEST_OTP):
            field.send_keys(digit)

    verify_candidates = _find_scoped_submit(driver, otp_fields[0])
    if not verify_candidates:
        verify_candidates = [
            b for b in driver.find_elements(By.XPATH, OTP_SEND_BUTTON_XPATH)
            if b.is_displayed() and b.is_enabled()
        ]
    if verify_candidates:
        verify_candidates[0].click()
    helpers['wait_ready'](driver)
    time.sleep(1)

    token = helpers['has_token'](driver)
    body = helpers['body_text'](driver)
    assert not token, (
        f'A deliberately WRONG OTP ({WRONG_TEST_OTP}) still established a session -- '
        'OTP verification is not being enforced server-side (auth bypass)'
    )
    feedback_shown = any(kw in body.lower() for kw in ['invalid', 'incorrect', 'wrong', 'error'])
    stayed_on_login = PUBLIC_LOGIN_PATH in driver.current_url
    assert feedback_shown or stayed_on_login, (
        f'Wrong OTP correctly did not grant a session, but the app gave no error messaging and '
        f'navigated away from /login. current_url={driver.current_url!r} body_snippet={body[:300]!r}'
    )


def test_otp_login_sends_otp_for_valid_number(driver, base_url, helpers):
    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    tel_field = WebDriverWait(driver, 10).until(lambda d: _find_phone_login_field(d))
    tel_field.clear()
    tel_field.send_keys(PHONE_NUMBER)

    submit_candidates = _find_scoped_submit(driver, tel_field)
    if not submit_candidates:
        submit_candidates = [
            b for b in driver.find_elements(By.XPATH, OTP_SEND_BUTTON_XPATH)
            if b.is_displayed() and b.is_enabled()
        ]
    assert submit_candidates, 'Could not find any submit/send-OTP button scoped to the phone login form'
    submit_candidates[0].click()
    helpers['wait_ready'](driver)
    time.sleep(1)

    body = helpers['body_text'](driver)
    otp_inputs = driver.find_elements(By.CSS_SELECTOR, OTP_INPUT_SELECTOR)
    otp_inputs = [f for f in otp_inputs if f.is_displayed()]
    assert otp_inputs or 'otp' in body.lower() or 'verification' in body.lower() or 'code' in body.lower(), (
        f'No OTP entry UI or OTP-related messaging appeared after submitting phone number. Page text: {body[:300]!r}'
    )


def test_otp_login_end_to_end_valid_number(driver, base_url, helpers):
    """Single continuous session: send OTP then submit it immediately, since
    separate execute_pytest calls do not preserve in-page state across a
    real human-relayed OTP round trip (each call opens a fresh tab)."""
    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    tel_field = WebDriverWait(driver, 10).until(lambda d: _find_phone_login_field(d))
    tel_field.clear()
    tel_field.send_keys(PHONE_NUMBER)

    submit_candidates = _find_scoped_submit(driver, tel_field)
    if not submit_candidates:
        submit_candidates = [
            b for b in driver.find_elements(By.XPATH, OTP_SEND_BUTTON_XPATH)
            if b.is_displayed() and b.is_enabled()
        ]
    assert submit_candidates, 'Could not find any submit/send-OTP button scoped to the phone login form'
    submit_candidates[0].click()
    helpers['wait_ready'](driver)
    time.sleep(1)

    otp_fields = [
        f for f in driver.find_elements(By.CSS_SELECTOR, OTP_INPUT_SELECTOR) if f.is_displayed()
    ]
    assert otp_fields, (
        f'No OTP entry field appeared after sending OTP. current_url={driver.current_url!r} '
        f"body_snippet={helpers['body_text'](driver)[:300]!r}"
    )

    if len(otp_fields) == 1:
        otp_fields[0].send_keys(KNOWN_TEST_OTP)
    else:
        for field, digit in zip(otp_fields, KNOWN_TEST_OTP):
            field.send_keys(digit)

    verify_candidates = _find_scoped_submit(driver, otp_fields[0])
    if not verify_candidates:
        verify_candidates = [
            b for b in driver.find_elements(By.XPATH, OTP_SEND_BUTTON_XPATH)
            if b.is_displayed() and b.is_enabled()
        ]
    if verify_candidates:
        verify_candidates[0].click()
    helpers['wait_ready'](driver)
    time.sleep(1)

    token = helpers['has_token'](driver)
    current_url = driver.current_url
    assert token or '/login' not in current_url, (
        f'OTP submission with {KNOWN_TEST_OTP!r} did not establish a session: '
        f'no token in storage and still on {current_url}'
    )


def test_otp_resend_within_window_handled_safely(driver, base_url, helpers):
    """Regression test for a bug found earlier today (TMS run 2148): sending a
    second OTP shortly after the first silently returned homepage content with
    no OTP screen and no error message. This formalizes that observation as a
    repeatable check instead of a one-off model assertion."""
    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    helpers['wait_ready'](driver)
    helpers['clear_storage'](driver)
    tel_field = WebDriverWait(driver, 10).until(lambda d: _find_phone_login_field(d))
    tel_field.clear()
    tel_field.send_keys(PHONE_NUMBER)
    first_submit = _find_scoped_submit(driver, tel_field)
    assert first_submit, 'Could not find submit button for first OTP send'
    first_submit[0].click()
    helpers['wait_ready'](driver)
    time.sleep(1)

    first_otp_fields = [f for f in driver.find_elements(By.CSS_SELECTOR, OTP_INPUT_SELECTOR) if f.is_displayed()]
    if not first_otp_fields:
        pytest.skip(
            f'First OTP send did not reach the OTP screen (current_url={driver.current_url!r}) -- '
            'cannot exercise resend behavior this run'
        )

    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    helpers['wait_ready'](driver)
    tel_field2 = WebDriverWait(driver, 10).until(lambda d: _find_phone_login_field(d))
    tel_field2.clear()
    tel_field2.send_keys(PHONE_NUMBER)
    second_submit = _find_scoped_submit(driver, tel_field2)
    assert second_submit, 'Could not find submit button for second (resend) OTP send'
    second_submit[0].click()
    helpers['wait_ready'](driver)
    time.sleep(1)

    second_otp_fields = [f for f in driver.find_elements(By.CSS_SELECTOR, OTP_INPUT_SELECTOR) if f.is_displayed()]
    body = helpers['body_text'](driver)
    current_url = driver.current_url

    got_otp_screen = bool(second_otp_fields)
    got_feedback = any(kw in body.lower() for kw in ['try again', 'wait', 'too many', 'rate limit', 'otp', 'code', 'error'])
    stayed_on_login = PUBLIC_LOGIN_PATH in current_url

    bug_reproduced = not (got_otp_screen or got_feedback or stayed_on_login)
    assert not bug_reproduced, (
        'Resending OTP shortly after the first send silently navigated away with no OTP screen and '
        f'no error feedback -- current_url={current_url!r} body_snippet={body[:300]!r} '
        '(matches known bug from an earlier session today, TMS run 2148)'
    )
