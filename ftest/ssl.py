from minet.utils import create_pool, raw_resolve

SSL_ISSUES = [
    'https://lemde.fr/2zmunsV',
    'https://buff.ly/2Nnaevg',
    'http://www.plateforme1418.com/',
    'https://www.silverday-normandie.fr',
    'http://swll.to/rJjizGY',
    'http://ow.ly/zpnt30mdb9N'
]

http = create_pool(insecure=True)

for url in SSL_ISSUES:
    print(url)
    err, stack, response = raw_resolve(http, url, return_response=True)
    print('Error', err, type(err))

    for r in stack:
        print(r)

    print()
