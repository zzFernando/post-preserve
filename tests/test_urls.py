from postpreserve.urls import normalize_instagram_url


def test_normalize_instagram_post_url():
    normalized = normalize_instagram_url("https://www.instagram.com/p/EXAMPLE/?utm_source=x")
    assert normalized.normalized == "https://www.instagram.com/p/EXAMPLE/"
    assert normalized.shortcode == "EXAMPLE"

