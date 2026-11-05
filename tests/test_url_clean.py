from urlclean import clean_url

REPO = "https://github.com/gyoridavid/ai_agents_az"


def test_removes_fbclid():
    assert clean_url(REPO + "?fbclid=abc123") == REPO
    assert clean_url(REPO + "?FBCLID=abc123") == REPO


def test_removes_utm_parameters():
    url = REPO + "?utm_source=x&utm_medium=y&utm_campaign=z"
    assert clean_url(url) == REPO
    assert clean_url(REPO + "?UTM_Source=x") == REPO
    assert "?" not in clean_url(url)


def test_keeps_other_parameters_in_order():
    url = "https://example.com/a?b=2&utm_source=x&a=1&fbclid=z&c=3"
    assert clean_url(url) == "https://example.com/a?b=2&a=1&c=3"
    assert clean_url(url + "#top") == "https://example.com/a?b=2&a=1&c=3#top"
    assert clean_url(REPO + "?fbclid=z#top") == REPO + "#top"


def test_with_and_without_fbclid_give_same_result():
    assert clean_url(REPO + "?fbclid=abc") == clean_url(REPO)


def test_input_is_not_changed():
    url = REPO + "?fbclid=abc&utm_source=x"
    original = url
    clean_url(url)
    assert url == original


def test_malformed_link_is_returned_unchanged():
    assert clean_url("http://[abc") == "http://[abc"
