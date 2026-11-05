from urllib.parse import urlsplit, urlunsplit


def _is_tracking(pair: str) -> bool:
    name = pair.partition("=")[0].lower()
    return name == "fbclid" or name.startswith("utm_")


def clean_url(url: str) -> str:
    """Return the link without fbclid and utm_* query parameters.

    Names match ignoring case. Other parameters stay as written and in order,
    no empty '?' is left behind, and the fragment is kept. No network call.
    """
    parts = urlsplit(url)
    kept = [pair for pair in parts.query.split("&") if pair and not _is_tracking(pair)]
    return urlunsplit(parts._replace(query="&".join(kept)))
