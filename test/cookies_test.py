from minet.cookies import cookie_string_to_dict


class TestCookies:
    def test_cookie_string_to_dict(self):
        assert cookie_string_to_dict("key1=2; key2=3") == {"key1": "2", "key2": "3"}
        assert cookie_string_to_dict(
            'lat=34; g_state={"i_p":1674220462478,"i_l":1}; lang=en'
        ) == {"lat": "34", "g_state": '{"i_p":1674220462478,"i_l":1}', "lang": "en"}
