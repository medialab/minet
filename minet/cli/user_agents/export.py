import casanova

from minet.user_agents.data import USER_AGENTS


def action(cli_args):
    writer = casanova.writer(cli_args.output, fieldnames=["user_agent", "percent"])

    for pct, ua in USER_AGENTS:
        writer.writerow([ua, pct])
