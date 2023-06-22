import csv

from minet.user_agents.data import USER_AGENTS


def action(cli_args):
    writer = csv.DictWriter(cli_args.output, ["user_agent", "percent"])
    writer.writeheader()
    for pct, ua in USER_AGENTS:
        writer.writerow({
            "user_agent": ua,
            "percent": pct
        })
