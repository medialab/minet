import casanova
import json

DEFAULT_CRAWLER_CAST = {
    "id": str,
    "parent": str,
    "spider": str,
    "depth": int,
    "url": str,
    "resolved_url": str,
    "error": str,
    "status": int,
    "degree": int,
    "body_size": int,
    "relevant": bool,
    "matches": int,
}


class CSVRowCaster(object):
    def __init__(self, rules, headers) -> None:
        self.rules = rules
        self.headers = headers

    def cast_row(self, row, fieldnames=None):
        if not fieldnames:
            fieldnames = self.headers
        return [self.try_cast(fieldnames[i], row[i]) for i in range(len(row))]

    def try_cast(self, field, value):
        dt = self.rules.get(field)
        if not dt or not value:
            return value
        if isinstance(value, dt):
            return value
        try:
            return dt(value)
        except Exception:
            return value


def prepare_columns(cli_args, headers):
    columns = headers.select(["id", "parent", "degree"])
    columns += headers.select(cli_args.select) if cli_args.select else []
    columns += headers.select(cli_args.label) if cli_args.label else []
    return dict((headers.nth(c), c) for c in columns)


def prepare_attributes(fields, row, fieldnames, caster):
    casted_row = caster.cast_row(fieldnames, row)
    for k, v in fields.items():
        if k != "id" and k != "parent" and k != "degree":
            yield (fieldnames[v], casted_row[v])


def action(cli_args):
    jobs = casanova.reader(cli_args.input)

    graph = {
        "attributes": {"name": "Crawl result"},
        "options": {"allowSelfLoops": True, "multi": False, "type": "directed"},
        "nodes": [],
        "edges": [],
    }

    fieldnames = jobs.fieldnames
    fields = prepare_columns(cli_args, jobs.headers)
    caster = CSVRowCaster(DEFAULT_CRAWLER_CAST, jobs.fieldnames)

    for row in jobs:
        row = caster.cast_row(row)

        job_id = row[fields["id"]]
        parent = row[fields["parent"]]
        degree = row[fields["degree"]]

        label = row[fields[cli_args.label]] if cli_args.label else job_id

        attributes = {"size": degree if degree > 0 else 1, "label": label}

        attributes.update(prepare_attributes(fields, row, fieldnames, caster))

        node = {
            "key": job_id,
            "attributes": attributes,
        }

        graph["nodes"].append(node)

        if not parent:
            continue

        edge = {"source": parent, "target": job_id}

        graph["edges"].append(edge)

    json.dump(graph, cli_args.output, indent=2, ensure_ascii=False)
