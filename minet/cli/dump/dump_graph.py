import casanova
import json

def action(cli_args):
    print(cli_args)
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

    h = jobs.headers
    id_idx = h.id
    parent_idx = h.parent

    for row in jobs:
        id = row[id_idx]
        parent = row[parent_idx]
        node = {
            "key": id,
            "attributes": {
                # Ajouter ici les attributs
                # issues des colonnes CSV
                # sélectionnées par l'utilisateur
            }
        }

        graph["nodes"].append(node)

        if not parent: continue

        edge = {
            "source": parent,
            "target": id
        }

        graph["edges"].append(edge)

    json.dump(graph, cli_args.output, indent=2, ensure_ascii=False)
