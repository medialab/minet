from typing import Tuple, List

import random
from os.path import join, dirname

import minet.user_agents.data as data
from minet.exceptions import UserAgentsUpdateError


def cum_sum_generator(probs):
    d = 0
    for p in probs:
        d = d + p
        yield d


def update_user_agents(transient: bool = False) -> None:
    from minet.web import request

    def download_useragentsme_data() -> List[Tuple[float, str]]:
        response = request("https://www.useragents.me/api")
        results = response.json()
        return [
            (row["pct"], row["ua"])
            for row in results.get("data", [])
            if not "Trident" in row["ua"]  # Filtering out windows shenanigans etc.
        ]

    try:
        data.USER_AGENTS = download_useragentsme_data()

        probs = [pct for (pct, _) in data.USER_AGENTS]
        data.USER_AGENTS_SHARE_CDF = [p for p in cum_sum_generator(probs)]

        if transient:
            return

        with open(join(dirname(__file__), "data.py"), "w") as f:
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
        raise UserAgentsUpdateError(
            "Unable to update the list of user agents", reason=reason
        )


def get_random_user_agent() -> str:
    return random.choices(
        data.USER_AGENTS, cum_weights=data.USER_AGENTS_SHARE_CDF, k=1
    )[0][1]
