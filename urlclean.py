from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def _is_tracking(name: str) -> bool:
    lowered = name.lower()
    return lowered == "fbclid" or lowered.startswith("utm_")


def clean_url(url: str) -> str:
    """Return the link without fbclid and utm_* query parameters.

    Names match ignoring case. Other parameters keep their order, no empty
    '?' is left behind, and the fragment is kept. No network call is made.
    """
    parts = urlsplit(url)
    kept = [
        (name, value)
        for name, value in parse_qsl(parts.query, keep_blank_values=True)
        if not _is_tracking(name)
    ]
    return urlunsplit(parts._replace(query=urlencode(kept)))
