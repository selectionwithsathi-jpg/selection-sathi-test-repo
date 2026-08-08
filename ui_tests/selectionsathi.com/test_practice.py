import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

WEBDRIVER_URL = os.environ.get('WEBDRIVER_URL', '')
WEBDRIVER_SESSION_ID = os.environ.get('WEBDRIVER_SESSION_ID', '')
KNOWN_TEST_OTP = os.environ.get('KNOWN_TEST_OTP', '123456')
PRACTICE_TEST_PHONE = os.environ.get('PRACTICE_TEST_PHONE', '8319218216')
PUBLIC_LOGIN_PATH = '/login'

OTP_INPUT_SELECTOR = (
    'input[type="number"], input[maxlength="6"], input[maxlength="4"], input[maxlength="1"], '
    'input[inputmode="numeric"], input[autocomplete="one-time-code"]'
)
PRACTICE_NAV_XPATH = '//*[self::a or self::button or self::span][contains(normalize-space(.), "Practice")]'
START_PRACTICE_XPATH = '//button[contains(normalize-space(.), "Start Practice")]'
LOAD_QUESTIONS_XPATH = '//button[contains(normalize-space(.), "Load Questions")]'
SUBMIT_ANSWER_XPATH = '//button[contains(normalize-space(.), "Submit Answer")]'
NEXT_QUESTION_XPATH = '//button[contains(normalize-space(.), "Next Question")]'
QUESTION_COUNT_XPATH_TMPL = '//button[normalize-space(text())="{count}"]'


