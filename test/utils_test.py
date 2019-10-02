# =============================================================================
# Minet Utils Unit Tests
# =============================================================================
from minet.utils import (
    parse_http_refresh,
    find_meta_refresh
)

HTTP_REFRESH_TESTS = [
    ('0;url=https://www.youtube.com/watch?v=sTJ1XwGDcA4', (0, 'https://www.youtube.com/watch?v=sTJ1XwGDcA4')),
    ('0;url=https://www.youtube.com/watch?v=sTJ1XwGDcA4   ', (0, 'https://www.youtube.com/watch?v=sTJ1XwGDcA4')),
    ('   0;URL=https://www.youtube.com/watch?v=sTJ1XwGDcA4', (0, 'https://www.youtube.com/watch?v=sTJ1XwGDcA4')),
    ('test;url=https://www.youtube.com/watch?v=sTJ1XwGDcA4', None),
    ('0;/www.youtube.com/watch?v=sTJ1XwGDcA4', None)
]

META_REFRESH = rb'''
    <head>
        <noscript>
            <META http-equiv="refresh" content="0;URL=https://twitter.com/i/web/status/1155764949777620992">
        </noscript>
        <title>https://twitter.com/i/web/status/1155764949777620992</title>
    </head>
    <script>
        window.opener = null;
        location.replace("https:\/\/twitter.com\/i\/web\/status\/1155764949777620992")
    </script>
'''


class TestUtils(object):
    def test_parse_http_refresh(self):
        for header_value, result in HTTP_REFRESH_TESTS:
            assert parse_http_refresh(header_value) == result

    def test_find_meta_refresh(self):
        meta_refresh = find_meta_refresh(META_REFRESH)

        assert meta_refresh == (0, 'https://twitter.com/i/web/status/1155764949777620992')
