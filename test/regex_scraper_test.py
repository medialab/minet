# =============================================================================
# Minet Regex Scrapers Unit Tests
# =============================================================================
from minet.scrape import (
    extract_encodings_from_xml,
    extract_canonical_link,
    extract_javascript_relocation,
    extract_meta_refresh,
)
from minet.scrape.regex import extract_href, JAVASCRIPT_LOCATION_RE

HTML_CANONICAL_TESTS = b"""
    <head>
        <link rel="canonical" href="https://www.corriere.it/" />
        <meta property="vr:canonical" content="https://www.corriere.it/"/>
        <meta property="og:image" content="https://images2.corriereobjects.it/includes_grafici/HP/images/corrieredellaseraFB.jpg"/>
        <meta property="og:title" content="Corriere della Sera: news e ultime notizie oggi da Italia e Mondo"/>
        <meta property="og:description" content="Notizie di cronaca, politica, economia e sport con foto e video. Meteo, salute, viaggi, musica e giochi online. Annunci di lavoro, immobiliari e auto."/>
        <meta property="og:url" content="https://www.corriere.it/"/>
        <meta charset="iso-8859-1"><meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="apple-itunes-app" content="app-id=326634016, affiliate-data=, app-argument=">
        <link rel="icon" href="https://components2.corriereobjects.it/rcs_cor_corriere-layout/v2/assets/img/ext/favicon/favicon.ico?v1" sizes="16x16 24x24 32x32 48x48 64x64 128x128" type="image/vnd.microsoft.icon">
    </head>
"""

CANONICAL_LINK_TESTS = [
    (
        b'<link href="https://www.dailymail.co.uk/home/index.html" rel="canonical" />',
        "https://www.dailymail.co.uk/home/index.html",
    ),
    (
        b'<link rel="canonical" href="https://www.lefigaro.fr/">',
        "https://www.lefigaro.fr/",
    ),
    (
        b'<link data-rh="true" rel="canonical" href="https://www.lesechos.fr/industrie-services/conso-distribution/passe-sanitaire-le-gouvernement-desserre-letau-sur-les-centres-commerciaux-1343524"/>',
        "https://www.lesechos.fr/industrie-services/conso-distribution/passe-sanitaire-le-gouvernement-desserre-letau-sur-les-centres-commerciaux-1343524",
    ),
    (
        b'<link rel="canonical" href="https://www.tokyo-sports.co.jp"/>',
        "https://www.tokyo-sports.co.jp",
    ),
    (
        b'<link rel="canonical" href="https://www.chinadaily.com.cn" />',
        "https://www.chinadaily.com.cn",
    ),
    (
        b'<link rel="canonical" href="https://www.repubblica.it/esteri/2021/09/03/news/afghanistana_murtaza_messi_maglia_di_plastica_bimbo_kabul-316373369/">',
        "https://www.repubblica.it/esteri/2021/09/03/news/afghanistana_murtaza_messi_maglia_di_plastica_bimbo_kabul-316373369/",
    ),
    (
        b'<link HREF="https://www.elmundo.es/" rel="canonical" data-ue-c="href" data-ue-u="canonical"/>',
        "https://www.elmundo.es/",
    ),
    (
        b'<link rel="canonical" href="https://www.theglobeandmail.com/">',
        "https://www.theglobeandmail.com/",
    ),
    (
        b'<link rel="canonical" href="https://www.spiegel.de/wirtschaft/soziales/inflation-angst-vor-steigenden-preisen-bei-friedrich-merz-und-co-kolumne-a-2aff6230-8965-4b0f-954d-984cc57fb35c">',
        "https://www.spiegel.de/wirtschaft/soziales/inflation-angst-vor-steigenden-preisen-bei-friedrich-merz-und-co-kolumne-a-2aff6230-8965-4b0f-954d-984cc57fb35c",
    ),
    (b'<link rel="canonical" href="https://elpais.com"/>', "https://elpais.com"),
    (b'<link rel="canonical" href="https://www.nrc.nl/">', "https://www.nrc.nl/"),
    (
        b'<link data-n-head="ssr" rel="canonical" href="https://www.nzz.ch">',
        "https://www.nzz.ch",
    ),
    (
        b'<link rel="canonical" href="https://www.haaretz.com/"/>',
        "https://www.haaretz.com/",
    ),
    (
        b'<link rel="canonical" href="https://timesofindia.indiatimes.com/world/south-asia/hunted-by-the-men-they-jailed-afghanistans-women-judges-seek-escape/articleshow/85896129.cms"/>',
        "https://timesofindia.indiatimes.com/world/south-asia/hunted-by-the-men-they-jailed-afghanistans-women-judges-seek-escape/articleshow/85896129.cms",
    ),
    (
        b'<link rel="canonical" href="https://www.corriere.it/" />',
        "https://www.corriere.it/",
    ),
    (
        b'<link rel="canonical" href="https://www.thesun.co.uk/news/16044176/buckingham-palace-furious-queens-secret-death/"/>',
        "https://www.thesun.co.uk/news/16044176/buckingham-palace-furious-queens-secret-death/",
    ),
    (
        b'<link rel="canonical" href="https://www.theguardian.com/us-news/commentisfree/2016/feb/16/thomas-piketty-bernie-sanders-us-election-2016" />',
        "https://www.theguardian.com/us-news/commentisfree/2016/feb/16/thomas-piketty-bernie-sanders-us-election-2016",
    ),
    (
        b'<link rel="canonical" "https://www.theguardian.com/us-news/commentisfree/2016/feb/16/thomas-piketty-bernie-sanders-us-election-2016" />',
        None,
    ),
    (b'<link rel="canonical" href=', None),
    (b'<link rel="canonical" href=""', None),
]

