from os.path import dirname, join

import minet.user_agents.data as data
from minet.web import request
from minet.exceptions import UserAgentsUpdateError

def useragentsme():
    endpoint = "https://www.useragents.me/api"
    response = request(endpoint, spoof_ua=False)
    results = response.json()
    return [
        (row["pct"], row["ua"])
        for row in results.get("data", [])
        if not "Trident" in row["ua"]
    ]


def cum_sum_generator(probs):
    d = 0
    for p in probs:
        d = d + p
        yield d


def update(transient=False):
    try:
        data.USER_AGENTS = useragentsme()
        output_path = join(dirname(__file__), "data.py")

        probs = [pct for (pct, _) in data.USER_AGENTS]
        data.USER_AGENTS_SHARE_CDF = [p for p in cum_sum_generator(probs)]

        if transient:
            return

        with open(output_path, "w") as f:
            f.write("USER_AGENTS = [\n")
            for pct, ua in data.USER_AGENTS:
                eua = ua.replace('"', r"\"")
                f.write('\t(%f, "%s"),\n' % (pct, eua))
            f.write("]\n\n")

            f.write("USER_AGENTS_SHARE_CDF = [\n")
            for pct in data.USER_AGENTS_SHARE_CDF:
                f.write("\t%f,\n" % pct)
            f.write("]\n\n")

    except Exception as reason:
        raise UserAgentsUpdateError("Unable to update the list of user agents", reason=reason)
