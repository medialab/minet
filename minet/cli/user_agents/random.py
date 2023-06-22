from minet.user_agents import get_random_useragent

def action(cli_args):
    pct, ua = get_random_useragent()
    print("Random user agent ({:.2f}%) :".format(pct))
    print(ua)
