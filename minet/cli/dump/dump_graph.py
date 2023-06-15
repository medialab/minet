import casanova
import json
from os.path import isfile

from minet.crawl.queue import CrawlerQueue
from minet.crawl.types import CrawlJob

from minet.cli.exceptions import FatalError

def action(cli_args):
    print(cli_args)
    jobs = casanova.reader(cli_args.file)
    graph = {
        "attributes": {
            "name": "Crawl result"
        },
        "options": {
            "allowSelfLoops": True,
            "multi": False,
            "type": "directed"
        },
        "nodes": [],
        "edges": []
    }

    h = jobs.headers
    for row in jobs:
        id = row[h.id]
        parent = row[h.parent]
        url = row[h.url]
        resolved_url = row[h.resolved_url]
        degree = int(row[h.degree])
        body_size = row[h.body_size]
        relevant = row[h.relevant]
        matches = row[h.matches]


        node = {
            "key": id,
            "attributes": {
                "label": url,
                "url": url,
                "resolved_url": resolved_url,
                "body_size": body_size,
                "relevant": relevant,
                "matches": matches,
                "size": degree,
            }
        }

        edge = {
            "source": parent,
            "target": id
        }


        graph["nodes"].append(node)
        if edge.get("source") and edge.get("target"):
            graph["edges"].append(edge)

    print(json.dumps(graph, indent=2))
