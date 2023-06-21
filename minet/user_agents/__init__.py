import json
import urllib3
import codecs
import random as rd
from functools import reduce
from os.path import dirname, join

import minet.user_agents.data as data


def download(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)

    try:
        data = response.data
    finally:
        response.close()

    return data.decode("utf-8")


def useragentsme():
    endpoint = "https://www.useragents.me/api"
    response = download(endpoint)
    results = json.loads(response)
    return [
        (row["pct"], row["ua"])
        for row in results.get("data", [])
        if not "Trident" in row["ua"]
    ]


def calculate_prob(probs):
    d = 0
    for p in probs:
        d = d + p
        yield d


def update(transient=False):
    try:
        agents = useragentsme()
        output_path = join(dirname(__file__), "data.py")

        data.USER_AGENTS = [ua for (_, ua) in agents]

        probs = [pct for (pct, _) in agents]
        data.USER_AGENTS_PROB = [p for p in calculate_prob(probs)]

        if transient:
            return

        with codecs.open(output_path, "w", encoding="utf-8") as f:
            f.write("# coding: utf-8\n\n")

            f.write("USER_AGENTS = [\n")
            for ua in data.USER_AGENTS:
                eua = ua.replace('"', r"\"")
                f.write('\t"%s",\n' % eua)
            f.write("]\n\n")

            f.write("USER_AGENTS_PROB = [\n")
            for pct in data.USER_AGENTS_PROB:
                f.write("\t%f,\n" % pct)
            f.write("]\n\n")

    except:
        raise TypeError("Unable to get new useragents")


def get_useragent(random=False):
    if random:
        return rd.choices(data.USER_AGENTS, cum_weights=data.USER_AGENTS_PROB, k=1)[0]
    return data.USER_AGENTS[0]
