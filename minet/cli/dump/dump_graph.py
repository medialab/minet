import casanova
import json

from minet.cli.cast import CSVRowCaster
from minet.cli.constants import DEFAULT_CRAWLER_CAST

def prepare_columns(cli_args, headers):
    columns = headers.select(["id", "parent"])
    columns += headers.select(cli_args.select) if cli_args.select else []
    columns += headers.select(cli_args.label) if cli_args.label else []
    return dict((headers.nth(c), c) for c in columns)

def prepare_attributes(fields, row, fieldnames, caster):
    crow = caster.cast_row(fieldnames, row)
    for (k, v) in fields.items():
        if k != "id" and k != "parent":
            yield (fieldnames[v], crow[v])

def action(cli_args):
    jobs = casanova.reader(cli_args.input)

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

    fieldnames = jobs.fieldnames
    fields = prepare_columns(cli_args, jobs.headers)
    caster = CSVRowCaster(DEFAULT_CRAWLER_CAST, jobs.fieldnames)

    for row in jobs:
        row = caster.cast_row(row)

        id = row[fields["id"]]
        parent = row[fields["parent"]]

        label = row[fields[cli_args.label]] if cli_args.label else id

        attributes = {
            "size": 20,
            "label": label
        }

        attributes.update(prepare_attributes(fields, row, fieldnames, caster))

        node = {
            "key": id,
            "attributes": attributes,
        }

        graph["nodes"].append(node)

        if not parent: continue

        edge = {
            "source": parent,
            "target": id
        }

        graph["edges"].append(edge)

    json.dump(graph, cli_args.output, indent=2, ensure_ascii=False)
