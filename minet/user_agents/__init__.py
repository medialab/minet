import json
import urllib3
import codecs
from os.path import dirname, join

import minet.user_agents.data as data

def download(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)

    try:
        data = response.data
    finally:
        response.close()

    return data.decode("utf-8")

def useragentsme():
    endpoint = "https://www.useragents.me/api"
    response = download(endpoint)
    results = json.loads(response)
    for row in results.get("data", []):
        yield row["ua"]

def update(transient=False):
    try:
        agents = useragentsme()
        output_path = join(dirname(__file__), "data.py")

        data.USER_AGENTS = [a for a in agents if not "Trident" in a]

        if transient:
            return

        with codecs.open(output_path, "w", encoding="utf-8") as f:
            f.write("# coding: utf-8\n\n")
            f.write("USER_AGENTS = [\n")
            for ua in data.USER_AGENTS:
                eua = ua.replace('"', r'\"')
                f.write("\t\"%s\",\n" % eua)
            f.write("]\n\n")
            f.write("LAST_USED_AGENT = 0\n")
    except:
        raise TypeError("Unable to get new useragents")

def get_useragent(new=False):
    if new:
        size = len(data.USER_AGENTS)
        data.LAST_USED_AGENT = (data.LAST_USED_AGENT + 1 ) % size
    return data.USER_AGENTS[data.LAST_USED_AGENT]