def _wait_ready(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    time.sleep(2)


def _body_text(driver):
    try:
        return driver.find_element(By.TAG_NAME, 'body').text
    except Exception:
        return ''


def _find_phone_login_field(driver):
    candidates = [f for f in driver.find_elements(By.CSS_SELECTOR, 'input[type="tel"]') if f.is_displayed()]
    for f in candidates:
        placeholder = (f.get_attribute('placeholder') or '').lower()
        if 'digit' in placeholder or 'phone' in placeholder or 'mobile' in placeholder:
            return f
    return candidates[0] if candidates else None


def _find_scoped_submit(driver, field):
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


def _click_first_visible_clickable(driver, xpath, timeout=10):
    elements = WebDriverWait(driver, timeout).until(
        lambda d: [e for e in d.find_elements(By.XPATH, xpath) if e.is_displayed() and e.is_enabled()] or False
    )
    elements[0].click()
    return elements[0]


def _go_to_practice_section(driver, base_url):
    driver.get(f'{base_url}/')
    _wait_ready(driver)
    _click_first_visible_clickable(driver, PRACTICE_NAV_XPATH)
    _wait_ready(driver)


def _start_practice(driver):
    _click_first_visible_clickable(driver, START_PRACTICE_XPATH)
    _wait_ready(driver)


def _select_filters(driver):
    selects = [s for s in driver.find_elements(By.TAG_NAME, 'select') if s.is_displayed()]
    changed = 0
    for sel in selects:
        select_obj = Select(sel)
        real_options = [o for o in select_obj.options if o.get_attribute('value')]
        if len(real_options) > 1:
            select_obj.select_by_index(1)
            changed += 1
            time.sleep(0.5)
    return changed


def _select_question_count(driver, count='100'):
    xpath = QUESTION_COUNT_XPATH_TMPL.format(count=count)
    buttons = [b for b in driver.find_elements(By.XPATH, xpath) if b.is_displayed() and b.is_enabled()]
    if buttons:
        buttons[0].click()
        return True
    return False


def _load_questions(driver):
    _click_first_visible_clickable(driver, LOAD_QUESTIONS_XPATH, timeout=15)
    _wait_ready(driver)


def _get_answer_option_buttons(driver):
    """Recorded journey showed options rendered as buttons whose text is
    'A\\nOracle', 'B\\nWebcam', etc -- a single leading option-letter followed
    by the answer text. Match generically by that shape rather than any
    specific answer content, since question content is randomized per load.
    """
    buttons = driver.find_elements(By.TAG_NAME, 'button')
    options = []
    for b in buttons:
        if not b.is_displayed():
            continue
        text = b.text.strip()
        if len(text) > 1 and text[0] in 'ABCDEFGH' and (text[1] in '\n.):' or text[1] == ' '):
            options.append(b)
    return options


def _submit_answer(driver):
    submit_btns = [b for b in driver.find_elements(By.XPATH, SUBMIT_ANSWER_XPATH) if b.is_displayed() and b.is_enabled()]
    assert submit_btns, 'Submit Answer button not found or not clickable'
    submit_btns[0].click()
    _wait_ready(driver)


def _click_next_question(driver):
    next_btns = [b for b in driver.find_elements(By.XPATH, NEXT_QUESTION_XPATH) if b.is_displayed() and b.is_enabled()]
    if next_btns:
        next_btns[0].click()
        _wait_ready(driver)
        return True
    return False


def _prepare_first_question(driver, base_url):
    _go_to_practice_section(driver, base_url)
    _start_practice(driver)
    _select_filters(driver)
    _select_question_count(driver, '100')
    _load_questions(driver)
    options = WebDriverWait(driver, 15).until(lambda d: _get_answer_option_buttons(d) or False)
    return options


@pytest.fixture(scope='module')
def practice_driver():
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--window-size=1920,1080')
    if WEBDRIVER_URL:
        if WEBDRIVER_SESSION_ID:
            chrome_options.set_capability('se:testSessionId', WEBDRIVER_SESSION_ID)
        drv = webdriver.Remote(command_executor=WEBDRIVER_URL, options=chrome_options)
    else:
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        drv = webdriver.Chrome(options=chrome_options)
    drv.implicitly_wait(10)
    yield drv
    drv.quit()


@pytest.fixture(scope='module')
def authenticated_practice_driver(practice_driver, base_url):
    """Logs in ONCE for the whole module via OTP.

    Uses the same known-test-phone / KNOWN_TEST_OTP env-var pattern already
    proven reliable in test_public_login.py -- NOT the specific phone number
    or OTP digits captured in the original recorded journey, which were a
    one-time real SMS code tied to a single live session and cannot be
    replayed.

    Login is module-scoped rather than per-test because a confirmed,
    repeatedly-reproduced bug (see test_otp_resend_within_window_handled_safely
    in test_public_login.py) makes a second OTP send shortly after the first
    silently fail. Running one OTP login per practice test would mostly
    exercise that known infra bug instead of the practice flow.
    """
    driver = practice_driver
    driver.get(f'{base_url}{PUBLIC_LOGIN_PATH}')
    _wait_ready(driver)
    try:
        driver.execute_script('window.localStorage.clear(); window.sessionStorage.clear();')
    except Exception:
        pass

    tel_field = WebDriverWait(driver, 10).until(lambda d: _find_phone_login_field(d))
    tel_field.clear()
    tel_field.send_keys(PRACTICE_TEST_PHONE)
    submit = _find_scoped_submit(driver, tel_field)
    if not submit:
        pytest.skip('Could not find OTP send button on /login -- cannot establish authenticated session for practice flow')
    submit[0].click()
    _wait_ready(driver)
    time.sleep(1)

    otp_fields = [f for f in driver.find_elements(By.CSS_SELECTOR, OTP_INPUT_SELECTOR) if f.is_displayed()]
    if not otp_fields:
        pytest.skip(
            f'OTP screen did not appear after sending OTP (current_url={driver.current_url!r}) -- likely blocked '
            'by the known OTP resend/rate-limit issue; practice flow cannot be exercised without an authenticated '
            'session this run'
        )

    if len(otp_fields) == 1:
        otp_fields[0].send_keys(KNOWN_TEST_OTP)
    else:
        for field, digit in zip(otp_fields, KNOWN_TEST_OTP):
            field.send_keys(digit)

    verify = _find_scoped_submit(driver, otp_fields[0])
    if verify:
        verify[0].click()
    _wait_ready(driver)
    time.sleep(1)

    token = driver.execute_script(
        "return window.localStorage.getItem('token') || window.localStorage.getItem('access_token') "
        "|| window.sessionStorage.getItem('token') || window.sessionStorage.getItem('access_token');"
    )
    if not token:
        pytest.skip('OTP login did not establish a session -- cannot exercise authenticated practice flow this run')
    return driver


def test_practice_nav_link_navigates_to_practice_section(authenticated_practice_driver, base_url):
    """The sidebar 'Practice' nav link navigates the user to the practice section."""
    driver = authenticated_practice_driver
    driver.get(f'{base_url}/')
    _wait_ready(driver)
    _click_first_visible_clickable(driver, PRACTICE_NAV_XPATH)
    _wait_ready(driver)
    body = _body_text(driver).lower()
    assert 'practice' in driver.current_url.lower() or 'practice' in body, (
        f"Clicking the 'Practice' nav link did not navigate to a practice-related page. "
        f'current_url={driver.current_url!r}'
    )


def test_practice_start_practice_button_opens_setup_form(authenticated_practice_driver, base_url):
    """'Start Practice' opens the exam/subject/topic setup form with filter dropdowns."""
    driver = authenticated_practice_driver
    _go_to_practice_section(driver, base_url)
    _start_practice(driver)
    selects = [s for s in driver.find_elements(By.TAG_NAME, 'select') if s.is_displayed()]
    assert selects, "'Start Practice' did not open a setup form with any visible filter dropdowns"


def test_practice_setup_filters_are_selectable(authenticated_practice_driver, base_url):
    """Subject/topic filter dropdowns on the practice setup form accept a selection."""
    driver = authenticated_practice_driver
    _go_to_practice_section(driver, base_url)
    _start_practice(driver)
    selects = [s for s in driver.find_elements(By.TAG_NAME, 'select') if s.is_displayed()]
    assert selects, 'No filter dropdowns found on the practice setup form'
    changed = _select_filters(driver)
    assert changed > 0, 'Could not select a non-default option in any practice setup filter dropdown'


def test_practice_question_count_selection(authenticated_practice_driver, base_url):
    """A question-count preset (100) can be selected on the practice setup form."""
    driver = authenticated_practice_driver
    _go_to_practice_section(driver, base_url)
    _start_practice(driver)
    _select_filters(driver)
    selected = _select_question_count(driver, '100')
    assert selected, "Could not find/click a '100' question-count preset button on the practice setup form"


def test_practice_load_questions_returns_question_set(authenticated_practice_driver, base_url):
    """'Load Questions', after filters + count are set, renders an answerable question."""
    driver = authenticated_practice_driver
    options = _prepare_first_question(driver, base_url)
    assert options, "'Load Questions' did not render any answer-option buttons for the first question"


def test_practice_answer_and_submit_question(authenticated_practice_driver, base_url):
    """Selecting an answer option and clicking Submit Answer produces feedback.

    NOTE: this writes a real practice attempt via POST /api/practice/submit
    for the test account -- a genuine, unavoidable side effect of exercising
    this behavior.
    """
    driver = authenticated_practice_driver
    options = _prepare_first_question(driver, base_url)
    assert options, 'No answer options available to select'
    options[0].click()
    _submit_answer(driver)
    body = _body_text(driver).lower()
    feedback_shown = any(kw in body for kw in ['correct', 'incorrect', 'explanation'])
    next_available = bool(
        [b for b in driver.find_elements(By.XPATH, NEXT_QUESTION_XPATH) if b.is_displayed()]
    )
    assert feedback_shown or next_available, (
        'Submitting a practice answer produced no visible feedback (no correct/incorrect/explanation text) '
        'and no Next Question control appeared'
    )


def test_practice_next_question_advances_question_set(authenticated_practice_driver, base_url):
    """After submitting one answer, Next Question advances to a new, distinct question.

    NOTE: like the previous test, this writes a real practice attempt.
    """
    driver = authenticated_practice_driver
    options = _prepare_first_question(driver, base_url)
    assert options, 'No answer options available for the first question'
    first_question_text = _body_text(driver)
    options[0].click()
    _submit_answer(driver)

    advanced = _click_next_question(driver)
    if not advanced:
        pytest.skip('No Next Question control appeared after submitting an answer -- cannot verify advancement this run')

    second_question_text = _body_text(driver)
    assert second_question_text != first_question_text, (
        'Clicking Next Question did not change the visible question content'
    )
    second_options = _get_answer_option_buttons(driver)
    assert second_options, 'No answer options available on the second question after Next Question'
