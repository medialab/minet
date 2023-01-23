from minet.web import resolve
from minet.exceptions import RedirectError

URLS = [
    # Direct hit
    "https://www.lemonde.fr/",
    # Regular redirect
    "http://bit.ly/2KkpxiW",
    # Self loop
    "https://demo.cyotek.com/features/redirectlooptest.php",
    "https://bit.ly/2gnvlgb",
    # Meta refresh & UA nonsense
    "http://bit.ly/2YupNmj",
    "http://www.google.com/url?q=http%3A%2F%2Fwww.violenciadomestica.org.uy%2F&sa=D&sntz=1&usg=AFQjCNH5HZgs1Y1GcT6N1SuaiiYqw_rZtQ",
    # 'https://www.google.com/url?q=https://www.facebook.com/Contaniunamenos/&sa=D&ust=1603455678482000&usg=AFQjCNFSANkezX4k8Fk4sY6xg30u6CHO2Q',
    # Invalid URL
    "http://www.outremersbeyou.com/talent-de-la-semaine-la-designer-comorienne-aisha-wadaane-je-suis-fiere-de-mes-origines/",
    # Refresh header
    "http://la-grange.net/2015/03/26/refresh/",
    # GET & UA nonsense
    "https://ebay.us/BUkuxU",
    # Incorrect refresh header
    "http://ow.ly/csT350v7mRc",
    # Utf-8 location header
    "http://ow.ly/2awz50v1JkO",
    "http://xfru.it/v2uFaC",
    # IP Host redirect
    "https://bit.ly/2ANzJNW",
    # Inference
    "https://test.com?url=http%3A%2F%2Flemonde.fr%3Fnext%3Dhttp%253A%252F%252Ftarget.fr",
    "http://lemonde.fr?url=http%3A%2F%2Flemonde.fr",
    "https://www.ohaime-passion.com/fil-info/11291-soutien-total-aux-supporters-interpellees.html",
    # AMP
    "https://amp.theguardian.com/us-news/commentisfree/2016/feb/16/thomas-piketty-bernie-sanders-us-election-2016",
]


for url in URLS:
    print()
    try:
        stack = resolve(
            url, follow_meta_refresh=True, infer_redirection=True, canonicalize=True
        )
    except RedirectError as error:
        print(type(error), error)
        continue

    for item in stack:
        print(item)