JAVASCRIPT_LOCATION = rb"""
    <head>
        <title>https://twitter.com/i/web/status/1155764949777620992</title>
    </head>
    <script>
        window.opener = null;
        location = "https:\/\/twitter.com\/i\/web\/status\/0"
        window.location = "https:\/\/twitter.com\/i\/web\/status\/1"
        location.replace("https:\/\/twitter.com\/i\/web\/status\/2");location = "https:\/\/twitter.com\/i\/web\/status\/3"
        window.location.replace("https:\/\/twitter.com\/i\/web\/status\/4")
        window.location='https:\/\/twitter.com\/i\/web\/status\/5'
        window.location      ="https:\/\/twitter.com\/i\/web\/status\/6"
    </script>
"""

META_REFRESH = rb"""
    <head>
        <noscript>
            <META http-equiv="refresh" content="0;URL=https://twitter.com/i/web/status/1155764949777620992">
        </noscrMETA_REFRESHipt>
        <title>https://twitter.com/i/web/status/1155764949777620992</title>
    </head>
    <script>
        window.opener = null;
        location.replace("https:\/\/twitter.com\/i\/web\/status\/1155764949777620992")
    </script>
"""


class RegexTestScraper(object):
    def test_extract_encodings_from_xml(self):
        html = b"""
            <?xml version="1.0" encoding="UTF-16"?>
            <meta charset="UTF-8">
            <meta charset="utf8">
        """

        encodings = extract_encodings_from_xml(html)

        assert encodings == {"utf-16": 1, "utf-8": 2}

    def test_extract_href(self):
        for html, result in CANONICAL_LINK_TESTS:
            assert extract_href(html) == result

    def test_extract_canonical_link(self):
        canonical_link = extract_canonical_link(HTML_CANONICAL_TESTS)
        assert canonical_link == "https://www.corriere.it/"

    def test_extract_javascript_relocation(self):
        locations = JAVASCRIPT_LOCATION_RE.findall(JAVASCRIPT_LOCATION)

        r = set(int(m.decode().rsplit("/", 1)[-1]) for m in locations)

        assert r == set(range(7))

        location = extract_javascript_relocation(JAVASCRIPT_LOCATION)

        assert location == "https://twitter.com/i/web/status/0"

        location = extract_javascript_relocation(META_REFRESH)

        assert location == "https://twitter.com/i/web/status/1155764949777620992"

        location = extract_javascript_relocation(b"NOTHING")

        assert location is None

    def test_find_meta_refresh(self):
        meta_refresh = extract_meta_refresh(META_REFRESH)

        assert meta_refresh == (
            0,
            "https://twitter.com/i/web/status/1155764949777620992",
        )
